import sys
import requests
import lxml.html
import re

global_keys = set([]) # TODO refactor

def get_links_from_url(url):
	page = requests.get(url)
	if page.status_code != 200:
		print "%s: %d" % (url, page.status_code)
		return
	dom = lxml.html.fromstring(page.content)
	find_api_keys(url, page.content, global_keys)
	return dom.xpath('//a/@href')

def find_api_keys(url, data, keys=None, keylen=16, wordlen=4):
	#print data
	#if "a" in data: 
	if keys is None:
		keys = set([])
	matches = re.findall(r"([a-zA-z0-9\-]{%d}[a-zA-Z0-9\-]*)" % keylen, data)
	if matches is not None:
		for m in matches[1:]:
			if re.findall(r"[a-zA-Z]{%d}" % wordlen, m): # heuristic to remove function names
				continue
			if m in keys:
				continue
			print m
			keys.add(m)
	return keys


def get_all_domain_links(url):
	return get_all_domain_links_set(url, set([url]))

def get_all_domain_links_set(first_url, urlset):
	new_links = set([])
	for url in urlset:
		raw_links = get_links_from_url(url)
		#print raw_links
		links = get_normalized_domain_urls(first_url, raw_links)
		#print url, len(links)
		for link in links: 
			new_links.add(link)
	for link in new_links: 
		urlset.add(link)
	if len(new_links) == 0:
		return urlset
	return get_all_domain_links_set(url, urlset)

def get_normalized_domain_urls(url, linkset):
	if linkset is None:
		linkset = set([])
	urlset = set([])
	for i, link in enumerate(linkset):
		if re.match(r"^[http|http]://.*url", link):
			urlset.add(link)
		elif re.match(r"^[http|https]", link):
			continue
		elif link[0] == "/":
			urlset.add(url + link)
	return urlset

def main(url):
	print get_all_domain_links("https://%s" % url)

if __name__ == "__main__":
	main(sys.argv[1])