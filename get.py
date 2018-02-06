#!/usr/bin/python

import urllib2
import re
import csv

URL_PREFIX = "https://developers.whatismybrowser.com"
MAIN_URL = URL_PREFIX + "/useragents/explore/hardware_type_specific/"
IGNORE = ["Computer", "Mobile", "Phone"]

columns = ["category" ,"ua", "major_name" , "medium_name"]

def get_ua_data(ua_link):
	ua_data = []
	medium_name = "UNKNOWN_MEDIUM"
	major_name = "UNKNOWN_MAJOR"

	ua_page = urllib2.urlopen(ua_link).read()
	UA_SIMPLE_MEDIUM_REGEX = '<div class="simple-medium">(.+?)</div>'
	UA_SIMPLE_MAJOR_REGEX = '<div class="simple-major">(.+?)</div>'
	medium_name_match = re.search(UA_SIMPLE_MEDIUM_REGEX, ua_page)
	major_name_match = re.search(UA_SIMPLE_MAJOR_REGEX, ua_page)

	if medium_name_match:
		medium_name = medium_name_match.groups()[0]
	
	if major_name_match:
		major_name = major_name_match.groups()[0]

	ua_data.extend([medium_name, major_name])
	return ua_data


def get_category_page_ua(category_page_link):
	uas = []
	category_page = urllib2.urlopen(category_page_link).read()
	exp = re.compile('<td class="useragent"><a href="(.+?)">(.+?)</a></td>')
	for (link, user_agent) in re.findall(exp, category_page):
		data = [link, user_agent] + get_ua_data(URL_PREFIX + link)
		yield data
		# uas.append(data)
	# return uas


def get_category_data(category_uri):
	category_link = URL_PREFIX + category_uri
	category_data = []
	category_page = urllib2.urlopen(category_link).read()

	last_page_pattern = '<a href="{}(.+?)">Last Page '.format(category_uri)
	exp = re.compile(last_page_pattern)
	last_page_regex = re.search(exp, category_page)

	if last_page_regex is not None:
		last_page = int(last_page_regex.groups()[0])
	else:
		last_page = 1

	for page_num in range(1, last_page+1):
		next_url = category_link + str(page_num)
		# category_data.extend(get_category_page_ua(next_url))
		for ua in get_category_page_ua(next_url):
			yield ua

	# return category_data

def fetch_data():
	# categories_data = {}
	exp = re.compile('<td><a href="(.+?)" class="maybe-long">(.+?)</a></td>')
	main = urllib2.urlopen(MAIN_URL).read()
	for (link, name) in re.findall(exp, main):
		if name in IGNORE:
			print "skipping ",name
			continue
		# category_data = get_category_data(link)
		# categories_data[name] = []
		for datum in get_category_data(link):
			row = [name] + list(datum)
			# categories_data[name].append(row)
			yield row

def crawl():
	try:
		# if not os.path.exists('uas.csv'):
		# 	with open('uas.csv', 'wb') as csvfile:
		# 		ua_data_writer.writerow(columns)
		with open('uas.csv', 'wb') as csvfile:
			ua_data_writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for data in fetch_data():
				print data
				ua_data_writer.writerow(data)

	except KeyboardInterrupt as ex:
		print "caught ", ex

if __name__ == "__main__":
	crawl()