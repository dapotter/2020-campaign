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

	# # Writing fields to csv to notify if political field changes
	# cols = list(range(0,len(dem_fields)))
	# with open('RaceFieldsDem.csv','w') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(cols)
	# 	writer.writerow(dem_fields)
	# with open('RaceFieldsRep.csv','w') as f:
	# 	writer = csv.writer(f)
	# 	writer.writerow(cols)
	# 	writer.writerow(rep_fields)
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
	if any(df_dem_field.iloc[-1] != dem_fields):
		print('!!!!!!!!!!!!!!!!!!!!!!! Dem field has changed')
	if any(df_rep.columns != rep_fields):
		print('!!!!!!!!!!!!!!!!!!!!!!! Rep field has changed')
	if any(df_pres.columns != pres_fields):
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
	df_pres_top8_no_time = df_pres_no_time.sort_values(axis=0)

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
df_dem, df_rep, df_pres, df_dem_field, df_rep_field, df_pres_field = CampaignBetting()
''' --------------------------- '''