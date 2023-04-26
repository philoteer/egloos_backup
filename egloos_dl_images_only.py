#!/usr/bin/env python3

#imports
from egloos_api import *
from bs4 import BeautifulSoup
import json
import shutil, os

##############################################################################################
# vars
##############################################################################################
#### dl path
username = input('User ID? ')
out_dir = username
sleep_ms = int(input("Delay per download? [default: 100]") or "100")
reverse_order = input("Reverse the post order? [Y/N; default: N] ")
reverse_order = (reverse_order == "y" or reverse_order == "Y")

download_all = input("Download all posts? [\"ALL\" for all posts; \"CAT\" for one category. default:ALL]")
download_all = not(download_all.lower() == "category" or download_all.lower() == "cat")
#### misc config
verbose = True

remove_cache = True
##############################################################################################

##############################################################################################
# main
##############################################################################################

def archive_all():
	#make output dir if needed
	if not os.path.exists(out_dir):
		os.mkdir(out_dir)
		
	#get categories
	categories_dict, categories_dict_rev = get_categories(username, sleep_ms = sleep_ms, verbose = False)
	print(f"categories: {categories_dict}")
	
	#per each category:
	for category_no in categories_dict:
		print(categories_dict[category_no])		
		#get category
		download_category(username, category_no, out_dir)
		
	if(remove_cache and os.path.exists(cache_path)):
		shutil.rmtree(cache_path)

def download_category(username, category_no, out_dir):
	print("Downloading post lists")
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
	
	for i in posts:
		contents = get_post(username, i['post_no'], sleep_ms = sleep_ms, verbose = False)
		
		print(f"({cnt}) {contents['post_title']}")
				
		save_path_img = out_dir + '/' + format(cnt, '05d')
		if not os.path.exists(save_path_img):
			os.mkdir(save_path_img)
			
		#get images!
		prefix = format(cnt, '05d')
		
		_ = get_images(contents['post_content'],save_path_img,sleep_ms, prefix, replace_urls = True)
		
		#increase post counter
		cnt += 1

		
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
		try:
			#set store file name
			filename = format(cnt, '05d')
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

			if(not(download_img(uri, full_path, sleep_ms = sleep_ms, retry = 3, verbose = False,skip_if_exists=True))):
				print("download failed")

			i['src'] = "assets/"+filename
			cnt += 1
		except:
			print("exception thrown")
	#print(str(soup))
		
	return str(soup)

##############################################################################################
	
#run main	
if __name__ == "__main__":
	if(download_all):
		archive_all()
	else:
		categories_dict, categories_dict_rev = get_categories(username, sleep_ms = sleep_ms, verbose = False)
		print(f"categories: {categories_dict}")
		
		category_no = int(input("Category number (*an integer, not a string)? "))
		print(categories_dict[category_no])		
		download_category(username, category_no, out_dir)
			
		if(remove_cache and os.path.exists(cache_path)):
			shutil.rmtree(cache_path)


	print("##########################################")
	print("Done. Press enter to exit.")
	print("##########################################")
	input()
