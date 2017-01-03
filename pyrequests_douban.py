import json, pprint, re, requests, time
from bs4 import BeautifulSoup


def get_actors(html):
	# dito ka na
	html.find("span", {"class": "actor"}).find("span", {"class": "attrs"}).findAll("a")
	return True

def get_directors(html):
	directors = []
	for d in html.find("div", {"id": "info"}).findChildren()[0].findAll("a"):
		director = {}
		director['id'] = d['href'].split('/')[2]
		director['name'] = d.string
		director['alt'] = "{}{}".format(domain, d['href'])
		d_res = requests.get(director['alt'])
		if d_res.status_code == 200:
			d_html = BeautifulSoup(d_res.content, 'html.parser')

			director['avatars'] = {}
			for s in ['small', 'medium', 'large']:
				director['avatars'][s] = [dt['src'].strip() for dt in d_html.find('div', {'class': 'pic'}).findAll('img', src=re.compile(r'{}'.format(s)))]

		directors.append(director)
	return directors


def get_images(html):
	return html.find('div', {'id': 'mainpic'}).find('img')['src']


def get_origtitle_year(html):
	return html.find("h1", "").findChildren()[0].string, html.find("h1", "").findChildren()[1].string[1:-1]

def get_screenwriters(html):
	directors = []
	for d in html.find("div", {"id": "info"}).findChildren()[2].findAll("a"):
		director = {}
		director['id'] = d['href'].split('/')[2]
		director['name'] = d.string
		director['alt'] = "{}{}".format(domain, d['href'])
		d_res = requests.get(director['alt'])
		if d_res.status_code == 200:
			d_html = BeautifulSoup(d_res.content, 'html.parser')

			director['avatars'] = {}
			for s in ['small', 'medium', 'large']:
				director['avatars'][s] = [dt['src'].strip() for dt in d_html.find('div', {'class': 'pic'}).findAll('img', src=re.compile(r'{}'.format(s)))]

		directors.append(director)
	return directors


def manual_scrape():
	print("Sending request to {}".format(url.format(page_limit, page_start)))
	response = requests.get(url.format(page_limit, page_start))

	if response.status_code == 200:

		subjects = json.loads(response.text)['subjects']

		for subject in subjects:
			subject['url_content'] = {}

			## Call Happy API to post data
			print("Sending request to {}".format(subject['url']))
			content_response = requests.get(subject['url'])
			if content_response.status_code == 200:
				content = BeautifulSoup(content_response.content, 'html.parser')

				subject['url_content']['original_title'], subject['url_content']['year'] = get_origtitle_year(content)
				subject['url_content']['images'] = get_images(content)
				subject['url_content']['directors'] = get_directors(content)
				subject['url_content']['screenwriters'] = get_screenwriters(content)

			pprint.pprint(subject)


if __name__ == "__main__":
	global url, page_limit, page_start, domain

	domain = "https://movie.douban.com"

	url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit={}&page_start={}"
	page_limit = 20
	page_start = 0
	
	manual_scrape()