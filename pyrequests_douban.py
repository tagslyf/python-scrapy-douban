import json, pprint, re, requests, time
from bs4 import BeautifulSoup


def get_celebrity(url):
	print("Sending request to {}".format(url))
	celebrity = {}
	res = get_request(url)
	if res.status_code == 200:
		html = BeautifulSoup(res.content, "html.parser")
		celebrity['avatars'] = {}
		if html.find("div", {'class': "pic"}):
			for s in ["small", "medium", "large"]:
				celebrity['avatars'][s] = [dt['src'].strip() for dt in html.find("div", {'class': "pic"}).findAll("img", src=re.compile(r'{}'.format(s)))]
	return celebrity


def get_initial_release(html):
	return html.find("div", {'id': "info"}).find("span", {'property': "v:initialReleaseDate"}).string


def get_photos(html, url):
	photos = []
	if html.find("a", {"href": url}):
		print("Sending request for {} to get all photos".format(url))
		res = get_request(url)
		if res.status_code == 200:
			html = BeautifulSoup(res.content, 'html.parser')
			if html.find("div", {'class': "article"}):
				all_photos_html = html.find("div", {'class': "article"}).findAll("div", {'class': "mod"})[0]
				for li in all_photos_html.findAll("li")[:10]:
					photo = {}
					photo['url'] = li.find("a")['href']
					photo['photo'] = li.find("img")['src']
					photos.append(photo)
	return photos


def get_request(url, s=0):
	time.sleep(s)
	return requests.get(url)


def get_runtime(html):
	return html.find("div", {'id': "info"}).find("span", {'property': "v:runtime"}).string


def get_screenwriters(html):
	directors = []
	if html.find("div", {'class': "info"}):
		for d in html.find("div", {'class': "info"}).findChildren()[2].findAll("a"):
			director = {}
			director['id'] = d['href'].split('/')[2]
			director['name'] = d.string
			director['alt'] = "{}{}".format(domain, d['href'])
			director['avatars'] = get_celebrity(director['alt'])
			directors.append(director)
	return directors

def get_starring(html):
	starrings = []
	if html.find("span", {'class': "actor"}):
		for star in html.find("span", {'class': "actor"}).find("span", {'class': "attrs"}).findAll("a"):
			starring = {}
			starring['id'] = star['href'].split('/')[2]
			starring['name'] = star.string.strip()
			starring['alt'] = "{}{}".format(domain, star['href'])
			starring['avatars'] = get_celebrity(starring['alt'])
			starrings.append(starring)
	return starrings


def get_trailer(html, url):
	trailers = []
	if html.find("a", {"href": url}):
		print("Sending request for {} to get trailers".format(url))
		res = get_request(url)
		if res.status_code == 200:
			html = BeautifulSoup(res.content, 'html.parser')
			if html.find("div", {'class': "article"}):
				for d in html.find("div", {'class': "article"}).findAll("div", {'class': "mod"}):
					trailer = {}
					if "预告片" in d.find("h2").string:
						trailer['url'] = d.find("a", {'class': "pr-video"})['href']
						trailer['view_img'] = d.find("a", {'class': "pr-video"}).find("img")['src']
						trailer['duration'] = d.find("a", {'class': "pr-video"}).find("em").string
						trailer['title'] = d.find("p").find("a").string.strip()
						trailer['date'] = d.find("p", {'class': "trail-meta"}).find("span").string.strip()
						trailer['responses_url'] = d.find("p", {'class': "trail-meta"}).find("a")['href']
					trailers.append(trailer)
	return trailers


def get_types(html):
	return ", ".join([sp.string for sp in html.find("div", {"id": "info"}).findAll("span", {'property': "v:genre"})])


def manual_scrape():
	print("Sending request to {}".format(url.format(page_limit, page_start)))
	response = get_request(url.format(page_limit, page_start), 5)
	if response.status_code == 200:
		subjects = json.loads(response.text)['subjects']
		for subject in subjects:
			subject['api_return'] = {}
			print("Sending request to {}".format(public_api_url.format(subject['id'])))
			api_response = get_request(public_api_url.format(subject['id']))
			if api_response.status_code == 200:
				subject['api_return'] = api_response.json()
			subject['url_content'] = {}
			## Call Happy API to post data
			print("Sending request to {}".format(subject['url']))
			content_response = get_request(subject['url'], 5)
			if content_response.status_code == 200:
				content = BeautifulSoup(content_response.content, 'html.parser')
				subject['url_content']['screenwriters'] = get_screenwriters(content)
				subject['url_content']['starring'] = get_starring(content)
				subject['url_content']['types'] = get_types(content)
				subject['url_content']['initial_release'] = get_initial_release(content)
				subject['url_content']['runtime'] = get_runtime(content)
				subject['url_content']['trailer'] = get_trailer(content, "{}trailer".format(subject['url']))
				subject['url_content']['photos'] = get_photos(content, "{}all_photos".format(subject['url']))
			pprint.pprint(subject)


if __name__ == "__main__":
	global url, page_limit, page_start, domain, public_api_url

	domain = "https://movie.douban.com"
	public_api_url = "https://api.douban.com/v2/movie/subject/{}"
	url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit={}&page_start={}"
	page_limit = 20
	page_start = 0

	manual_scrape()