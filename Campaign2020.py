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
	#
	# Javascript total tweets from socialblade:
	# 
	# <script type="text/javascript">
		# g = new Dygraph(

		# // containing div
		# document.getElementById('TotalTweetsGained'),
		# // CSV or path to a CSV file.
		# 	"Date,Total Tweets\n" + "2018-02-13,1611\n" +"2018-02-14,1630\n" +"2018-02-15,1640\n" +"2018-02-16,1643\n" +"2018-02-17,1653\n" +"2018-02-18,1661\n" +"2018-02-19,1665\n" +"2018-02-20,1669\n" +"2018-02-21,1673\n" +"2018-02-22,1676\n" +"2018-02-23,1677\n" +"2018-02-24,1681\n" +"2018-02-25,1683\n" +"2018-02-26,1684\n" +"2018-02-27,1684\n" +"2018-02-28,1689\n" +"2018-03-01,1697\n" +"2018-03-02,1708\n" +"2018-03-03,1716\n" +"2018-03-04,1726\n" +"2018-03-05,1728\n" +"2018-03-06,1735\n" +"2018-03-07,1742\n" +"2018-03-08,1745\n" +"2018-03-09,1751\n" +"2018-03-10,1753\n" +"2018-03-11,1756\n" +"2018-03-12,1758\n" +"2018-03-13,1764\n" +"2018-03-14,1764\n" +"2018-03-15,1770\n" +"2018-03-16,1771\n" +"2018-03-17,1779\n" +"2018-03-18,1780\n" +"2018-03-19,1793\n" +"2018-03-20,1800\n" +"2018-03-21,1809\n" +"2018-03-22,1814\n" +"2018-03-23,1815\n" +"2018-03-24,1820\n" +"2018-03-25,1826\n" +"2018-03-26,1829\n" +"2018-03-27,1831\n" +"2018-03-28,1837\n" +"2018-03-29,1846\n" +"2018-03-30,1854\n" +"2018-03-31,1856\n" +"2018-04-01,1860\n" +"2018-04-02,1861\n" +"2018-04-03,1873\n" +"2018-04-04,1888\n" +"2018-04-05,1898\n" +"2018-04-06,1904\n" +"2018-04-07,1911\n" +"2018-04-08,1922\n" +"2018-04-09,1923\n" +"2018-04-10,1924\n" +"2018-04-11,1928\n" +"2018-04-12,1931\n" +"2018-04-13,1946\n" +"2018-04-14,1949\n" +"2018-04-15,1950\n" +"2018-04-16,1951\n" +"2018-04-17,1953\n" +"2018-04-18,1960\n" +"2018-04-19,1965\n" +"2018-04-20,1982\n" +"2018-04-21,1988\n" +"2018-04-22,1988\n" +"2018-04-23,1995\n" +"2018-04-24,1997\n" +"2018-04-25,2010\n" +"2018-04-27,2021\n" +"2018-04-28,2025\n" +"2018-04-29,2032\n" +"2018-04-30,2038\n" +"2018-05-01,2048\n" +"2018-05-02,2066\n" +"2018-05-03,2068\n" +"2018-05-04,2071\n" +"2018-05-05,2072\n" +"2018-05-06,2076\n" +"2018-05-07,2082\n" +"2018-05-08,2087\n" +"2018-05-09,2089\n" +"2018-05-11,2096\n" +"2018-05-12,2102\n" +"2018-05-13,2107\n" +"2018-05-14,2113\n" +"2018-05-15,2124\n" +"2018-05-16,2129\n" +"2018-05-17,2135\n" +"2018-05-18,2138\n" +"2018-05-19,2138\n" +"2018-05-20,2139\n" +"2018-05-21,2150\n" +"2018-05-22,2156\n" +"2018-05-23,2165\n" +"2018-05-24,2170\n" +"2018-05-25,2175\n" +"2018-05-26,2183\n" +"2018-05-27,2186\n" +"2018-05-28,2196\n" +"2018-05-29,2201\n" +"2018-05-30,2207\n" +"2018-05-31,2219\n" +"2018-06-01,2225\n" +"2018-06-02,2235\n" +"2018-06-03,2238\n" +"2018-06-04,2249\n" +"2018-06-05,2257\n" +"2018-06-06,2257\n" +"2018-06-07,2271\n" +"2018-06-08,2277\n" +"2018-06-09,2284\n" +"2018-06-10,2297\n" +"2018-06-11,2306\n" +"2018-06-12,2320\n" +"2018-06-13,2327\n" +"2018-06-14,2342\n" +"2018-06-15,2356\n" +"2018-06-16,2358\n" +"2018-06-17,2363\n" +"2018-06-18,2368\n" +"2018-06-19,2410\n" +"2018-06-20,2433\n" +"2018-06-21,2436\n" +"2018-06-22,2450\n" +"2018-06-23,2478\n" +"2018-06-24,2489\n" +"2018-06-25,2495\n" +"2018-06-26,2511\n" +"2018-06-27,2528\n" +"2018-06-28,2540\n" +"2018-06-29,2566\n" +"2018-06-30,2593\n" +"2018-07-01,2608\n" +"2018-07-02,2618\n" +"2018-07-03,2653\n" +"2018-07-04,2662\n" +"2018-07-05,2670\n" +"2018-07-06,2681\n" +"2018-07-07,2692\n" +"2018-07-08,2699\n" +"2018-07-09,2714\n" +"2018-07-10,2728\n" +"2018-07-11,2740\n" +"2018-07-12,2750\n" +"2018-07-13,2759\n" +"2018-07-14,2763\n" +"2018-07-15,2772\n" +"2018-07-16,2775\n" +"2018-07-17,2783\n" +"2018-07-18,2787\n" +"2018-07-19,2793\n" +"2018-07-20,2801\n" +"2018-07-21,2813\n" +"2018-07-22,2816\n" +"2018-07-23,2820\n" +"2018-07-24,2837\n" +"2018-07-25,2846\n" +"2018-07-26,2856\n" +"2018-07-27,2869\n" +"2018-07-28,2874\n" +"2018-07-29,2883\n" +"2018-07-30,2885\n" +"2018-07-31,2903\n" +"2018-08-01,2918\n" +"2018-08-02,2923\n" +"2018-08-03,2931\n" +"2018-08-04,2935\n" +"2018-08-05,2943\n" +"2018-08-06,2951\n" +"2018-08-07,2953\n" +"2018-08-08,2961\n" +"2018-08-09,2975\n" +"2018-08-10,2987\n" +"2018-08-11,2998\n" +"2018-08-12,3007\n" +"2018-08-13,3022\n" +"2018-08-14,3029\n" +"2018-08-15,3033\n" +"2018-08-16,3041\n" +"2018-08-17,3049\n" +"2018-08-18,3058\n" +"2018-08-19,3065\n" +"2018-08-20,3078\n" +"2018-08-21,3110\n" +"2018-08-22,3121\n" +"2018-08-23,3138\n" +"2018-08-24,3146\n" +"2018-08-25,3149\n" +"2018-08-26,3152\n" +"2018-08-27,3184\n" +"2018-08-28,3189\n" +"2018-08-29,3201\n" +"2018-08-30,3212\n" +"2018-08-31,3228\n" +"2018-09-01,3241\n" +"2018-09-02,3250\n" +"2018-09-03,3262\n" +"2018-09-04,3278\n" +"2018-09-05,3296\n" +"2018-09-06,3321\n" +"2018-09-07,3331\n" +"2018-09-08,3345\n" +"2018-09-09,3353\n" +"2018-09-10,3359\n" +"2018-09-11,3367\n" +"2018-09-12,3373\n" +"2018-09-13,3385\n" +"2018-09-14,3393\n" +"2018-09-15,3418\n" +"2018-09-16,3438\n" +"2018-09-17,3450\n" +"2018-09-18,3459\n" +"2018-09-19,3475\n" +"2018-09-20,3519\n" +"2018-09-21,3543\n" +"2018-09-22,3559\n" +"2018-09-23,3566\n" +"2018-09-24,3582\n" +"2018-09-25,3602\n" +"2018-09-26,3619\n" +"2018-09-27,3627\n" +"2018-09-28,3638\n" +"2018-09-29,3647\n" +"2018-09-30,3651\n" +"2018-10-01,3659\n" +"2018-10-02,3670\n" +"2018-10-03,3698\n" +"2018-10-04,3711\n" +"2018-10-05,3717\n" +"2018-10-06,3733\n" +"2018-10-11,3786\n" +"2018-10-14,3826\n" +"2018-10-15,3845\n" +"2018-10-16,3848\n" +"2018-10-17,3851\n" +"2018-10-18,3851\n" +"2018-10-19,3851\n" +"2018-10-20,3857\n" +"2018-10-21,3864\n" +"2018-10-22,3884\n" +"2018-10-23,3892\n" +"2018-10-25,3920\n" +"2018-10-26,3947\n" +"2018-10-27,3948\n" +"2018-10-28,3973\n" +"2018-10-29,3999\n" +"2018-11-02,4016\n" +"2018-11-03,4018\n" +"2018-11-04,4020\n" +"2018-11-05,4025\n" +"2018-11-06,4044\n" +"2018-11-07,4054\n" +"2018-11-08,4066\n" +"2018-11-09,4071\n" +"2018-11-11,4101\n" +"2018-11-12,4116\n" +"2018-11-13,4122\n" +"2018-11-14,4134\n" +"2018-11-15,4147\n" +"2018-11-16,4166\n" +"2018-11-17,4178\n" +"2018-11-18,4182\n" +"2018-11-19,4191\n" +"2018-11-20,4205\n" +"2018-11-21,4220\n" +"2018-11-22,4234\n" +"2018-11-23,4239\n" +"2018-11-24,4250\n" +"2018-11-26,4263\n" +"2018-12-01,4322\n" +"2018-12-02,4324\n" +"2018-12-03,4328\n" +"2018-12-04,4338\n" +"2018-12-05,4347\n" +"2018-12-06,4360\n" +"2018-12-07,4373\n" +"2018-12-08,4384\n" +"2018-12-09,4390\n" +"2018-12-10,4395\n" +"2018-12-11,4405\n" +"2018-12-12,4409\n" +"2018-12-13,4425\n" +"2018-12-14,4437\n" +"2018-12-15,4451\n" +"2018-12-16,4464\n" +"2018-12-17,4470\n" +"2018-12-18,4487\n" +"2018-12-19,4502\n" +"2018-12-20,4512\n" +"2018-12-21,4530\n" +"2018-12-22,4541\n" +"2018-12-23,4555\n" +"2018-12-24,4566\n" +"2018-12-25,4573\n" +"2018-12-26,4584\n" +"2018-12-27,4596\n" +"2018-12-28,4612\n" +"2018-12-29,4621\n" +"2018-12-30,4630\n" +"2018-12-31,4634\n" +"2019-01-01,4641\n" +"2019-01-02,4649\n" +"2019-01-03,4665\n" +"2019-01-04,4671\n" +"2019-01-05,4678\n" +"2019-01-06,4690\n" +"2019-01-07,4697\n" +"2019-01-08,4716\n" +"2019-01-09,4728\n" +"2019-01-10,4752\n" +"2019-01-11,4779\n" +"2019-01-12,4794\n" +"2019-01-13,4787\n" +"2019-01-14,4811\n" +"2019-01-15,4829\n" +"2019-01-16,4857\n" +"2019-01-17,4868\n" +"2019-01-18,4883\n" +"2019-01-19,4911\n" +"2019-01-20,4924\n" +"2019-01-21,4933\n" +"2019-01-22,4951\n" +"2019-01-23,4959\n" +"2019-01-24,4976\n" +"2019-01-25,4994\n" +"2019-01-26,5012\n" +"2019-01-27,5028\n" +"2019-01-28,5045\n" +"2019-01-29,5071\n" +"2019-01-30,5087\n" +"2019-01-31,5116\n" +"2019-02-01,5129\n" +"2019-02-02,5152\n" +"2019-02-03,5172\n" +"2019-02-04,5185\n" +"2019-02-05,5199\n" +"2019-02-06,5221\n" +"2019-02-07,5236\n" +"2019-02-10,5268\n" +"2019-02-11,5281\n" +"2019-02-12,5299\n" +"2019-02-13,5319\n" +"2019-02-14,5362\n" +"2019-02-15,5393\n" +"2019-02-16,5478\n" +"2019-02-17,5515\n" +"2019-02-18,5540\n" +"2019-02-19,5597\n" +"2019-02-20,5622\n" +"2019-02-21,5668\n" +"2019-02-22,5697\n" +"2019-02-23,5728\n" +"2019-02-24,5757\n" +"2019-02-25,5787\n" +"2019-02-26,5820\n" +"2019-02-28,5896\n" +"2019-03-01,5920\n" +"2019-03-02,5942\n" +"2019-03-03,5987\n" +"2019-03-04,5989\n" +"2019-03-05,6018\n" +"2019-03-06,6048\n" +"2019-03-07,6085\n" +"2019-03-08,6122\n" +"2019-03-09,6183\n" +"2019-03-10,6272\n" +"2019-03-11,6345\n" +"2019-03-12,6432\n" +"2019-03-13,6479\n" +"2019-03-14,6532\n" +"2019-03-15,6617\n" +"2019-03-16,6640\n" +"2019-03-17,6689\n" +"2019-03-18,6710\n" +"2019-03-19,6730\n" +"2019-03-20,6733\n" +"2019-03-21,6757\n" +"2019-03-22,6770\n" +"2019-03-23,6795\n" , {
		# 		title: 'Total Tweets Posted for AndrewYang',
		# 		legend: 'always',
		# 		ylabel: false,
		# 		titleHeight: 20,
		# 		labelsDivStyles: { 'background': 'none', 'margin-top': '-10px', 'text-align': 'right', },
		# 		strokeWidth: 1,
		# 		colors: ["#dd2323", "#dd2323", "#dd2323", "#dd2323"],
		# 		labelsKMB: true,
		# 		maxNumberWidth: 10
		# 	}
		# );
		# </script>

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
					dygraph_str = dygraph_str[dygraph_str.index('\\n" + "'):dygraph_str.rindex('\\n" ')]#-8]
					dygraph_str = dygraph_str.replace('\\n" + "','').replace('\\n" +"',',').replace('\\n" ','')
					dygraph_str = dygraph_str.split(',')
					#dygraph_str.replace(',','","')
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

	# Adding the 'Name' column to the index (append does this):
	df_all_names.set_index(['Name'], append=True, inplace=True)

	print('df_all_names:\n', df_all_names.to_string())

	# Pickle out:
    df_all_names_pkl = df_all_names.to_pickle('/home/dp/Documents/Campaign/pickle/df_all_names.pkl')

	driver.quit()
	return dygraph_elements_list

def PlotWebMetrics():
	df = pd.read_pickle('/home/dp/Documents/Campaign/pickle/df_all_names.pkl')
	# Plotting:
	plt.figure()
	plt.plot(df.index, df['Daily Followers Gained'], linewidth=2, marker='o', markersize=3, markerfacecolor='white')
	plt.show()

	plt.figure()
	plt.plot(df.index, df['Total Follower Count'], linewidth=2, marker='o', markersize=3, markerfacecolor='white', markeredgecolor='red')
	plt.show()

	return
		
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
df_all = WebMetrics()
PlotWebMetrics()
''' ----------------------------- '''