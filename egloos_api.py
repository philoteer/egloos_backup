import requests, json
import time
import os
############### configs
headers = {'User-Agent': 'Mozilla/5.0 (XWayland; OS/2 mipseb; rv:25.25) Gecko/43430101 Firefox/39.[object Object]'}
use_cache = True
cache_path = './cache'

if(use_cache):
	import hashlib
########################################################################

#see: http://apicenter.egloos.com/manual_post.php
def get_page(uri, sleep_ms = 1, retry = 3, verbose = False, return_json = False):
	#check cache (optional)
	if(use_cache):
		if not os.path.exists(cache_path):
			os.mkdir(cache_path)	
			
		uri_hash = hashlib.sha1(uri.encode('utf-8')).hexdigest()
			
			
		if os.path.exists(cache_path + "/" + uri_hash):
			f = open(cache_path + "/" + uri_hash, "r", encoding="utf-8")
			s = f.read()
			f.close()
			
			if(return_json):
				s = json.loads(s)

			return s

	#do attempt to get
	for i in range (0, retry):
		try:
			data = requests.get(uri, headers=headers)
			time.sleep(sleep_ms/1000)
			out = data.text
			
			if(data.status_code != 200):
				raise Exception("non-200 HTTP status")
				
			#cache the data
			if(use_cache):
				f = open(cache_path + "/" + uri_hash, "w", encoding="utf-8")
				f.write(data.text)
				f.close()
			
			if(return_json):
				out = json.loads(out)
				

			return out
		except:
			if(verbose):
				print(f"exception: failed to get ({uri}, {i})")
			time.sleep(1.0)
	
	if(verbose):
		print(f"Retry count is up; I give up. ({uri})")
	return None
		
def download_img(uri, save_path, sleep_ms = 1, retry = 3, verbose = False, skip_if_exists=False):
	if(skip_if_exists and os.path.isfile(save_path)):
		return True
	
	#download original instead of the thumbnail (hacky)
	if("thumbnail.egloos" in uri):
		uri = uri.split("http://")[-1]
		uri = f"http://{uri}"

	#do attempt to get
	for i in range (0, retry):
		try:
			data = requests.get(uri, headers=headers)
			time.sleep(sleep_ms/1000)
			if data.status_code == 200:
				f = open(save_path, "wb")
				f.write(data.content)
				f.close()	
				return True
				
		except:
			if(verbose):
				print(f"exception: failed to get ({uri}, {i})")
			time.sleep(1.0)
	
	if(verbose):
		print(f"Retry count is up; I give up. ({uri})")
	return False
	
#outputs 2 dict:
#out_1 : key = index num, val = name(string)
#out_2 : key = name(string), val = index num
def get_categories(username, sleep_ms = 1, verbose = False):
	uri = f'https://api.egloos.com/{username}/category.json'
	data = get_page(uri,sleep_ms, verbose = verbose, return_json = True)
	
	if data is None:
		if verbose:
			print(f"get_categories failed! ({uri})")
		return
		
	data = data['category']
	out_1 = {} #key = index num, val = name(string)
	out_2 = {} #key = name(string), val = index num
	for datum in data:
		out_1[int(datum['category_no'])]  = datum['category_name']
		out_2[datum['category_name']]  = int(datum['category_no'])
	
	return out_1, out_2
		
#outputs a list of dict, in style:
#{'comment_no': xxx, 'comment_date_created': '1970-01-01 00:00:00', 'comment_writer': 'id', 'comment_nick': 'nick', 'comment_writer_url': 'http://something.so', 'comment_writer_homepage': None, 'comment_hidden': '', 'comment_content': 'something', 'comment_depth': 'num', 'comment_writer_thumbnail': 'http://profile.egloos.net/something.jpg'}
def get_comments_per_pg(username, post_no, page_no, sleep_ms = 1, verbose = False):
	
	uri = f'https://api.egloos.com/{username}/post/{post_no}/comment.json?page={page_no}'
	data = get_page(uri,sleep_ms, verbose = verbose, return_json = True)
	
	if data is None:
		if verbose:
			print(f"get_comments_per_pg failed! ({uri})")
		return
	
	data = data['comment']
	
	return data

#outputs a list of dict, in style:
#{'comment_no': xxx, 'comment_date_created': '1970-01-01 00:00:00', 'comment_writer': 'id', 'comment_nick': 'nick', 'comment_writer_url': 'http://something.so', 'comment_writer_homepage': None, 'comment_hidden': '', 'comment_content': 'something', 'comment_depth': 'num', 'comment_writer_thumbnail': 'http://profile.egloos.net/something.jpg'}
def get_comments(username, post_no, sleep_ms = 1, verbose = False):	
	page_no = 1
	out = []
	while(True):
		comments = get_comments_per_pg(username,post_no,page_no, sleep_ms=sleep_ms,verbose=verbose)
		page_no += 1
		if (comments is None):
			return out
			
		out.extend(comments)
		
		if(len(comments) < 100):
			break;
			
	return out

#outputs a list of dict, in style:
#{'post_title': 'foo', 'post_content': 'bar', 'post_thumb': 'http://thumbnail.egloos.net/100x76/...', 'category_name': 'baz', 'post_url': 'baq', 'post_no': 'num', 'comment_count': 'some_no', 'open_comment_count': 'some_no', 'post_hidden': some_no, 'post_date_created': '1970-01-01 00:00:00'}
def get_post_list_per_pg(username, page_no, category_no = None, sleep_ms = 1, verbose = False):
	
	uri = f'https://api.egloos.com/{username}/post.json?page={page_no}'
	if(category_no is not None):
		uri = f'{uri}&category_no={category_no}'
	
	data = get_page(uri,sleep_ms, verbose = verbose, return_json = True)
	
	if data is None:
		if verbose:
			print(f"get_post_list_per_pg failed! ({uri})")
		return
	
	data = data['post']
	
	return data
	
#outputs a list of dict, in style:
#{'post_title': 'foo', 'post_content': 'bar', 'post_thumb': 'http://thumbnail.egloos.net/100x76/...', 'category_name': 'baz', 'post_url': 'baq', 'post_no': 'num', 'comment_count': 'some_no', 'open_comment_count': 'some_no', 'post_hidden': some_no, 'post_date_created': '1970-01-01 00:00:00'}
def get_post_list(username, category_no = None, sleep_ms = 1, verbose = False, show_progress = False):
	page_no = 1
	out = []
	while(True):
		posts = get_post_list_per_pg(username, page_no, category_no = category_no, sleep_ms = sleep_ms, verbose = verbose)
		if(posts is None):
			return out
			
		out.extend(posts)
		if(show_progress):
			print(f"pg #{page_no}: {len(posts)} articles.")
		page_no += 1
		
		if(len(posts) < 10):
			break;
			
	return out

#outputs a dict:
#{'post_title': 'foo', 'post_no': 'no', 'post_content': 'bar', 'category_name': 'baz', 'category_no': 'no', 'post_nick': 'handle', 'comment_count': '0', 'trackback_count': '0', 'post_hidden': 0, 'comment_enabled': '1', 'trackback_enabled': '1', 'post_date_created': '1970-01-01 00:00:00', 'post_date_modified': '1970-01-01 00:00:00', 'post_tags': None}
def get_post(username, post_no, sleep_ms = 1, verbose = False, return_json = True):
	uri = f'https://api.egloos.com/{username}/post/{post_no}.json'
	data = get_page(uri,sleep_ms, verbose = verbose, return_json = return_json)
	
	if data is None:
		if verbose:
			print(f"get_post failed! ({uri})")
		return
	
	if (return_json):
		data = data['post']
	
	return data


##################################### unofficial fct
def write_html_post(contents,contents_comments, path):
	f = open(path, "w", encoding="utf-8")
	f.write(f"<!DOCTYPE html> <html lang=\"ko\"><head>")
	f.write("<style> img {display: block;}</style>")
	f.write(f"<meta content=\"text/html; charset=utf-8\" /><title>{contents['post_title']}</title> </head>")
	f.write(f"<body>")
	f.write(f"<h1>")
	f.write(contents['post_title'])
	f.write(f"</h1>")			
	f.write(f"<h2>")
	f.write(f"카테고리: {contents['category_name']}; 댓글수: {contents['comment_count']}; 게시일: {contents['post_date_created']}")
	f.write(f"</h2> <hr>")			
	f.write(contents['post_content'])
	f.write(f"<hr> <h2>")
	f.write(f"댓글")
	f.write(f"</h2> ")
	
	if(contents_comments is not None):
		for comment in contents_comments:
			f.write("<p>")
			f.write(f"<h3> 작성자: {comment['comment_nick']}  작성일: {comment['comment_date_created']} </h3>")
			f.write(f"{comment['comment_content']}")
			f.write("</p>")
			
			
	f.write(f"</body> </html>")
	f.close()
