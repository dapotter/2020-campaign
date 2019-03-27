# Operating this script in Conda environment 'fwp_venv'
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import datetime
import time
import csv

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from apscheduler.schedulers.background import BackgroundScheduler

import re

sched = BackgroundScheduler()

# Create original dataframe once:
def DonorCounter():
	#global df

	driver = webdriver.Chrome('/usr/bin/chromedriver')
	# This doesn't allow the donor count to update: driver.minimize_window()
	driver.set_window_size(0, 0)
	driver.set_window_position(0,0)
	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
	url = 'https://www.yang2020.com/'
	driver.get(url)
	time.sleep(1) # Allow the user see website load
	donor_count_str = driver.find_element_by_class_name('donor-count-number').text
	donor_goal_str = driver.find_element_by_css_selector('.total.goal').text
	donor_count = int(float(donor_count_str.replace(',','')))
	donor_goal = int(float(donor_goal_str.replace(',','')))
	donor_pcnt = (donor_count / donor_goal)*100
	current_time = datetime.datetime.now()

	print('donor_count:', donor_count)
	print('donor_goal:', donor_goal)
	print('donor_pcnt:', donor_pcnt)
	print('current_time:', current_time)

	donor_arr = [current_time, donor_count, donor_goal, donor_pcnt]

	fields=['Time','Count','Goal', 'Pcnt']
	donor_dict = {'Time':current_time,'Count':donor_count,'Goal':donor_goal, 'Pcnt':donor_pcnt}
	print('donor_dict:\n', donor_dict)

	#df = df.append(donor_dict, ignore_index=True)

	''' Creates csv, overwrites the current one of the same name: '''
	# with open('DonorCountYang.csv','w') as f:
	#     writer = csv.DictWriter(f, fieldnames=fields)
	#     writer.writerow(donor_dict)

	''' Appends the csv '''
	with open(r'DonorCountYang.csv', 'a', newline='') as f:
	    writer = csv.DictWriter(f, fieldnames=fields)
	    writer.writerow(donor_dict)
	
	# Close driver:
	driver.quit()

	# Read csv into dataframe:
	df = pd.read_csv('DonorCountYang.csv')
	print('df head:\n', df.head)
	# Format Time column
	df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
	# Check formatting:
	#print('time type:\n', type(df.iloc[0]['Time']))
	
	print('Donor Count df:\n', df.to_string())

	# ''' Plotting data: '''
	#fig = plt.figure()
	w = 3
	h = 3
	#fig = plt.figure(frameon=False)
	#fig.set_size_inches(w,h)
	plt.figure()
	plt.plot(df['Time'], df['Count'], linewidth=1, marker='o', markersize=3, markerfacecolor='none', markeredgecolor='k')
	plt.xlabel('DateTime'); plt.ylabel('Number of donors')
	plt.xticks(rotation='vertical')
	plt.savefig('DonorCountYang.png', bbox_inches='tight')
	plt.show()
	# ''' --------------- '''

	# ''' try-except isn't necessary unless webpage won't load '''
	#
	# try:
	# 	element_present = EC.presence_of_element_located((By.CLASS_NAME, 'donor-count-number'))
	# 	WebDriverWait(driver, timeout).until(element_present)
	# 	donor_count_3 = driver.find_element_by_class_name('donor-count-number')
	# 	print('donor_count_3:\n', donor_count_3.text)
	# except TimeoutException:
	# 	print("Timed out waiting for page to load")

	return df



''' --- Betting Percentiles --- '''
def CampaignBetting():
	driver = webdriver.Chrome('/usr/bin/chromedriver')
	# Runningn 'driver.minimize_window()' doesn't allow the donor count to update
	driver.set_window_size(0, 0)
	driver.set_window_position(0,0)
	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
	url = 'https://electionbettingodds.com/'
	driver.get(url)
	time.sleep(1) # Allow the user see website load
	
	#--- Getting candidate names:
	# Gets all names except for 'Other': href_links = driver.find_elements(By.TAG_NAME, "a")
	# Gets all names except for 'Other': href_links = driver.find_elements(By.XPATH, '//td/a/img')
	img_elements = driver.find_elements_by_tag_name('img')
	img_elements_list = [str(img.get_attribute('src')) for img in img_elements]
	# print('img_elements_list:\n', img_elements_list)
	
	# Filtering: unfiltered_name_list contains candidate names and instances of 'green' and 'red'
	unfiltered_name_list = [s.replace('https://electionbettingodds.com/','').replace('.png','') for s in img_elements_list if '/' in s]
	name_list = [i for i in unfiltered_name_list if 'red' not in i and 'green' not in i]
	# print('name_list:\n', name_list)

	#--- Getting betting percentiles:
	bet_percentiles = driver.find_elements_by_xpath("//p[@style='font-size: 55pt; margin-bottom:-10px']")
	pcnt_list = [float(pcnt.get_attribute('innerHTML').replace('%','')) for pcnt in bet_percentiles]
	
	num_names = len(name_list)
	num_pcnts = len(pcnt_list)
	if num_names != num_pcnts:
		print('!!!!!!!!!!!! Warning: number of candidates does not match number of percentiles')

	# Combine both lists:
	# Not using this: name_pcnt_list = [[i,j] for i,j in zip(name_list,pcnt_list)]
	
	# Get current time:
	current_time = datetime.datetime.now()
	# print('current_time:', current_time)

	#name_list.append('time')
	#pcnt_list.append(current_time)

	print(name_list)
	print(pcnt_list)
	print('len name_list:', len(name_list))
	print('len pcnt_list:', len(pcnt_list))

	# Finding 'Other' in the names list to split the list into Democratic, Republican and Presidential primaries
	# [add 1 to every element x of [16, 47, 53 <- indices where 'Other' is located]]
	# Results in [17, 48, 54]
	end_indices = [x+1 for x in [i for i, n in enumerate(name_list) if n == 'Other']]
	start_indices = [0] + end_indices[0:-1]

	grouped_name_list = []; grouped_pcnt_list = []
	for i,j in zip(start_indices, end_indices):
		grouped_name_list.append(name_list[i:j])
		grouped_pcnt_list.append(pcnt_list[i:j])

	# print('grouped_name_list:\n', grouped_name_list)
	# print('grouped_pcnt_list:\n', grouped_pcnt_list)
	# print('end indices:', end_indices)
	# print('start_indices:', start_indices)

	dem_fields = ['Time'] + grouped_name_list[0] #['Time','Count','Goal', 'Pcnt']
	rep_fields = ['Time'] + grouped_name_list[2]
	pres_fields = ['Time'] + grouped_name_list[1]
	# print('dem_fields:\n', dem_fields)
	# print('rep_fields:\n', rep_fields)
	# print('pres_fields:\n', pres_fields)

	dem_pcnts = [current_time] + grouped_pcnt_list[0]
	rep_pcnts = [current_time] + grouped_pcnt_list[2]
	pres_pcnts = [current_time] + grouped_pcnt_list[1]
	# print('dem_pcnts:\n', dem_pcnts)
	# print('rep_pcnts:\n', rep_pcnts)
	# print('pres_pcnts:\n', pres_pcnts)

	dem_field_pcnt_list = [[i,j] for i,j in zip(dem_fields,dem_pcnts)]
	rep_field_pcnt_list = [[i,j] for i,j in zip(rep_fields,rep_pcnts)]
	pres_field_pcnt_list = [[i,j] for i,j in zip(pres_fields,pres_pcnts)]
	# print('dem_field_pcnt_list:\n', dem_field_pcnt_list)

	''' --- Making dictionaries for csv export --- '''
	''' Dict comprehension syntax:		d = {key: value for (key, value) in iterable} '''
	''' Dict comprehension from lists:	d = {key: value for (key, value) in zip(key_list, value_list)} '''
	dem_dict = {key: value for (key, value) in zip(dem_fields, dem_pcnts)}
	rep_dict = {key: value for (key, value) in zip(rep_fields, rep_pcnts)}
	pres_dict = {key: value for (key, value) in zip(pres_fields, pres_pcnts)}
	# print('dem_dict:\n', dem_dict)
	# print('rep_dict:\n', rep_dict)
	# print('pres_dict:\n', pres_dict)

	# DON'T NEED BECAUSE TIME IS INCLUDED ABOVE
	# time_dict = {'Time':current_time}
	# dem_dict = dem_dict.update(time_dict)
	# print('dem_dict:\n', dem_dict)
	# rep_dict = rep_dict.update(time_dict)
	# print('rep_dict:\n', rep_dict)
	# pres_dict = pres_dict.update(time_dict)
	# print('rep_dict:\n', rep_dict)

	''' Creates csv, overwrites the current one of the same name: '''
	''' --- Only run once, then use append code block below --- '''
	# # Writing percents to csv:
	# with open('RaceDem.csv','w') as f:
	# 	writer = csv.DictWriter(f, fieldnames=dem_fields)
	# 	writer.writeheader()
	# 	writer.writerow(dem_dict)
	# with open('RaceRep.csv','w') as f:
	# 	writer = csv.DictWriter(f, fieldnames=rep_fields)
	# 	writer.writeheader()
	# 	writer.writerow(rep_dict)
	# with open('RacePres.csv','w') as f:
	# 	writer = csv.DictWriter(f, fieldnames=pres_fields)
	# 	writer.writeheader()
	# 	writer.writerow(pres_dict)

	# Writing fields to csv to notify if political field changes
	# cols = list(range(0,len(dem_fields)))
	# with open('RaceFieldsDem.csv','w') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(cols)
	# 	writer.writerow(dem_fields)
	# cols = list(range(0,len(rep_fields)))
	# with open('RaceFieldsRep.csv','w') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(cols)
	# 	writer.writerow(rep_fields)
	# cols = list(range(0,len(pres_fields)))
	# with open('RaceFieldsPres.csv','w') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(cols)
	# 	writer.writerow(pres_fields)
	''' --------------------------------------------------------- '''
	
	''' --- Appends csv files --- '''
	# Writing percents to csv:
	with open(r'RaceDem.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=dem_fields)
		writer.writerow(dem_dict)
	with open(r'RaceRep.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=rep_fields)
		writer.writerow(rep_dict)
	with open(r'RacePres.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=pres_fields)
		writer.writerow(pres_dict)

	# Writing fields to csv to notify if political field changes
	with open(r'RaceFieldsDem.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(dem_fields)
	with open(r'RaceFieldsRep.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(rep_fields)
	with open(r'RaceFieldsPres.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(pres_fields)
	''' ------------------------- '''

	# Close driver:
	driver.quit()

	# Read csv files into dataframe:
	df_dem = pd.read_csv('RaceDem.csv')
	df_rep = pd.read_csv('RaceRep.csv')
	df_pres = pd.read_csv('RacePres.csv')
	df_dem_field = pd.read_csv('RaceFieldsDem.csv')
	df_rep_field = pd.read_csv('RaceFieldsRep.csv')
	df_pres_field = pd.read_csv('RaceFieldsPres.csv')
	# Checking data:
	print('df_dem bet percents:\n\n', df_dem.to_string())
	print('\n\n')
	print('df_dem_field:\n\n', df_dem_field.to_string())
	print('\n\n')

	# Generate warning if latest field doesn't match prior:
	# if previous dem field from csv (df_dem_field.iloc[-1]) doesn't match current scraped dem field (df_dem_field)
	# print('list(df_dem_field.iloc[-1]):\n', list(df_dem_field.iloc[-1]))
	# print('dem_fields:\n', dem_fields)

	# Print if there's a disagreement between scraped and previous fields
	# print('df_dem_field.iloc[-1]:\n', df_dem_field.iloc[-1])
	# print('dem_fields:\n', dem_fields)
	# print('df_rep_field.iloc[-1]:\n', df_rep_field.iloc[-1])
	# print('rep_fields:\n', rep_fields)
	# print('df_pres_field.iloc[-1]:\n', df_pres_field.iloc[-1])
	# print('pres_fields:\n', pres_fields)

	if any(df_dem_field.iloc[-1] != dem_fields):
		print('!!!!!!!!!!!!!!!!!!!!!!! Dem field has changed')
	if any(df_rep_field.iloc[-1] != rep_fields):
		print('!!!!!!!!!!!!!!!!!!!!!!! Rep field has changed')
	if any(df_pres_field.iloc[-1] != pres_fields):
		print('!!!!!!!!!!!!!!!!!!!!!!! Pres field has changed')

	# Format csv derived Time column before plotting:
	df_dem['Time'] = pd.to_datetime(df_dem['Time'], format='%Y-%m-%d %H:%M:%S')
	df_rep['Time'] = pd.to_datetime(df_rep['Time'], format='%Y-%m-%d %H:%M:%S')
	df_pres['Time'] = pd.to_datetime(df_pres['Time'], format='%Y-%m-%d %H:%M:%S')
	# Check time formatting:
	# print('time type:\n', type(df_dem.iloc[0]['Time']))

	# Append latest scraped data (dem_fields) to csv derived df's (df_dem):
	df_dem = df_dem.append(dem_dict, ignore_index=True)
	df_rep = df_rep.append(rep_dict, ignore_index=True)
	df_pres = df_pres.append(pres_dict, ignore_index=True)
	df_dem_field = df_dem_field.append(dem_fields, ignore_index=True)
	df_rep_field = df_rep_field.append(rep_fields, ignore_index=True)
	df_pres_field = df_pres_field.append(pres_dict, ignore_index=True)

	# Close driver:
	driver.quit()

	plt.close()

	df_dem_no_time = df_dem.drop(columns=['Time','Yang','Biden'])
	cols = df_dem_no_time.columns
	ax = df_dem.plot(x='Time', y='Yang', color='b', linewidth=2, markersize=5, marker='o', markeredgecolor='b', markerfacecolor='white')
	df_dem.plot(x='Time', y='Biden', ax=ax, color='g', linewidth=2, markersize=5, marker='o', markeredgecolor='g', markerfacecolor='white')
	df_dem.plot(x='Time', y=cols, ax=ax)
	plt.xlabel('Datetime'); plt.ylabel('Betting odds, %'); plt.legend(loc='best')#center right', bbox_to_anchor=(0.7, 0.1, 0.5, 0.5))
	# Doesn't help the axis display: plt.xticks(rotation='vertical')
	plt.savefig('Betting Odds - Democratic Primary.png', bbox_inches='tight')
	plt.show()

	df_rep_no_time = df_rep.drop(columns=['Time','Trump','Pence'])
	cols = df_rep_no_time.columns
	ax = df_rep.plot(x='Time', y='Trump', color='r', linewidth=2, markersize=5, marker='o', markeredgecolor='r', markerfacecolor='white')
	df_rep.plot(x='Time', y='Pence', ax=ax, color='g', linewidth=2, markersize=5, marker='o', markeredgecolor='g', markerfacecolor='white')
	df_rep.plot(x='Time', y=cols, ax=ax)
	plt.xlabel('Datetime'); plt.ylabel('Betting odds, %'); plt.legend(loc='best')#center right', bbox_to_anchor=(0.7, 0.1, 0.5, 0.5))
	# Doesn't help the axis display: plt.xticks(rotation='vertical')
	plt.savefig('Betting Odds - Republican Primary.png', bbox_inches='tight')
	plt.show()

	df_pres_no_time = df_pres.drop(columns=['Time','Biden','Yang','Trump'])
	#df_pres_top8_no_time = df_pres_no_time.sort_values(axis=0)
	cols = df_pres_no_time.columns
	ax = df_dem.plot(x='Time', y='Yang', color='b', linewidth=2, markersize=5, marker='o', markeredgecolor='b', markerfacecolor='white')
	df_pres.plot(x='Time', y='Trump', ax=ax, color='r', linewidth=2, markersize=5, marker='o', markeredgecolor='r', markerfacecolor='white')
	df_pres.plot(x='Time', y='Biden', ax=ax, color='g', linewidth=2, markersize=5, marker='o', markeredgecolor='g', markerfacecolor='white')
	df_pres.plot(x='Time', y=cols, ax=ax)
	plt.xlabel('Datetime'); plt.ylabel('Betting odds, %'); plt.legend(loc='best')#center right', bbox_to_anchor=(0.7, 0.1, 0.5, 0.5))
	# Doesn't help the axis display: plt.xticks(rotation='vertical')
	plt.savefig('Betting Odds - Presidential Race.png', bbox_inches='tight')
	plt.show()

	return df_dem, df_rep, df_pres, df_dem_field, df_rep_field, df_pres_field



def WebMetrics():
	''' URLs: '''
	# Biden: https://www.instagram.com/joebiden/
	# Yang: https://www.instagram.com/andrewyang2020/
	# Gabbard: https://www.instagram.com/tulsigabbard/
	# Harris: https://www.instagram.com/kamalaharris/ # Events: https://www.mobilize.us/kamalaharris/
	# Sanders: https://www.instagram.com/berniesanders/ # Events: 
	# Warren: https://www.instagram.com/elizabethwarren/
	# O'Rourke: https://www.instagram.com/betoorourke/
	# Booker: https://www.instagram.com/corybooker/
	# Trump: https://www.instagram.com/realdonaldtrump/
	# 
	# https://twitter.com/joebiden
	# https://twitter.com/AndrewYang
	# https://twitter.com/TulsiGabbard
	# https://twitter.com/KamalaHarris
	# https://twitter.com/BernieSanders
	# https://twitter.com/ewarren
	# https://twitter.com/BetoORourke
	# https://twitter.com/CoryBooker
	# https://twitter.com/PeteButtigieg
	# https://twitter.com/amyklobuchar
	# https://twitter.com/realDonaldTrump
	# 
	# Followers element:
	# <a class="-nal3 " href="/elizabethwarren/followers/"><span class="g47SY " title="1,342,293">1.3m</span> followers</a>
	# followers_elements = driver.find_elements_by_tag_name('a')
	# follower_el_list = [int(follower_elements.get_attribute(title)) for follower_count in followers_elements]
	#
	# Tweets element:
	# <span class="ProfileNav-value" data-count="6802" data-is-compact="false">6,802</span>
	#
	# Following element:
	# <span class="ProfileNav-value" data-count="4258" data-is-compact="false">4,258</span>
	#
	# Followers element:
	# <span class="ProfileNav-value" data-count="193814" data-is-compact="true">194K</span>
	# 
	# Tweet time element:
	# <a href="/AndrewYang/status/1109526585420464129" class="tweet-timestamp js-permalink js-nav js-tooltip" title="11:45 AM - 23 Mar 2019" data-conversation-id="1109526585420464129"><span class="_timestamp js-short-timestamp js-relative-timestamp" data-time="1553366726" data-time-ms="1553366726000" data-long-form="true" aria-hidden="true">2h</span><span class="u-hiddenVisually" data-aria-label-part="last">2 hours ago</span></a>
	# 
	# Tweet contents:
	# <p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" lang="en" data-aria-label-part="0">Thanks for the shoutout <a href="/cthagod" class="twitter-atreply pretty-link js-nav" dir="ltr" data-mentioned-user-id="17878322"><s>@</s><b>cthagod</b></a> <img class="Emoji Emoji--forText" src="https://abs.twimg.com/emoji/v2/72x72/1f44d.png" draggable="false" alt="👍" title="Thumbs up sign" aria-label="Emoji: Thumbs up sign"><a href="https://t.co/utSmWtDxLD" rel="nofollow noopener" dir="ltr" data-expanded-url="https://www.cbsnews.com/live-news/charlamagne-tha-god-interview-cbs-news-president-2020/?ftag=CNM-00-10aab6a&amp;linkId=65096384" class="twitter-timeline-link u-hidden" target="_blank" title="https://www.cbsnews.com/live-news/charlamagne-tha-god-interview-cbs-news-president-2020/?ftag=CNM-00-10aab6a&amp;linkId=65096384"><span class="tco-ellipsis"></span><span class="invisible">https://www.</span><span class="js-display-url">cbsnews.com/live-news/char</span><span class="invisible">lamagne-tha-god-interview-cbs-news-president-2020/?ftag=CNM-00-10aab6a&amp;linkId=65096384</span><span class="tco-ellipsis"><span class="invisible">&nbsp;</span>…</span></a></p>
	# <p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" lang="en" data-aria-label-part="0">Fear does not exist in this dojo.<a href="https://t.co/gz8JiqaRCY" class="twitter-timeline-link u-hidden" data-pre-embedded="true" dir="ltr">pic.twitter.com/gz8JiqaRCY</a></p>

	# Scraping socialblade.com:
	driver = webdriver.Chrome('/usr/bin/chromedriver')
	# Runningn 'driver.minimize_window()' doesn't allow the donor count to update
	driver.set_window_size(0, 0)
	driver.set_window_position(0,0)
	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
	twitter_handle_list = ['https://twitter.com/AndrewYang', 'https://twitter.com/joebiden', 'https://twitter.com/TulsiGabbard',
							'https://twitter.com/KamalaHarris,' 'https://twitter.com/BernieSanders', 'https://twitter.com/ewarren',
							'https://twitter.com/BetoORourke', 'https://twitter.com/CoryBooker', 'https://twitter.com/PeteButtigieg',
							'https://twitter.com/amyklobuchar', 'https://twitter.com/realDonaldTrump']

	# Finds the index of the last /, returns s[last_/_index+1:] for all twitter handles
	twitter_name_list = [s[s.rfind('/')+1:] for s in twitter_handle_list]
	print('twitter_name_list:\n', twitter_name_list)

	df_all_names = pd.DataFrame()
	for i, twitter_name in enumerate(twitter_name_list):
		url = 'https://socialblade.com/twitter/user/' + twitter_name + '/monthly'
		print('url:', url)
		driver.get(url)
		time.sleep(5) # Allow the user see website load
		#--- Getting candidate names:
		dygraph_elements = driver.find_elements_by_xpath('//script[@type="text/javascript"]')
		dygraph_elements_list = [[dygraph.get_attribute('innerHTML')] for dygraph in dygraph_elements]
		#print('dygraph_elements_list:\n', dygraph_elements_list)

		dygraph_cleaned = []
		for dygraph in dygraph_elements_list:
			print('dygraph:\n', dygraph[0])
			for dygraph_str in dygraph:
				print('dygraph_str', dygraph_str)
				if 'new Dygraph' in dygraph_str:
					print('##########################   in for loop')
					dygraph_str = dygraph_str[dygraph_str.index('\\n" + "'):dygraph_str.rindex('\\n" ')]
					dygraph_str = dygraph_str.replace('\\n" + "','').replace('\\n" +"',',').replace('\\n" ','')
					dygraph_str = dygraph_str.split(',')
					print('cleaned dygraph_str:\n', dygraph_str)

					# dygraph_str_re_clean = re.search(',(.*),', dygraph_str)
					# if dygraph_str_re_clean:
					# 	found = dygraph_str_re_clean.group(1)
					# 	print('found:\n', found)
					# 	print('re-cleaned dygraph_str:\n', dygraph_str_re_clean)
					# for re_str in dygraph_str_re_clean.group(1):
					# 	print('re_str:\n', re_str)

					dygraph_cleaned.append(dygraph_str)

		print('---------------------------------------------------dygraph_cleaned:\n', dygraph_cleaned)

		# Getting the graph titles:
		title_elements = driver.find_elements_by_xpath('//div[@class="dygraph-label dygraph-title"]')
		replacement_str = ' for ' + twitter_name

		# Eponymous and anonymous lists:
		# Epo: ['Daily Followers Gained for Joe Biden','Total Followers for Joe Biden',...]
		# Ano: ['Daily Followers Gained','Total Followers',...]
		title_epo_list = [str(title.get_attribute('innerHTML')) for title in title_elements]
		title_ano_list = [title[:title.find(' for')] for title in title_epo_list]
		title_list = title_ano_list # Reassigning for shortness
		print('===============================================title_ano_list:\n', title_ano_list)

		# Using title_epo_list to get full candidate names e.g. 'Andrew Yang' and replace
		# space to make 'AndrewYang', 'JoeBiden', etc:
		epo_list = [title[title.find('for')+3:].replace(' ','') for title in title_epo_list]
		print('epo_list:\n', epo_list)
		# Use epo_list candidate names for csv filename construction for exporting df,
		# created downstream. epo_list contains repetitions of one name, select the first:
		csv_filename_base = '/home/dp/Documents/Campaign/Plots/' + 'TwitterMetrics_'
		csv_filename = csv_filename_base + epo_list[0] + '.csv'
		print('csv_filename:\n', csv_filename)



		reshaped_dygraph_cleaned = [np.reshape(l, (int(len(l)/2),2)) for l in dygraph_cleaned]
		print('reshaped_dygraph_cleaned:\n', reshaped_dygraph_cleaned)
		print('reshaped_dygraph_cleaned[0]:\n', reshaped_dygraph_cleaned[0])

		# date_name_title_list will be used for column titles:
		# e.g. [['2019-02-28','AndrewYang','Daily Followers Gained'], ['2019-02-29','AndrewYang','Daily Followers Gained'], ...]
		date_list = ['Date']*len(title_list)
		date_title_list = [[date,title] for date,title in zip(date_list,title_list)]
		print('date_title_list:\n', date_title_list)

		data_arr = reshaped_dygraph_cleaned[0:6]
		col_arr = date_title_list[0:6]

		# Need to make name list for each reshaped dygraph numpy array:
		#l,r,c = np.shape(x)
		#name_list = np.full((l,r,1), twitter_name)
		#Attaching name columns to data arrays:
		#data_arr = [np.hstack(d,n) for d,n in zip(data_arr,name_list)]

		# Make list of dataframes. Each has columns 'Date','Some Variable'.
		dfs = [pd.DataFrame(data=d, columns=cols) for d,cols in zip(data_arr,col_arr)]
		dfs_indexed = [df.set_index('Date') for df in dfs]
		print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$dfs_indexed:\n', dfs_indexed)
		df = pd.concat(dfs_indexed, axis=1, join='inner', sort=True)
		print('*********************************************df after concatenation:\n', df)

		# Change idex and column data types:
		df.index = pd.to_datetime(df.index, format='%Y-%m-%d', errors='coerce')
		cols = df.columns
		df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

		# Append name list ['AndrewYang','AndrewYang',...] once the final shape of
		# the dataframe is established:
		name_list = [twitter_name]*len(df)
		print('name_list:\n', name_list)
		name_series = pd.Series(data=name_list)

		print('name_series:\n', name_series.to_string())
		print('#####################################################df before series:\n', df.to_string())
		df.reset_index(inplace=True)
		print('#####################################################df before series after resetting index:\n', df.to_string())

		df = pd.concat((df,name_series.rename('Name')), axis=1)
		print('#####################################################df after series:\n', df.to_string())
		print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~df columns after series:\n', df.columns)

		df.set_index('Date', inplace=True)


		if i == 0:
			# df_all_synvar_grid_interp contains all grid interpolated synoptic variables
			df_all_names = df_all_names.append(df)
		else:
			df_all_names = pd.concat((df_all_names, df), axis=0, sort=True)
			''' ########################################### '''

		''' Creates csv, overwrites the current one of the same name: '''
		''' --- Only run once, then use append code block below --- '''
		# Writing percents to csv:
		df.to_csv(path_or_buf=csv_filename)

	# Adding the 'Name' column to the index (append does this):
	# Don't need name in the index
	#df_all_names.set_index(['Name'], append=True, inplace=True)
	
	# Export to csv
	csv_all_filename = csv_filename_base + 'AllCandidates.csv'
	df_all_names.to_csv(path_or_buf=csv_all_filename)
	print('df_all_names:\n', df_all_names.to_string())

	# Pickle out:
	df_all_names_pkl = df_all_names.to_pickle('/home/dp/Documents/Campaign/pickle/df_all_names.pkl')
	
	driver.quit()

	return dygraph_elements_list


def PlotWebMetrics(datepoints_start_list, datepoints_end_list):
	df = pd.read_pickle('/home/dp/Documents/Campaign/pickle/df_all_names.pkl')
	# df.reset_index(inplace=True)
	# df.set_index('Date', inplace=True)
	# df.sort_index(inplace=True)
	df.reset_index(inplace=True)
	#rint('df:\n', df.to_string())
	
	plt.close()

	# Dropping Donald Trump from df:
	df_no_dt_index = df[df['Name']=='realDonaldTrump'].index
	df.drop(df_no_dt_index, inplace=True)
	print('***************************************df:\n', df.to_string())

	# # Line plots
	# cols = [col for col in df.columns if col != 'Name' and col != 'Date']
	# print('cols:\n', cols)
	# for title in cols:
	# 	fig, ax = plt.subplots(figsize=(8,6))
	# 	for label, d in df.groupby('Name'):
	# 		d.plot(x='Date', y=title, kind='line', ax=ax, label=label, title=title)
	# 	plt.legend(); plt.xlabel('Date'); plt.ylabel(title)
	# 	plt.savefig('TwitterMetrics '+title, bbox_inches='tight')

	# # Boxplot of Daily Followers Gained:
	# df.boxplot(column='Daily Followers Gained', by='Name')#; plt.xlabel('Date'); plt.ylabel('Daily Followers Gained')
	# plt.xticks(rotation='vertical'); plt.ylabel('Daily Followers Gained')
	# plt.savefig('TwitterMetrics Daily Followers Gained Boxplot', bbox_inches='tight')
	# plt.show()

	''' Plotting % Growth: '''
	# convert timedelta_str to timedelta object
	# subtract timedelta from current date
	# get all data from df['Total Follower Count'].loc[start_date:end_date] grouped by name
	# plot bar plot
	
	# Creating list of previous dates to calculate percent growth time period:
	dates_start_list = [datetime.datetime.strptime(date_str, '%Y,%m,%d') for date_str in datepoints_start_list]
	date_start_objects_list = [pd.Timestamp(d) for d in dates_start_list]
	print('date_start_objects_list:\n', date_start_objects_list)
	dates_end_list = [datetime.datetime.strptime(date_str, '%Y,%m,%d') for date_str in datepoints_end_list]
	date_end_objects_list = [pd.Timestamp(d) for d in dates_end_list]
	print('date_end_objects_list:\n', date_end_objects_list)

	# In this loop, date_end_objects_list and date_start_objects_list[0]
	# are used to select data at two timepoints and calculate percent growth.
	# Variable of interest is pcnt growth in total followers gained.
	# Example end date - start date = 2019-3-8 - 2019-3-1
	df_all_pcnt_growth = pd.DataFrame()
	i_list = list(range(0,len(date_start_objects_list)))
	for i, start, end in zip(i_list, date_start_objects_list, date_end_objects_list):
		# Creating a dataframe groupby object  (won't print, not a dataframe) with embedded groups,
		# need to iterate through it.
		col_of_interest = 'Total Follower Count'
		df_grouped = df[['Date','Name',col_of_interest]].groupby('Name')
		print('df_grouped:\n', df_grouped)

		''' Need to drop rows to get only the start and end of each time period's
			data for each candidate for the column 'Daily Followers Gained'.
			The process is:
			1) Create an index object of all rows that match the start or the end
			   time are found and then their indices stored.
			2) Use the index object to drop those indices from the dataframe. '''
		# 1) Creates an index object:
		df_grouped_ind_to_drop = df[(df['Date']!=start) & (df['Date']!=end)].index
		print('df_grouped_ind_to_drop:\n', df_grouped_ind_to_drop)
		# 2) Drops the rows (using chain indexing, can I avoid this?)
		df_grouped_dropped = df.drop(df_grouped_ind_to_drop)[['Name',col_of_interest]]# for df in df_grouped]
		print('df grouped dropped:\n', df_grouped_dropped.to_string())

		''' As an exercise, the above will be repeated, but instead of creating an
			index object, it should be possible to use the critera for selecting
			the data and selecting the data itself in one step (no need to create 
			an index object and then delete indices):
			1) Select dataframe based on logical critera (using chain indexing, can I avoid this?) '''
		df_start = df[(df['Date']==start)][['Name',col_of_interest]]
		df_end = df[df['Date']==end][['Name',col_of_interest]]
		df_start.set_index('Name', inplace=True)
		df_end.set_index('Name', inplace=True)
		print('df_start:\n', df_start.to_string())
		print('df_end:\n', df_end.to_string())

		# Calculate percent growth by subtracting start time from end time
		# dataframe, dividing by the start time dataframe, multiply by 100
		df_pcnt_growth = ((df_end - df_start) / df_start)*100
		print('df_pcnt_growth:\n', df_pcnt_growth)

		if i == 0:
			df_all_pcnt_growth = df_all_pcnt_growth.append(df_pcnt_growth)
		else:
			df_all_pcnt_growth = pd.concat((df_all_pcnt_growth,df_pcnt_growth), axis=1, sort=True)

	# [NEEDS TO BE FIXED] THESE NAMES NEED TO BE DERIVED FROM WebMetrics() 
	# ABOVE. DOING MANUAL CORRECTION HERE:
	last_name_list = []
	for name in df_all_pcnt_growth.index:
		if name == 'AndrewYang':
			last_name_list.append('Yang')
		elif name == 'joebiden':
			last_name_list.append('Biden')
		elif name == 'TulsiGabbard':
			last_name_list.append('Gabbard')
		elif name == 'BernieSanders':
			last_name_list.append('Sanders')
		elif name == 'ewarren':
			last_name_list.append('Warren')
		elif name == 'BetoORourke':
			last_name_list.append('ORourke')
		elif name == 'CoryBooker':
			last_name_list.append('Booker')
		elif name == 'PeteButtigieg':
			last_name_list.append('PeteButtigieg')
		elif name == 'amyklobuchar':
			last_name_list.append('Klobuchar')

	print('last_name_list:\n', last_name_list)
	df_all_pcnt_growth.index = last_name_list

	# Making legend date ranges for pandas bar plot, e.g. 'Mar 1 - Mar 8'
	start_str_list = [datetime.datetime.strftime(d, '%b %d') for d in date_start_objects_list]
	end_str_list = [datetime.datetime.strftime(d, '%b %d %Y') for d in date_end_objects_list]
	print('start_str_list:\n', start_str_list)
	print('end_str_list:\n', end_str_list)
	start_end_str_list = [s+' - '+e for s,e in zip(start_str_list, end_str_list)]

	df_all_pcnt_growth.columns = start_end_str_list
	print('df_all_pcnt_growth:\n', df_all_pcnt_growth.to_string())

		# Zip through the dataframe adding 1 to each element, returns
		# a numpy array into a dataframe for you.
		# def my_compute(x):
	 #    	return x + 1
		# """ Use enumerate function to iterate"""
	 #    b = np.empty(len(dataset))
	 #    for i, (x) in enumerate(zip(df[col_of_interest])):
	 #        b[i] = my_compute(x[0])
	 #    dataset['b'] = b
	
	plt.close()
	label = df_pcnt_growth.index
	title = col_of_interest
	ind = df_pcnt_growth.index
	fig, ax = plt.subplots(figsize=(6,6))
	ax = df_all_pcnt_growth.plot.bar(title=title, rot=45)#x=ind, y=col_of_interest, label=label, title=title)
	plt.xlabel('Candidates'); plt.ylabel('% Growth')
	plt.savefig('TwitterMetrics - % Growth.png', bbox_inches='tight')
	plt.show()

	return ax
		
		# # Filtering: unfiltered_name_list contains candidate names and instances of 'green' and 'red'
		# unfiltered_name_list = [s.replace('https://electionbettingodds.com/','').replace('.png','') for s in img_elements_list if '/' in s]
		# name_list = [i for i in unfiltered_name_list if 'red' not in i and 'green' not in i]
		# # print('name_list:\n', name_list)

		# #--- Getting betting percentiles:
		# bet_percentiles = driver.find_elements_by_xpath("//p[@style='font-size: 55pt; margin-bottom:-10px']")
		# pcnt_list = [float(pcnt.get_attribute('innerHTML').replace('%','')) for pcnt in bet_percentiles]





''' ----------------------------------------- DonorCounter() ----------------------------------------- '''

# ''' Initialize donor dict and dataframe. Only do once. '''
# donor_dict = {	'time':[],
# 				'donor_count':[],
# 				'donor_goal':[],
# 				'donor_percent':[]}
# df = pd.DataFrame(data=donor_dict, columns=['Time','Count','Goal','Pcnt'])
# ''' -------------------------------------------------- '''


''' --- Run DonorCounter() --- '''
#df = DonorCounter()
''' -------------------------- '''


''' --- Scheduling the DonorCounter() data collection: --- '''
''' --- Uncomment to schedule DonorCounter(), specify time --- '''
# Seconds can be replaced with minutes, hours, or days
# sched.start()
# sched.add_job(DonorCounter, 'interval', seconds=3)
# while True:
#     time.sleep(1)
# sched.shutdown()



''' ----------------------------------------- CampaignBetting() ----------------------------------------- '''

''' --- Initialize dem, rep, and pres dictionaries and dataframes. --- '''
''' Only do once. Not sure if this code is doing anything '''
# dem_dict = {}; rep_dict = {}; pres_dict = {}; 
# df_dem = pd.DataFrame([]); df_rep = pd.DataFrame([]); df_pres = pd.DataFrame([])
# df_dem_field = pd.DataFrame([]); df_rep_field = pd.DataFrame([]); df_pres_field = pd.DataFrame([])
''' ------------------------------------------------------------------ '''

''' --- Run CampaignBetting() --- '''
#df_dem, df_rep, df_pres, df_dem_field, df_rep_field, df_pres_field = CampaignBetting()
''' --------------------------- '''


''' ----------------------------------------- WebMetrics() ----------------------------------------- '''

''' --- Run CampaignBetting() --- '''
# df_all = WebMetrics()
PlotWebMetrics(['2019,3,1','2019,3,8','2019,3,15','2019,3,22'],['2019,3,8','2019,3,15','2019,3,22','2019,3,25'])
''' ----------------------------- '''