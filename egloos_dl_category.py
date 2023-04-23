#!/usr/bin/env python3

#imports
from egloos_api import *
from bs4 import BeautifulSoup
import json

##############################################################################################
# vars
##############################################################################################
#### dl path
username = "help"
category_name = "게시물 관리"
out_dir = "baz"
sleep_ms = 1000
reverse_order = True

#### misc config
verbose = True
generate_html = True
##############################################################################################

##############################################################################################
# main
##############################################################################################
def main():
	print(f"username: {username}, category: {category_name}")
	print("Downloading post lists")
	cat_1, cat_2 = get_categories(username, sleep_ms = sleep_ms, verbose = False)
	category_no = cat_2[category_name]
	#get list of post URLs
	posts = get_post_list(username, category_no = category_no, sleep_ms = sleep_ms, verbose = False, show_progress=True)
	if verbose:
		print(f"Total {len(posts)} articles.")
		
	if(reverse_order):
		posts.reverse()

	#mkdir output directory
	if not os.path.exists(out_dir):
		os.mkdir(out_dir)
				
	#get pages
	cnt = 1
	

	if(generate_html):
		f_index_pg = open(out_dir+"/"+"index.html", "w")
		f_index_pg.write(f"<!DOCTYPE html> <html lang=\"ko\"><head>")
		f_index_pg.write("<style> img {display: block;}</style>")
		f_index_pg.write("<meta content=\"text/html; charset=utf-8\" /><title>index</title> </head>")
		f_index_pg.write(f"<body> <ul>")

	for i in posts:
		contents = get_post(username, i['post_no'], sleep_ms = sleep_ms, verbose = False)
		contents_comments = get_comments(username, i['post_no'], sleep_ms = sleep_ms, verbose = False)
		
		print(f"({cnt}) {contents['post_title']}")
		
		save_path = out_dir + '/' + str(i['post_no'])
		if not os.path.exists(save_path):
			os.mkdir(save_path)
				
		save_path_img = out_dir + '/' + str(i['post_no'])+"/assets"
		if not os.path.exists(save_path_img):
			os.mkdir(save_path_img)
			
		#get images!
		prefix = format(cnt, '03d')
		contents['post_content'] = get_images(contents['post_content'],save_path_img,sleep_ms, prefix, replace_urls = True)
		
		#save page
		f = open(save_path+"/"+str(i['post_no'])+".json", "w")
		f.write(json.dumps(contents))
		f.close()
		
		f = open(save_path+"/"+str(i['post_no'])+"_comments.json", "w")
		f.write(json.dumps(contents_comments))
		f.close()
		
		if(generate_html):
			f = open(save_path+"/"+str(i['post_no'])+".html", "w")
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
			
			f_index_pg.write(f"<li><a href=\"{i['post_no']}/{i['post_no']}.html\"> ({contents['post_date_created']}) {contents['post_title']}</a></li>")
		#increase post counter
		cnt += 1


	if(generate_html):
		f_index_pg.write(f"</ul></body> </html>")
		f_index_pg.close()
		
##############################################################################################

##############################################################################################
# fcts
##############################################################################################
#Gets images
#very hacky (wontfix - Egloos is closing anyway)
def get_images(contents,save_path,sleep_time,prefix, replace_urls=False):
	soup = BeautifulSoup(contents, 'html.parser')	
	s3 = soup.find_all('img')
	
	#for each image tag:
	cnt = 1
	for i in s3:
		#set store file name
		filename = format(cnt, '03d')
		if(i.has_attr('filename')):
			filename = prefix+"_"+filename + "_" + str(i['filename'])
		elif len(str(i['src']).split("/")[-1].split(".")) > 1:
			ext = str(i['src']).split("/")[-1].split(".")[-1]
			filename = prefix+"_"+filename + "_." + ext
		else:
			filename = prefix+"_"+filename + ".jpg"
			
		#set store path
		full_path = save_path+"/" + filename
		
		#get the file
		#skip ico_badreport.png
		uri = str(i['src'])
		if("ico_badreport.png" in uri):
			continue
			

		#do download
		print(f"{filename} {uri}")
		
		if(not(download_img(uri, full_path, sleep_ms = sleep_ms, retry = 3, verbose = False))):
			print("what")
		
		i['src'] = "assets/"+filename
		cnt += 1
	#print(str(soup))
		
	return str(soup)

##############################################################################################
	
#run main	
if __name__ == "__main__":
	main()
