#!/usr/bin/env python3

#imports
from egloos_api import *
from bs4 import BeautifulSoup
'''
import re, sys
'''
##############################################################################################
# vars
##############################################################################################
#### dl path
username = "help"
category_name = "이글루스란?"
out_dir = "baz"
sleep_ms = 1000
reverse_order = True

#### misc config
verbose = True
##############################################################################################

##############################################################################################
# main
##############################################################################################
def main():
	print(f"username: {username}, category: {category_name}")
	print("downloading post lists")
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
		
	#cache posts
	cnt = 1
	for i in posts:
		#get page
		print(f"Getting {i['post_url']} ({cnt})")
		_ = get_post(username, i['post_no'], sleep_ms = sleep_ms, verbose = False)
		cnt +=1 
		
	#get images
	cnt = 1
	for i in posts:
		#get page
		contents = get_post(username, i['post_no'], sleep_ms = sleep_ms, verbose = False)
		
		print(f"({cnt}) {contents['post_title']}")
		
		save_path = out_dir + '/'
				
		#get images!
		prefix = format(cnt, '03d')
		get_images(contents['post_content'],save_path,sleep_ms, prefix)
		
		#increase post counter
		cnt += 1

##############################################################################################

##############################################################################################
# fcts
##############################################################################################
#Gets images
#very hacky (wontfix - Egloos is closing anyway)
def get_images(contents,save_path,sleep_time,prefix):
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
			print("image download failed.")
		
		
		cnt += 1

##############################################################################################
	
#run main	
if __name__ == "__main__":
	main()
