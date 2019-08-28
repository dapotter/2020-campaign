# Operating this script in Conda environment 'fwp_venv'
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import seaborn as sns
register_matplotlib_converters()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

import glob
import os

import psycopg2

sched = BackgroundScheduler()

# # Create original dataframe once:
# def YangDonorCounter():
# 	#global df

# 	driver = webdriver.Chrome('/usr/bin/chromedriver')
# 	# This doesn't allow the donor count to update: driver.minimize_window()
# 	driver.set_window_size(0, 0)
# 	driver.set_window_position(0,0)
# 	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
# 	url = 'https://www.yang2020.com/'
# 	driver.get(url)
# 	time.sleep(3) # Allow the user see website load
# 	donor_count_str = driver.find_element_by_class_name('donor-count-number').text
# 	donor_goal_str = driver.find_element_by_css_selector('.total.goal').text
# 	donor_count = int(float(donor_count_str.replace(',','')))
# 	donor_goal = int(float(donor_goal_str.replace(',','')))
# 	donor_pcnt = (donor_count / donor_goal)*100
# 	current_time = datetime.datetime.now()

# 	print('donor_count:', donor_count)
# 	print('donor_goal:', donor_goal)
# 	print('donor_pcnt:', donor_pcnt)
# 	print('current_time:', current_time)

# 	donor_arr = [current_time, donor_count, donor_goal, donor_pcnt]

# 	fields=['Time','Count','Goal', 'Pcnt']
# 	donor_dict = {'Time':current_time,'Count':donor_count,'Goal':donor_goal, 'Pcnt':donor_pcnt}
# 	print('donor_dict:\n', donor_dict)

# 	#df = df.append(donor_dict, ignore_index=True)

# 	''' Creates csv, overwrites the current one of the same name: '''
# 	# with open('DonorCountYang.csv','w') as f:
# 	#     writer = csv.DictWriter(f, fieldnames=fields)
# 	#     writer.writerow(donor_dict)

# 	''' Appends the csv '''
# 	with open(r'DonorCountYang.csv', 'a', newline='') as f:
# 	    writer = csv.DictWriter(f, fieldnames=fields)
# 	    writer.writerow(donor_dict)

# 	# Close driver:
# 	driver.quit()

# 	# Read csv into dataframe:
# 	df = pd.read_csv('DonorCountYang.csv')
# 	print('df head:\n', df.head)
# 	# Format Time column
# 	df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
# 	# Check formatting:
# 	#print('time type:\n', type(df.iloc[0]['Time']))

# 	# Calculate donor growth rate:
# 	x = mdates.date2num(df.Time.values) # Time values converted to floats
# 	print('Time values converted to numbers:\n', x)
# 	y = df['Count'].values # Counts
# 	growth_rate = np.gradient(y,x)
# 	df['Rate'] = growth_rate

# 	print('Donor Count df:\n', df.to_string())

# 	# Pickle out:
# 	DonorCountYang_df_pkl = df.to_pickle('/home/dp/Documents/Campaign/pickle/DonorCountYang_df.pkl')

# 	# ''' Make projection for 200,000 donors '''
# 	# Data from Time and Count column for 7 days prior to the current date
# 	# Fit line to Count vs Time data.
# 	# Plug 200,000 into y-value, solve for x (date)
# 	# Put date value into plot: 'Projected 200,000 donors'

# 	current_time = datetime.datetime.now()
# 	print('current time:', current_time)
# 	one_wk_timedelta = datetime.timedelta(days=7)
# 	one_mnth_timedelta = datetime.timedelta(days=30)
# 	print('one_wk_timedelta:', one_wk_timedelta)
# 	one_wk_prior_time = current_time - one_wk_timedelta
# 	one_mnth_prior_time = current_time - one_mnth_timedelta
# 	print('one_wk_prior_time:', one_wk_prior_time)
	
	
# 	df['Time'] = pd.to_datetime(df['Time'])
# 	df.set_index('Time', inplace=True)
# 	df_7_days = df.loc[one_wk_prior_time:current_time]
# 	df_30_days = df.loc[one_mnth_prior_time:current_time]
# 	print('df_7_days:\n', df_7_days)

# 	# mask = (df['Time'] >= one_wk_prior_time) & (df['Time'] <= current_time)
# 	# df_7_days = df.loc[mask]
# 	# print('df_7_days:\n', df_7_days)
# 	dates_float_7_days = mdates.date2num(df_7_days.index)
# 	dates_float_30_days = mdates.date2num(df_30_days.index)
# 	print('dates_float:\n', dates_float_7_days)

# 	count_7_days = df_7_days.loc[:,'Count']
# 	count_30_days = df_30_days.loc[:,'Count']
# 	print('df_7_days.loc[:,"Count"]:\n', df_7_days.loc[:,'Count'])

# 	pfit_7_days = np.polyfit(x=dates_float_7_days, y=count_7_days, deg=1)
# 	linfit_7_days = np.poly1d(pfit_7_days)
# 	pfit_30_days = np.polyfit(x=dates_float_30_days, y=count_30_days, deg=1)
# 	linfit_30_days = np.poly1d(pfit_30_days)

# 	#df.reset_index(inplace=True)
# 	df_7_days['Trendline 1 Week'] = linfit_7_days(dates_float_7_days)
# 	df_30_days['Trendline 1 Month'] = linfit_30_days(dates_float_30_days)
# 	print('df_7_days with Trendline:\n', df_7_days)

# 	# 200k donor prediction date:
# 	start_date = current_time
# 	# date_step = datetime.timedelta(days=7)
# 	projected_dates = [datetime.timedelta(days=day)+current_time for day in list(range(1,800))]
# 	projected_dates_float = mdates.date2num(projected_dates)
# 	projected_donor_count_7_days = linfit_7_days(projected_dates_float)
# 	projected_donor_count_30_days = linfit_30_days(projected_dates_float)

# 	# print('projected_dates:', projected_dates)
# 	# print('projected_donor_count:\n', projected_donor_count)
# 	print('shape projected_donor_count_7_days:\n', np.shape(projected_donor_count_7_days))
# 	projected_datetime_200k_7_days = projected_dates[np.flatnonzero(projected_donor_count_7_days > 200000)[0]] # np.where also works but returns a 1-element tuple
# 	# SOMETIMES THE CODE ERRORS HERE. THIS IS THE RESULT OF THE PROJECTION NEVER REACHING 200,000
# 	# DONORS BECAUSE THE RATE OF GROWTH IS TOO LOW. TO FIX: IN list(range(1,X)) ABOVE, MAKE X
# 	# BIGGER UNTIL ERROR GOES AWAY. X IS THE NUMBER OF TIMESTEPS INTO THE FUTURE TO PROJECT.
# 	projected_date_200k_7_days = projected_datetime_200k_7_days.strftime('%b %d, %Y')
# 	print('projected_date_200k_7_days:', projected_date_200k_7_days)
# 	projected_datetime_200k_30_days = projected_dates[np.flatnonzero(projected_donor_count_30_days > 200000)[0]] # np.where also works but returns a 1-element tuple
# 	projected_date_200k_30_days = projected_datetime_200k_30_days.strftime('%b %d, %Y')

# 	# ''' Plotting data: '''
# 	#fig = plt.figure()
# 	w = 3
# 	h = 3
# 	#fig = plt.figure(frameon=False)
# 	#fig.set_size_inches(w,h)
# 	f, ax1 = plt.subplots(figsize=(8,8))
# 	ax2 = ax1.twinx()
# 	ax1.plot(df.index, df['Count'], linewidth=1, color='k', marker='o', markersize=3, markerfacecolor='none', markeredgecolor='k')
# 	ax1.plot(df_7_days.index, df_7_days['Trendline 1 Week'], color='r')
# 	ax1.plot(df_30_days.index, df_30_days['Trendline 1 Month'], color='#b2b74e')
# 	ax2.plot(df.index, df['Rate'], linewidth=1, color='#4b7a46', marker='^', markersize=3, markerfacecolor='none', markeredgecolor='#4b7a46')
# 	ax1.set_xlabel('DateTime', color='k')
# 	ax1.set_ylabel('Number of donors', color='k')
# 	ax1.tick_params('y', colors='k')
# 	ax1.legend(labels=['Donor count','7-day trend','30-day trend'])
# 	ax2.set_ylabel('Donors/Day', color='#4b7a46')
# 	ax2.tick_params('y', colors='#4b7a46')
# 	ax2.legend(labels=['Donor growth'])
# 	f.autofmt_xdate()
# 	plt.title('200k donors projected date: {0} or {1}'.format(projected_date_200k_7_days, projected_date_200k_30_days))
# 	plt.savefig('DonorCountYang.png', bbox_inches='tight')
# 	plt.show()

# 	# ''' --------------- '''

# 	# ''' try-except isn't necessary unless webpage won't load '''
# 	#
# 	# try:
# 	# 	element_present = EC.presence_of_element_located((By.CLASS_NAME, 'donor-count-number'))
# 	# 	WebDriverWait(driver, timeout).until(element_present)
# 	# 	donor_count_3 = driver.find_element_by_class_name('donor-count-number')
# 	# 	print('donor_count_3:\n', donor_count_3.text)
# 	# except TimeoutException:
# 	# 	print("Timed out waiting for page to load")

# 	return


''' ----------------------------------------------------------------------------------------------- '''


# Create original dataframe once:
def YangMoneyRaised():
	#global df

	driver = webdriver.Chrome('/usr/bin/chromedriver')
	# This doesn't allow the donor count to update: driver.minimize_window()
	driver.set_window_size(0, 0)
	driver.set_window_position(0,0)
	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
	url = 'https://www.yang2020.com/'
	driver.get(url)
	time.sleep(15) # Allow the user see website load
	
	# money_count_str = driver.find_element_by_class_name('donor-count-number').text
	money_count_str = driver.find_element_by_class_name('yang-progress').text
	money_count_str = money_count_str.replace('$','') # Remove $ symbol
	money_count_str = money_count_str.replace(',','') # Remove ,
	print('money_count_str:\n', money_count_str)
	money_count = int(float(money_count_str))
	
	# # money_goal_str = driver.find_element_by_css_selector('.total.goal').text
	# money_goal_str = driver.find_element_by_class_name('yang-progress').text
	# money_goal_str = money_goal_str.replace('$','') # Remove $ symbol
	# money_goal_str = money_goal_str.replace(',','') # Remove $ symbol
	# money_goal = int(float(money_goal_str))
	money_goal = 5000000
	
	money_pcnt = (money_count / money_goal)
	current_time = datetime.datetime.now()

	print('money_count:', money_count)
	print('money_goal:', money_goal)
	print('money_pcnt:', money_pcnt)
	print('current_time:', current_time)

	money_arr = [current_time, money_count, money_goal, money_pcnt]

	fields=['Time','Count','Goal','Pcnt']
	money_dict = {'Time':current_time,'Count':money_count,'Goal':money_goal, 'Pcnt':money_pcnt}
	print('money_dict:\n', money_dict)


	''' Creates csv, overwrites the current one of the same name: '''
	# df = df.append(money_dict, ignore_index=True) # This does nothing
	# with open('YangMoneyRaised.csv','w') as f:
	#     writer = csv.DictWriter(f, fieldnames=fields)
	#     writer.writerow(money_dict)

	''' Appends the csv '''
	with open(r'YangMoneyRaised.csv', 'a', newline='') as f:
	    writer = csv.DictWriter(f, fieldnames=fields)
	    writer.writerow(money_dict)

	# Close driver:
	driver.quit()

	# Read csv into dataframe:
	df = pd.read_csv('YangMoneyRaised.csv')

	print('df head:\n', df.head)
	# Format Time column
	df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S')
	# Check formatting:
	#print('time type:\n', type(df.iloc[0]['Time']))

	df.set_index('Time', inplace=True)
	df['Q'] = df.index.quarter
	df.reset_index(inplace=True)
	df['Rate'] = np.gradient(df.Count, mdates.date2num(df.Time.values))
	print('df:\n', df)

	print('Dollar Count df:\n', df.to_string())

	# Pickle out:
	df.to_pickle('/home/dp/Documents/Campaign/pickle/YangMoneyRaised_df.pkl')

	# ''' Make projection for 200,000 donors '''
	# Data from Time and Count column for 7 days prior to the current date
	# Fit line to Count vs Time data.
	# Plug 200,000 into y-value, solve for x (date)
	# Put date value into plot: 'Projected 200,000 donors'

	current_time = datetime.datetime.now()
	print('current time:', current_time)
	one_wk_timedelta = datetime.timedelta(days=7)
	one_mnth_timedelta = datetime.timedelta(days=30)
	print('one_wk_timedelta:', one_wk_timedelta)
	one_wk_prior_time = current_time - one_wk_timedelta
	one_mnth_prior_time = current_time - one_mnth_timedelta
	print('one_wk_prior_time:', one_wk_prior_time)
	
	df['Time'] = pd.to_datetime(df['Time'])
	df.set_index('Time', inplace=True)

	df_7_days = df.loc[one_wk_prior_time:current_time]
	df_30_days = df.loc[one_mnth_prior_time:current_time]
	print('df_7_days:\n', df_7_days)

	# mask = (df['Time'] >= one_wk_prior_time) & (df['Time'] <= current_time)
	# df_7_days = df.loc[mask]
	# print('df_7_days:\n', df_7_days)
	dates_float_7_days = mdates.date2num(df_7_days.index)
	dates_float_30_days = mdates.date2num(df_30_days.index)
	print('dates_float:\n', dates_float_7_days)

	count_7_days = df_7_days.loc[:,'Count']
	count_30_days = df_30_days.loc[:,'Count']
	print('df_7_days.loc[:,"Count"]:\n', df_7_days.loc[:,'Count'])

	pfit_7_days = np.polyfit(x=dates_float_7_days, y=count_7_days, deg=1)
	linfit_7_days = np.poly1d(pfit_7_days)
	pfit_30_days = np.polyfit(x=dates_float_30_days, y=count_30_days, deg=1)
	linfit_30_days = np.poly1d(pfit_30_days)

	#df.reset_index(inplace=True)
	df_7_days['Trendline 1 Week'] = linfit_7_days(dates_float_7_days)
	df_30_days['Trendline 1 Month'] = linfit_30_days(dates_float_30_days)
	print('df_7_days with Trendline:\n', df_7_days)

	# -----------------------------------------------------------------------------------------------
	# $3.5 MILLION DONATION LINEAR PROJECTIONS. UNCOMMENT TO USE:
	start_date = current_time
	# date_step = datetime.timedelta(days=7)
	projected_dates = [datetime.timedelta(days=day)+current_time for day in list(range(1,2000))]
	projected_dates_float = mdates.date2num(projected_dates)
	projected_money_count_7_days = linfit_7_days(projected_dates_float)
	projected_money_count_30_days = linfit_30_days(projected_dates_float)

	# print('projected_dates:', projected_dates)
	# print('projected_money_count:\n', projected_money_count)
	print('shape projected_money_count_7_days:\n', np.shape(projected_money_count_7_days))
	projected_datetime_XMil_7_days = projected_dates[np.flatnonzero(projected_money_count_7_days > money_goal)[0]] # np.where also works but returns a 1-element tuple
	# SOMETIMES THE CODE ERRORS HERE. THIS IS THE RESULT OF THE PROJECTION NEVER REACHING $2
	# MILLION BECAUSE THE RATE OF GROWTH IS TOO LOW. TO FIX: IN list(range(1,X)) ABOVE, 
	# LOOK FOR THE LINE DEFINING projected_dates,
	# MAKE X BIGGER UNTIL ERROR GOES AWAY. X IS THE NUMBER OF TIMESTEPS INTO THE FUTURE TO PROJECT.
	projected_date_XMil_7_days = projected_datetime_XMil_7_days.strftime('%b %d, %Y')
	print('projected_date_XMil_7_days:', projected_date_XMil_7_days)
	projected_datetime_XMil_30_days = projected_dates[np.flatnonzero(projected_money_count_30_days > money_goal)[0]] # np.where also works but returns a 1-element tuple
	projected_date_XMil_30_days = projected_datetime_XMil_30_days.strftime('%b %d, %Y')
	# -----------------------------------------------------------------------------------------------

	# ''' Plotting data: '''
	# Second quarter:
	plt.close()
	f, (ax1, ax3) = plt.subplots(1,2, figsize=(12,6))
	ax2 = ax1.twinx()
	df_Q2 = df[ df['Q'] == 2 ]
	ax1.plot(df_Q2.index, df_Q2.Count, linewidth=1, color='k', marker='o', markersize=3, markerfacecolor='none', markeredgecolor='k')
	# ax1.plot(df_7_days.index, df_7_days['Trendline 1 Week'], color='r')
	# ax1.plot(df_30_days.index, df_30_days['Trendline 1 Month'], color='#b2b74e')
	ax2.plot(df_Q2.index, df_Q2.Rate, linewidth=1, color='#4b7a46', marker='d', markersize=3, markerfacecolor='none', markeredgecolor='#4b7a46')
	ax1.set_xlabel('DateTime', color='k')
	ax1.set_ylabel('Money Raised', color='k')
	ax1.tick_params('y', colors='k')
	# ax1.legend(labels=['Dollar count','7-day trend','30-day trend'])
	# ax2.set_ylabel('Dollars/Day', color='#4b7a46')
	ax2.tick_params('y', colors='#4b7a46')
	ax2.legend(labels=['Donations growth'])
	f.autofmt_xdate()
	# ax1.set_title('$3.5 million projected date: {0} or {1}'.format(projected_date_XMil_7_days, projected_date_XMil_30_days))
	ax1.set_title('Q2 Donations and Growth Rate')

	# Third quarter:
	ax4 = ax3.twinx()
	df_Q3 = df[ df['Q'] == 3 ]
	ax3.plot(df_Q3.index, df_Q3.Count, linewidth=1, color='k', marker='o', markersize=3, markerfacecolor='none', markeredgecolor='k')
	ax3.plot(df_7_days.index, df_7_days['Trendline 1 Week'], color='r')
	ax3.plot(df_30_days.index, df_30_days['Trendline 1 Month'], color='#b2b74e')
	ax4.plot(df_Q3.index, df_Q3.Rate, linewidth=1, color='#4b7a46', marker='d', markersize=3, markerfacecolor='none', markeredgecolor='#4b7a46')
	ax3.set_xlabel('DateTime', color='k')
	# ax3.set_ylabel('Money Raised', color='k')
	ax3.tick_params('y', colors='k')
	ax4.set_ylabel('$/Day', color='#4b7a46')
	ax4.tick_params('y', colors='#4b7a46')
	ax4.legend(labels=['Donations growth'])
	f.autofmt_xdate()
	ax3.set_title('${0} million proj.: {1} or {2}'.format(money_goal/1E6, projected_date_XMil_7_days, projected_date_XMil_30_days))

	plt.subplots_adjust(wspace=0.5)
	plt.savefig('YangMoneyRaised.png', bbox_inches='tight')
	plt.show()
	# ''' --------------- '''


	# ''' Plotting Q2 vs Q3: Fundraising Rate: '''
	print('Index duplicates:\n', df[ ~df.index.duplicated()] )
	df_rs = df.resample('D').mean().interpolate(method='linear')
	# df_rs = df
	df_rs.Q = df_rs.index.quarter # Remaking the Q column
	df_rs['Rate'] = np.gradient(df_rs.Count, mdates.date2num(df_rs.index.values))
	
	# Getting rid of data between end of Q2 July 1 2019, and start of Q3 August 2 2019
	# Due to resampling the data on a daily frequency, it filled in all of July for which there is no data
	# Grabbing all data outside of July here:
	df_rs = df_rs[ (df_rs.index < '2019-07-01') | (df_rs.index > '2019-08-02') ]
	print('df_rs:\n', df_rs)
	rate_mean = df_rs.groupby('Q')['Rate'].agg(['mean', 'median'])
	print('rate_mean:\n', rate_mean)
	rate_mean.rename({2:'Q2',3:'Q3'}, axis=0, inplace=True)
	rate_mean.rename({'mean':'Avg', 'median':'Median'}, axis=1, inplace=True)
	print('rate_mean:\n', rate_mean)
	
	# Again, due to resampling, need to redefine second and third quarters
	df_Q2 = df_rs[ df_rs.Q == 2 ]
	df_Q3 = df_rs[ df_rs.Q == 3 ]

	plt.close()
	fig, (ax1, ax2) = plt.subplots(1,2, figsize=(8,3))
	# rate_mean.plot.bar(use_index=True, ax=ax1, color=['#000000', '#757575'])
	sns.barplot(x='Q', y='Rate', data=df_rs, ax=ax1, capsize=0.2, palette=['#000000', '#757575'], alpha=0.7)
	df_Q2.plot(use_index=True, y='Count', ax=ax2, color='#40000c', marker='o', label='Q2', legend=True, alpha=0.5)
	df_Q3.plot(use_index=True, y='Count', ax=ax2, color='#9c001d', marker='o', label='Q3', legend=True, alpha=0.5)
	ax1.set_xlabel('Quarter')
	ax1.set_ylabel('$/Day')
	ax1.set_title('Q2-Q3 Donation Rates')
	ax2.set_ylabel('Donations, $')
	ax2.set_xlabel('Date')
	ax2.set_title('Q2-Q3 Total Donations')
	ax2.legend(loc='upper left')
	plt.subplots_adjust(wspace=0.4)
	plt.savefig('/home/dp/Documents/Campaign/YangMoneyRaised_rate_comparison.png', bbox_inches='tight')
	plt.show()

	# ''' --------------- '''


	# ''' try-except isn't necessary unless webpage won't load '''
	#
	# try:
	# 	element_present = EC.presence_of_element_located((By.CLASS_NAME, 'donor-count-number'))
	# 	WebDriverWait(driver, timeout).until(element_present)
	# 	money_count_3 = driver.find_element_by_class_name('donor-count-number')
	# 	print('money_count_3:\n', money_count_3.text)
	# except TimeoutException:
	# 	print("Timed out waiting for page to load")

	return


''' ----------------------------------------------------------------------------------------------- '''


def FEC():
	# Plots Federal Election Commission's public records of donations to each political candidate
	# Columns: contribution_receipt_date and contribution_receipt_amount

	FEC_files_path = '/home/dp/Documents/Campaign/FEC/'
	FEC_itemized_files = glob.glob(os.path.join(FEC_files_path, '*Itemized.csv')) # H500 file paths in a list

	
	fields = ['committee_name','contribution_receipt_date','contribution_receipt_amount','contributor_aggregate_ytd','contributor_state','contributor_last_name'] # 'contributor_name'
	df_gen = (pd.read_csv(f, header='infer', usecols=fields) for f in FEC_itemized_files)
	df = pd.concat(df_gen, axis=0, sort=True)
	df.drop(labels = df[df['contributor_last_name']=='ActBlue'].index, axis=0, inplace=True)
	print('df:\n', df)

	FEC_contribution_size_files = glob.glob(os.path.join(FEC_files_path, '*ContributionSize.csv')) # H500 file paths in a list
	fields = ['committee_name', 'cycle', 'total', 'count', 'size']
	df_gen = (pd.read_csv(f, header='infer', usecols=fields) for f in FEC_contribution_size_files)
	df_contribution_size = pd.concat(df_gen, axis=0, sort=True)
	df_contribution_size.fillna(0, inplace=True)
	print('df_contribution_size:\n', df_contribution_size)
	df_contribution_size.reset_index(drop=True, inplace=True)
	# Index values where the donor count is 0.0. This happens only for donors < $200
	criteria = df_contribution_size[df_contribution_size['count'] == 0.0].index
	# # Multiply all < $200 donor totals by estimate factor to get an estimate of the < $200 donor count
	# # The estimate factor assumes for donations < $200: 65% are $20, 20% are $50, 10% are $100, 5% are $200
	# estimate_factor = (1/100) #(0.65/20 + 0.2/50 + 0.1/100 + 0.05/200)
	# df_contribution_size['count'].iloc[criteria] = df_contribution_size['total'].iloc[criteria] * estimate_factor
	# print('df_contribution_size with count estimates for donations < $200:\n', df_contribution_size)
	
	# Making a string column based on contribution size, will contain '$0-$199' for 0, '$200-$499' for 200, etc.
	df_contribution_size['range'] = ['0-200' if size==0 else '200-499' if size==200 else '500-999' if size==500 else '1000-1999' if size==1000 else '>2000' for size in df_contribution_size['size']]
	df_contribution_size['range'] = df_contribution_size['range'].apply(str)
	df_contribution_size['total'] = df_contribution_size['total'] / 1E6
	# df_contribution_size.set_index('committee_name', inplace=True)
	# df_contribution_size.sort_values(by='size', inplace=True)
	print('df_contribution_size with donation size ranges:\n', df_contribution_size.to_string())
	df_contribution_size['pcnt'] = df_contribution_size.groupby('committee_name')['total'].apply(lambda x: x/x.sum()*100)
	print('df_contribution_size with donor count percentage:\n', df_contribution_size.to_string())

	# df_below_200_count = df.groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: (x<=200).sum())#.reset_index(name='count')


	# REPLACING COMMITTEE NAMES. NEED TO USE BETTER METHOD.
	# df.replace('DONALD J. TRUMP FOR PRESIDENT, INC.','Trump', inplace=True)
	# df.replace('TRUMP MAKE AMERICA GREAT AGAIN COMMITTEE','Trump (MAGA)', inplace=True)
	# df.replace('TRUMP VICTORY','Trump (Victory)', inplace=True)
	df.replace('ELIZABETH WARREN ACTION FUND','Warren', inplace=True)
	df.replace('WARREN FOR PRESIDENT, INC.','Warren', inplace=True)
	df.replace('BERNIE 2020','Sanders', inplace=True)
	df.replace('FRIENDS OF ANDREW YANG','Yang', inplace=True)
	df.replace('TULSI NOW','Gabbard', inplace=True)
	df.replace('AMY FOR AMERICA','Klobuchar', inplace=True)
	df.replace('BETO FOR AMERICA','ORourke', inplace=True)
	df.replace('JULIAN FOR THE FUTURE','Castro', inplace=True)
	df.replace('PETE FOR AMERICA, INC.','Buttigieg', inplace=True)
	df.replace('CORY 2020','Booker', inplace=True)
	df.replace('KAMALA HARRIS FOR THE PEOPLE','Harris', inplace=True)

	df_contribution_size.replace('ELIZABETH WARREN ACTION FUND','Warren', inplace=True)
	df_contribution_size.replace('WARREN FOR PRESIDENT, INC.','Warren', inplace=True)
	df_contribution_size.replace('BERNIE 2020','Sanders', inplace=True)
	df_contribution_size.replace('FRIENDS OF ANDREW YANG','Yang', inplace=True)
	df_contribution_size.replace('TULSI NOW','Gabbard', inplace=True)
	df_contribution_size.replace('AMY FOR AMERICA','Klobuchar', inplace=True)
	df_contribution_size.replace('BETO FOR AMERICA','ORourke', inplace=True)
	df_contribution_size.replace('JULIAN FOR THE FUTURE','Castro', inplace=True)
	df_contribution_size.replace('PETE FOR AMERICA, INC.','Buttigieg', inplace=True)
	df_contribution_size.replace('CORY 2020','Booker', inplace=True)
	df_contribution_size.replace('KAMALA HARRIS FOR THE PEOPLE','Harris', inplace=True)

	# Write out all data to csv for use in postgres:
	df.to_csv('/home/dp/Documents/Campaign/FEC/FEC.csv')


	# Processing df:
	print('df:\n', df)
	df['contribution_receipt_date'] = pd.to_datetime(df['contribution_receipt_date'])
	print('type(df["contribution_receipt_date"]:', type(df["contribution_receipt_date"].iloc[0]))
	df.set_index(['committee_name', 'contribution_receipt_date'], inplace=True)
	df.sort_index(inplace=True)
	print('df:\n', df)
	# May need to specify committee names in the future: committee_names_list = df.index.get_level_values(0).unique().to_list()
	committee_names_list = ['Sanders', 'Warren', 'Yang'] # 'Trump', 'Trump\n(MAGA)', 'Trump\n(Victory)'
	print('committee_names_list:\n', committee_names_list)

	df.reset_index(inplace=True)


	states = ['OH','MI','WI','PA','FL','CO','IA','MN','NV','NH','NC','VA']
	# ----------------------------------
	# Number of unique donations in each swing state shows each
	# candidate's support in that state.
	df_geo = df[['committee_name','contributor_state','contributor_aggregate_ytd']]
	df_geo.set_index(['committee_name','contributor_state'], inplace=True)
	df_geo_counts = df_geo.groupby(level=['committee_name','contributor_state']).size()
	df_geo_counts.sort_index(inplace=True)
	print(df_geo_counts.index.levels)
	print(df_geo_counts)
	# print(df_geo_counts.iloc[df_geo_counts.index.get_level_values('contributor_state') == 'OH']) #,'PA','MI','WI','FL']])
	df_geo_counts = df_geo_counts.loc[(slice(None)), states]
	# Ohio only: df_geo_counts = df_geo_counts.loc[(slice(None), 'OH')]
	# df_geo_counts.sort_values(inplace=True)

	# Rank all candidates for each state:
	# First make the states the columns, rows the candidates:

	df_geo_counts = df_geo_counts.reset_index(name='contributor_count')
	print(df_geo_counts)

	# Bar Plot: Unique Contributor Count vs Committee for each swing state:
	sns.barplot(x='committee_name', y='contributor_count', hue='contributor_state', data=df_geo_counts)
	plt.show()

	df_geo_sum = df_geo.groupby(level=['committee_name','contributor_state'])['contributor_aggregate_ytd'].sum()
	df_geo_sum.sort_index(inplace=True)
	df_geo_sum = df_geo_sum.loc[(slice(None), states)]
	df_geo_sum = df_geo_sum.reset_index(name='contribution_aggregate_ytd_sum')
	print(df_geo_sum)

	# Bar Plot: YTD Contribution Sum vs Committee for each swing state:
	sns.barplot(x='committee_name', y='contribution_aggregate_ytd_sum', hue='contributor_state', data=df_geo_sum)
	plt.show()

	# Making plots from df_contribution_size:

	# 1a) Stacked bar plot of donor amounts by range of donation amount
	# 1b) Stacked bar plot of donor counts by range of donation amount
	fig, ax = plt.subplots(1,2, figsize=(8,8))
	colors = ["#006D2C", "#31A354","#74C476","#9cce9e","#c5d8c6"]
	cols = df_contribution_size['range']
	print('cols:\n', cols)

	df_amount_pivot = df_contribution_size.pivot(index='committee_name', columns='size', values='total')
	df_count_pivot = df_contribution_size.pivot(index='committee_name', columns='size', values='pcnt')
	df_amount_pivot.plot.bar(stacked=True, color=colors, legend=True, ax=ax[0])
	df_count_pivot.plot.bar(stacked=True, color=colors, legend=True, ax=ax[1])
	ax[0].set_xlabel('Candidate'); ax[0].set_ylabel('Donation amount, $1E6')
	ax[1].set_xlabel('Candidate'); ax[1].set_ylabel('Donation amount/Total amount, %')
	plt.savefig('FEC_Donation_Range_Amounts_and_Pcnts.png', bbox_inches='tight')
	plt.show()

	# 2) Using Contribution Size data to determine fractions of various donation amounts:
	df_cs_below_200 = df_contribution_size[df_contribution_size['size']==0].set_index('committee_name')
	df_cs_200_to_499 = df_contribution_size[df_contribution_size['size']==200].set_index('committee_name')
	df_cs_500_to_999 = df_contribution_size[df_contribution_size['size']==500].set_index('committee_name')
	df_cs_1000_to_1999 = df_contribution_size[df_contribution_size['size']==1000].set_index('committee_name')
	df_cs_above_2000 = df_contribution_size[df_contribution_size['size']==2000].set_index('committee_name')
	print('df_cs_below_200:\n', df_cs_below_200)
	print('df_cs_1000_to_1999:\n', df_cs_1000_to_1999)
	df_cs_all = df_contribution_size.groupby('committee_name')['total'].sum()
	print('df_cs_all:\n', df_cs_all)
	df_cs_pcnt_below_200 = df_cs_below_200['total'] / df_cs_all * 100
	print('df_cs_pcnt_below_200:\n', df_cs_pcnt_below_200)
	df_cs_pcnt_above_2000 = df_cs_above_2000['total'] / df_cs_all * 100
	print('df_cs_pcnt_above_2000:\n', df_cs_pcnt_above_2000)


	# I LEFT OFF HERE AND THIS PLOT ISN'T WORKING DUE TO MISSING DATA IN BERNIE'S AND KAMALA'S
	# CONTRIBUTION SIZE FILES
	plt.close()
	# Plotting bar plots of fraction of donors giving under $200:
	f,ax = plt.subplots(1,2, figsize=(8,8))
	df_cs_pcnt_below_200.plot.bar(use_index=True, ax=ax[0], rot=90, legend=False, color='gray')
	df_cs_pcnt_above_2000.plot.bar(use_index=True, ax=ax[1], rot=90, legend=False, color='gray')
	# df_below_200_pcnt_2019.plot.bar(use_index=True, ax=ax[0,1], rot=90, legend=False, color='#bf8957')
	# df_above_2700_pcnt.plot.bar(use_index=True, ax=ax[1,0], rot=90, legend=False, color='#3d5782')
	# df_above_2700_pcnt_2019.plot.bar(use_index=True, ax=ax[1,1], rot=90, legend=False, color='#5e85c4')
	# Modify axes:
	ax[0].set_xlabel('Candidate'); ax[0].set_ylabel('% Donations < $200'); ax[0].set_title('Q1 2019')
	ax[1].set_xlabel('Candidate'); ax[1].set_ylabel('% Donations > $2700'); ax[1].set_title('Q1 2019')

	# Turn off x-axis labels and x-axis tick labels for top three plots:
	# x_axis = ax[0,0].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# x_axis = ax[0,1].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	plt.suptitle('All Donations')
	# Savefig and show:
	plt.savefig('FEC_Pcnt_Donations_Under_200.png', bbox_inches='tight')
	plt.show()

	''' Plotting: Percentage of all donations below and above various thresholds '''
	df_below_200_count = df.groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: (x<=200).sum())#.reset_index(name='count')
	df_all_count = df.groupby('committee_name')['contribution_receipt_amount'].agg('count')
	print('df_below_200_count:\n', df_below_200_count)
	print('df_all_count:\n', df_all_count)
	df_below_200_pcnt = round(df_below_200_count / df_all_count * 100)
	df_below_200_pcnt.sort_values(ascending=True, inplace=True)
	print('df_below_200_pcnt:\n', df_below_200_pcnt)



	# PLOT POLLING NUMBERS PER DOLLAR RAISED
	# PLOT POLLING NUMBERS PER TV COVERAGE

	# Plotting percent of all donations under $200 and over $2700
	# for all time and 2019 (presidential bids):
	date_object = datetime.date(2019,1,1)
	print('date_object:\n', date_object)
	df_below_200_count_2019 = df[df['contribution_receipt_date'] > date_object].groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: (x<=200).sum())#.reset_index(name='count')
	df_all_count_2019 = df[df['contribution_receipt_date'] > date_object].groupby('committee_name')['contribution_receipt_amount'].agg('count')
	print('df_below_200_count_2019:\n', df_below_200_count_2019)
	print('df_all_count_2019:\n', df_all_count_2019)
	df_below_200_pcnt_2019 = round(df_below_200_count_2019 / df_all_count_2019 * 100)
	df_below_200_pcnt_2019.sort_values(ascending=True, inplace=True)
	print('df_below_200_pcnt_2019:\n', df_below_200_pcnt_2019)
	
	
	df_above_2700_count = df.groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: (x>2700).sum())
	df_all_count = df.groupby('committee_name')['contribution_receipt_amount'].agg('count')
	print('df_above_2700_count:\n', df_above_2700_count)
	df_above_2700_pcnt = round(df_above_2700_count / df_all_count * 100)
	df_above_2700_pcnt.sort_values(ascending=True, inplace=True)
	print('df_above_2700_pcnt:\n', df_above_2700_pcnt)

	# Plotting percent of all donations under $200 and over $2700
	# for all time and 2019 (presidential bids):
	date_object = datetime.date(2019,1,1)
	print('date_object:\n', date_object)
	df_above_2700_count_2019 = df[df['contribution_receipt_date'] > date_object].groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: (x>2700).sum())#.reset_index(name='count')
	df_all_count_2019 = df[df['contribution_receipt_date'] > date_object].groupby('committee_name')['contribution_receipt_amount'].agg('count')
	print('df_above_2700_count_2019:\n', df_above_2700_count_2019)
	print('df_all_count_2019:\n', df_all_count_2019)
	df_above_2700_pcnt_2019 = round(df_above_2700_count_2019 / df_all_count_2019 * 100)
	df_above_2700_pcnt_2019.sort_values(ascending=True, inplace=True)
	print('df_above_2700_pcnt_2019:\n', df_above_2700_pcnt_2019)
	
	plt.close()
	# Plotting bar plots of fraction of donors giving under $200:
	f,ax = plt.subplots(2,2, figsize=(8,8))
	df_below_200_pcnt.plot.bar(use_index=True, ax=ax[0,0], rot=90, legend=False, color='#825e3d')
	df_below_200_pcnt_2019.plot.bar(use_index=True, ax=ax[0,1], rot=90, legend=False, color='#bf8957')
	df_above_2700_pcnt.plot.bar(use_index=True, ax=ax[1,0], rot=90, legend=False, color='#3d5782')
	df_above_2700_pcnt_2019.plot.bar(use_index=True, ax=ax[1,1], rot=90, legend=False, color='#5e85c4')
	# Modify axes:
	ax[0,0].set_ylabel('% Donations < $200'); ax[0,0].set_title('Jan 1, 2017 - Apr 15, 2019')
	ax[0,1].set_title('Q1 2019')
	ax[1,0].set_xlabel('Candidate'); ax[1,0].set_ylabel('% Donations > $2700')
	ax[1,1].set_xlabel('Candidate')
	# Turn off x-axis labels and x-axis tick labels for top three plots:
	# x_axis = ax[0,0].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# x_axis = ax[0,1].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	plt.suptitle('Itemized Donations')
	# Savefig and show:
	plt.savefig('FEC_Pcnt_Donations_Under_200.png', bbox_inches='tight')
	plt.show()


	plt.close()
	# Plotting histogram of Yang, Bernie and Klobuchar donation amounts:
	df_yang = df[df['committee_name'] == 'Yang']
	df_sanders = df[df['committee_name'] == 'Sanders']
	df_klobuchar = df[df['committee_name'] == 'Klobuchar']
	f,ax = plt.subplots(1,3, figsize=(12,3))
	df_yang.hist(column='contribution_receipt_amount', ax=ax[0], bins=100, rwidth=0.95, color='#142e7b')
	df_sanders.hist(column='contribution_receipt_amount', ax=ax[1], bins=100, rwidth=0.95, color='#4a5410')
	df_klobuchar.hist(column='contribution_receipt_amount', ax=ax[2], bins=100, rwidth=0.95, color='gray')
	# Modify axes:
	donation_amount_limit_x = 1000	# Upper histogram donation amount limit in dollars (y axis)
	donation_count_limit_y = 20000	# Upper histogram donation count limit (x axis)
	ax[0].set_xlim(0,donation_amount_limit_x); ax[0].set_ylim(0, donation_count_limit_y)
	ax[0].set_title('Yang')
	ax[0].set_xlabel('Donation Amount')
	ax[0].set_ylabel('Donation Count')
	ax[1].set_xlim(0,donation_amount_limit_x); ax[1].set_ylim(0, donation_count_limit_y)
	ax[1].set_title('Sanders')
	ax[1].set_xlabel('Donation Amount')
	ax[2].set_xlim(0,donation_amount_limit_x); ax[2].set_ylim(0, donation_count_limit_y)
	ax[2].set_title('Klobuchar')
	ax[2].set_xlabel('Donation Amount')
	plt.suptitle('Itemized Donations')
	# Savefig and show:
	plt.savefig('FEC_Yang_Sanders_Donation_Count_Hist.png', bbox_inches='tight')
	plt.show()


	# Aggregated df for plotting the following:
	# Sum: Total money donated to each candidate's PAC
	# Count: Total number of unique donations
	# Mean: Average donation size in dollars
	# Std: Standard deviation of the donation amounts
	df_stats = df.set_index('committee_name')['contribution_receipt_amount']
	df_stats = df_stats.groupby(['committee_name']).agg(['sum','count','mean','std'])
	df_stats['sum'] = df_stats['sum'] / 1000000		# Scaling by $1 million
	df_stats['count'] = df_stats['count'] / 1000	# Scaling by $1000
	print('df_stats:\n', df_stats)


	plt.close()
	# Plotting: Time Series of cumulative sum of donation amounts
	plt.figure(figsize=(8,5))
	df_timeseries_donation_amount = df.set_index('contribution_receipt_date')[['committee_name', 'contribution_receipt_amount']]
	df_timeseries_donation_amount['cumsum'] = df_timeseries_donation_amount.groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: x.cumsum())
	df_timeseries_donation_amount.groupby('committee_name')['cumsum'].plot(y='cumsum', legend=True)
	print('df_timeseries_donation_amount:\n', df_timeseries_donation_amount)
	plt.ylabel('Cumulative Donations, $')
	plt.xlabel('Date')
	plt.suptitle('Itemized Donations')
	plt.savefig('FEC_Donation_Time_Series.png', bbox_inches='tight')
	plt.show()


	plt.close()
	# Plotting: Total donation amount, unique donors, average donation amount:
	fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(6,10))
	df_stats.plot.bar(y='sum', use_index=True, ax=ax[0], rot=0, legend=False, color='gray')
	df_stats.plot.bar(y='count', use_index=True, ax=ax[1], rot=0, legend=False, color='k')
	df_stats.plot.bar(y='mean', yerr='std', use_index=True, ax=ax[2], rot=0, legend=False, color='r')
	df.boxplot(column='contribution_receipt_amount', by='committee_name', ax=ax[3], rot=0)
	# Modify axes:
	ax[0].set_ylabel('Donation Total, $1E6')
	ax[1].set_ylabel('Unique Donations, 1000\'s')
	ax[2].set_ylabel('Avg Donation, $')
	ax[3].set_ylabel('Donation Amount, $'); ax[3].set_xlabel('PAC'); ax[3].set_title('')
	# Turn off x-axis labels and x-axis tick labels for top three plots:
	x_axis = ax[0].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	x_axis = ax[1].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	x_axis = ax[2].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# Savefig and show:
	plt.suptitle('')
	plt.subplots_adjust(left=0.2, right=0.9, bottom=0.1, top=0.9, wspace=0.2, hspace=0.15)
	plt.xticks(rotation=90)
	plt.suptitle('Itemized Donations')
	plt.savefig('FEC_Donation_Data', bbox_inches='tight')
	plt.show()


	return


''' ----------------------------------------------------------------------------------------------- '''
def NationalPolling():
	df = pd.read_csv('/home/dp/Documents/Campaign/NationalPolling.csv', sep=',')
	print('df:\n', df.to_string())
	print(df.isnull().sum())

	# pandas is unable to convert the current string to a datetime, so string
	# formatting is done to remove the first date and merge with the Year column
	unparsed_dates = df.Date.tolist()
	print('Dates before parsing:\n', unparsed_dates)
	# Removing '-' and all spaces from '8/17 - 8/20'
	parsed_dates = [s[0:s.index('- ')].replace('- ','').replace(' ','') for s in unparsed_dates]
	complete_dates = [d+'/'+str(y) for d,y in zip(parsed_dates, df.Year)]
	# Making a Series to assign to overwrite Date column of df. Could have also
	# converted complete_dates to NumPy array using np.asarray(complete_dates) and
	# assigned it to df.Date
	df.Date = pd.Series(complete_dates)
	df.Date = pd.to_datetime(df.Date)	
	# Don't need the Year column anymore:
	df.drop('Year', axis=1, inplace=True)
	# Drop Klobuchar so final plot can be 4x3:
	df.drop('Klobuchar', axis=1, inplace=True)
	df.replace('--', np.nan, inplace=True)
	df.set_index('Date', inplace=True)
	# Removing the apostrophe from O'Rourke
	df.columns = df.columns.str.replace("'", "")
	# Create a list of candidates:
	candidates = df.columns.values[1:]
	# df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce') # This is superceded by the integer conversion below
	# Note that pd.to_numeric above can't be applied to an entire dataframe like astype can. It acts on 1-D objects: arrays, strings, Series, etc.
	# Convert to nullable int8:
	df.loc[:,candidates] = df.loc[:,candidates].astype(dtype='float64', errors='raise') # All the numbers are strings, so convert to float first...
	df.loc[:,candidates] = df.loc[:,candidates].astype(dtype=pd.Int8Dtype(), errors='raise') # then convert to nullable int8
	print('df:\n', df.to_string())
	print('df.dtypes:\n', df.dtypes)

	# Finding the average and std deviation of each poll
	# This data isn't used for anything at the moment
	poll_agg = df.groupby('Poll').agg(['mean','std'])
	print('poll_agg:\n', poll_agg)
	
	# Melting for the purpose of seaborn plots
	df_sns = df.reset_index()
	print('df_sns:\n', df_sns)
	df_sns = pd.melt(df_sns, id_vars=['Date','Poll'], value_vars=candidates, var_name='Candidate', value_name='PollPcnt')
	print('df_sns:\n', df_sns)
	print('df_sns.dtypes:\n', df_sns.dtypes)
	df_sns.PollPcnt = df_sns.PollPcnt.astype(dtype=pd.Int8Dtype(), errors='raise')


	# CatPlot of bars: mean and std of each poll for each candidate
	plt.close()
	g = sns.catplot(kind='bar', x='Poll', y='PollPcnt', col='Candidate', data=df_sns, estimator=np.mean, col_wrap=3, height=2, aspect=1.5)
	g.set_xticklabels(rotation=90)
	plt.savefig('national_polling__poll_comparison.png', bbox_inches='tight')
	plt.show()

	# Lineplot: Time series of polling percent
	plt.close()
	plt.figure(figsize=(7,6))
	sns.lineplot(x='Date', y='PollPcnt', hue='Candidate', data=df_sns, estimator=np.mean)
	plt.xticks(rotation=45)
	plt.ylabel('National Polling, %')
	plt.savefig('national_polling__poll_time_series.png', bbox_inches='tight')
	plt.show()

	return
''' --------------------------------------------------------------------------------------------- '''


def CampaignBetting():

	driver = webdriver.Chrome('/usr/bin/chromedriver')
	# Runningn 'driver.minimize_window()' doesn't allow the donor count to update
	driver.set_window_size(0, 0)
	driver.set_window_position(0,0)
	#driver = webdriver.Chrome('/home/dp/Downloads/')  # Optional argument, if not specified will search path.
	url = 'https://electionbettingodds.com/'
	driver.get(url)
	time.sleep(1) # Allow the user see website load	

	#--- Getting each table:
	tables = driver.find_elements_by_xpath('table')
	tables = [table.get_attribute('innerHTML') for table in tables]
	print('tables:\n', tables)

	#--- Getting candidate names:
	img_elements = driver.find_elements_by_tag_name('img')
	img_elements_list = [str(img.get_attribute('src')) for img in img_elements]
	# print('img_elements_list:\n', img_elements_list)

	#--- Filtering: unfiltered_name_list contains candidate names and instances of 'green' and 'red'
	unfiltered_name_list = [s.replace('https://electionbettingodds.com/','').replace('.png','') for s in img_elements_list if '/' in s]
	name_list = [i for i in unfiltered_name_list if 'red' not in i and 'green' not in i]
	# print('name_list:\n', name_list)

	#--- Getting betting percentiles, putting them into pcnt_list:
	betting_odds = driver.find_elements_by_xpath("//p[@style='font-size: 55pt; margin-bottom:-10px']")
	odds_list = [float(pcnt.get_attribute('innerHTML').replace('%','')) for pcnt in betting_odds]

	# Close driver:
	driver.quit()

	num_names = len(name_list)
	num_odds = len(odds_list)
	if num_names != num_odds:
		print('!!!!!!!!!!!! Warning: number of candidates does not match number of percentiles\n\n\n\n\n\n\n\n')

	# Combine both lists:
	# name_pcnt_list = [[i,j] for i,j in zip(name_list,pcnt_list)] # Not using this as I don't need to combine

	print('scraped name_list:\n', name_list)
	print('scraped pcnt_list:\n', odds_list)
	print('len scraped name_list:', len(name_list))
	print('len scraped odds_list:', len(odds_list))

	# Finding 'Other' in the names list to split the list into Democratic, Republican and Presidential primaries
	# A better way would be to grab each list with independent calls
	# [add 1 to every element x of [16, 47, 53 <- indices where 'Other' is located]]
	# Results in [17, 48, 54]
	num_other = name_list.count('Other')
	if num_other == 3:
		# Using 'Other' to find the end of each list. This works unless one of the lists
		# doesn't have 'Other', in which case the else loop below uses the difference
		# between one list's leading candidate and the previous list's bottom candidate
		end_indices = [x+1 for x in [i for i, n in enumerate(name_list) if n == 'Other']]
		start_indices = [0] + end_indices[0:-1]
	else:
		# In this loop, the odds_list[i+1] - odds_list[i] is computed. If that difference
		# is larger than 10, then that likely signals the start of a new list where the
		# leader's (Trump's) percentage is high and last person from the previous list
		# (Hickenlooper) is very low. The difference should be at least 10. Because the
		# last list (Republicans) doesn't have a list that follows it, just tack on the
		# last index to end_indices.
		odds_shifted = odds_list[1:]
		odds_shifted.extend([0]) # This amends without the need for assignment
		print('odds_shifted:\n', odds_shifted)
		odds_diff = np.array(odds_shifted) - np.array(odds_list)
		print('odds_diff:\n', odds_diff)
		# find where odds differences are > 10. Add one to account for non-inclusive end
		end_indices = [i for i in [i for i,d in enumerate(odds_diff) if d > 10]]
		end_indices.extend([len(odds_list)-1])
		start_indices = [0] + end_indices[0:-1]

	grouped_name_list = []; grouped_odds_list = []
	for i,j in zip(start_indices, end_indices):
		grouped_name_list.append(name_list[i:j])
		grouped_odds_list.append(odds_list[i:j])

	# Grouped by race:
	# [[Dem primary race candidate names],	[Pres race candidate names],	[Rep primary race candidates]]
	# [[Dem primary race betting odds],		[Pres race betting odds],		[Rep primary betting odds]]
	# These grouped lists are used to make dictionaries of:
	# {'Time':Datetime, '1st place name': odds, '2nd place name': odds, ... ,'Last place name': odds}
	# Note: The resulting dem_dict, rep_dict, pres_dict are ordered from first place candidate to last,
	# but this changes from day to day and needs to be sorted according to the previous day's candidate ranks
	print('grouped_name_list:\n', grouped_name_list)
	print('grouped_pcnt_list:\n', grouped_odds_list)
	print('start_indices:', start_indices)	# e.g. [0,18,50]
	print('end indices:', end_indices)		# e.g. [18, 50, 56]

	# Naming convention:
	# new_ <- Just pulled from website
	# old_ <- Data from csv from previous scrape

	# Warning: This may error here if electionbettingodds.com has removed
	# 'Other' classification from the ends of its list.
	print('THIS MAY ERROR HERE: SEE NOTES IN CODE')
	new_dem_fields = grouped_name_list[0]
	new_rep_fields = grouped_name_list[2]
	new_pres_fields = grouped_name_list[1]
	# print('dem_fields:\n', dem_fields)
	# print('rep_fields:\n', rep_fields)
	# print('pres_fields:\n', pres_fields)

	new_dem_odds = grouped_odds_list[0]
	new_rep_odds = grouped_odds_list[2]
	new_pres_odds = grouped_odds_list[1]
	# print('dem_odds:\n', dem_odds)
	# print('rep_odds:\n', rep_odds)
	# print('pres_odds:\n', pres_odds)

	# Get current time:
	current_time = datetime.datetime.now()
	print('current_time:', current_time)
	time_tuple_list = [tuple(('Time',current_time))]

	# Pair the field names (candidates) with betting odds into tuples:
	new_dem_field_odds = [(i,j) for i,j in zip(new_dem_fields, new_dem_odds)]
	new_rep_field_odds = [(i,j) for i,j in zip(new_rep_fields, new_rep_odds)]
	new_pres_field_odds = [(i,j) for i,j in zip(new_pres_fields, new_pres_odds)]

	# Sort the lists by first element of each tuple (e.g. sort by candidate name)
	new_dem_field_odds.sort(key=lambda x: x[0])
	new_rep_field_odds.sort(key=lambda x: x[0])
	new_pres_field_odds.sort(key=lambda x: x[0])

	# After alphabetical sort, add time tuple so it's the leftmost element
	new_dem_field_odds = dict(time_tuple_list + new_dem_field_odds)
	new_rep_field_odds = dict(time_tuple_list + new_rep_field_odds)
	new_pres_field_odds = dict(time_tuple_list + new_pres_field_odds)
	# print('new_dem_field_odds:\n', new_dem_field_odds)
	# print('new_rep_field_odds:\n', new_rep_field_odds)
	# print('new_pres_field_odds:\n', new_pres_field_odds)


	# Read current CSV data and compare it to new scraped data
	# to see if the field has changed since the last time data was recorded
	old_dem_odds = pd.read_csv('RaceDem.csv').iloc[-1].values.tolist()
	old_rep_odds = pd.read_csv('RaceRep.csv').iloc[-1].values.tolist()
	old_pres_odds = pd.read_csv('RacePres.csv').iloc[-1].values.tolist()
	old_dem_field = pd.read_csv('RaceFieldsDem.csv').iloc[-1].values.tolist()
	old_rep_field = pd.read_csv('RaceFieldsRep.csv').iloc[-1].values.tolist()
	old_pres_field = pd.read_csv('RaceFieldsPres.csv').iloc[-1].values.tolist()
	# print('Verifying old_dem_odds from CSV file:\n', old_dem_odds)
	# print('Verifying old_dem_field from CSV file:\n', old_dem_field)

	# Make old field-odds list as a guide for filling new_dem_field_odds with np.nan
	# where candidates are missing from the scraped data
	old_dem_field_odds = {n:o for (n,o) in zip(old_dem_field, old_dem_odds)}
	old_rep_field_odds = {n:o for (n,o) in zip(old_rep_field, old_rep_odds)}
	old_pres_field_odds = {n:o for (n,o) in zip(old_pres_field, old_pres_odds)}
	print('--------------------------------------------- old_dem_field_odds:\n', old_dem_field_odds)
	print('--------------------------------------------- old_rep_field_odds:\n', old_rep_field_odds)
	print('--------------------------------------------- old_pres_field_odds:\n', old_pres_field_odds)


	# If a name in old_dem_field_odds matches any name in new_dem_field_odds, then return the name and new odds value, else return 0
	# old_pres_field_odds 			= {'Time': '2019-04-05 19:40:28.784303', 'Avenatti': 0.1, 'Biden': 6.9, 'Bloomberg': 0.4, 'Booker': 0.9, 'Brown': 0.1, 'Buttigieg': 5.7, ...}
	# new_pres_field_odds 			= {'Time': datetime(2019,4,6,14,57,13), 'Biden': 7.0, 'Bloomberg': 0.4, 'Booker': 0.9, 'Buttigieg': 5.6, ...}
	# new_pres_field_odds_matched 	= {'Time': datetime(2019,4,6,14,57,13), 'Avenatti': 0, 'Biden': 7.0, 'Bloomberg': 0.4, 'Booker': 0.9, 'Brown': 0, 'Buttigieg': 5.6, ...}
	# Note how the new_pres_field_odds_matched list has Avenatti at 0 and Biden's updated value of 7.0. Between old and new, Avenatti was dropped
	# from the presidential race list and Biden's odds value changed.
	# For some reason the new_ dictionaries have datetime objects but the resulting CSV write is the same.
	new_dem_field_odds_matched = {k:new_dem_field_odds[k] if k in new_dem_field_odds else 0 for (k,v) in old_dem_field_odds.items()}
	new_rep_field_odds_matched = {k:new_rep_field_odds[k] if k in new_rep_field_odds else 0 for (k,v) in old_rep_field_odds.items()}
	new_pres_field_odds_matched = {k:new_pres_field_odds[k] if k in new_pres_field_odds else 0 for (k,v) in old_pres_field_odds.items()}
	print('********************************************* new_dem_field_odds_matched:\n', new_dem_field_odds_matched)
	print('********************************************* new_rep_field_odds_matched:\n', new_rep_field_odds_matched)
	print('********************************************* new_pres_field_odds_matched:\n', new_pres_field_odds_matched)


	# Now that the latest scraped field and odds data is matched to the old csv data
	# with all missing values filled in with np.nan, write this data to dictionaries
	''' Dict comprehension syntax:		d = {key: value for (key, value) in dict.items()} Note: .items() makes the dictionary iterable'''
	''' Dict comprehension from lists:	d = {key: value for (key, value) in zip(key_list, value_list)} '''
	# Dictionaries are written to CSV files
	new_dem_dict = new_dem_field_odds_matched
	new_rep_dict = new_rep_field_odds_matched
	new_pres_dict = new_pres_field_odds_matched
	print('new_dem_dict:\n', new_dem_dict)
	print('new_rep_dict:\n', new_rep_dict)
	print('new_pres_dict:\n', new_pres_dict)
	# Written to CSV fieldnames
	new_dem_field = list(new_dem_dict.keys())
	new_rep_field = list(new_rep_dict.keys())
	new_pres_field = list(new_pres_dict.keys())
	print('new_dem_field from dictionary:\n', new_dem_field)


	''' Now that I have the new scraped data into one dictionary for each race,
		I write it to the csv files and pickle it, then pull the up-to-date csv data,
		put it into dataframes to plot.
		Note: Each dictionary is one row of data. '''

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
	# Writing dictionaries with scraped data to csv:
	with open(r'RaceDem.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=new_dem_field)
		writer.writerow(new_dem_dict)
	with open(r'RaceRep.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=new_rep_field)
		writer.writerow(new_rep_dict)
	with open(r'RacePres.csv', 'a', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=new_pres_field)
		writer.writerow(new_pres_dict)

	# Writing fields to a fields-specific csv to notify if political field changes
	with open(r'RaceFieldsDem.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(new_dem_field)
	with open(r'RaceFieldsRep.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(new_rep_field)
	with open(r'RaceFieldsPres.csv','a', newline='') as f:
		writer = csv.writer(f)
		writer.writerow(new_pres_field)
	''' ------------------------- '''

	# Read csv files into dataframe. Doing this here to plot the entire
	# time series of the data. Alternatively, could read in old data from csv,
	# append new data to the dataframe, write back to csv, then plot dataframe.

	df_dem = pd.read_csv('RaceDem.csv')
	df_rep = pd.read_csv('RaceRep.csv')
	df_pres = pd.read_csv('RacePres.csv')
	df_dem_field = pd.read_csv('RaceFieldsDem.csv')
	df_rep_field = pd.read_csv('RaceFieldsRep.csv')
	df_pres_field = pd.read_csv('RaceFieldsPres.csv')
	# Checking data from csv read:
	print('--- Checking data from csv read:\n')
	print('df_dem bet percents from old csv:\n\n', df_dem.to_string())
	print('\n\n')
	print('df_dem_field from old csv:\n\n', df_dem_field.to_string())
	print('\n\n')

	# Generate warning if latest field doesn't match prior:
	# if previous dem field from csv (df_dem_field.iloc[-1]) doesn't match current scraped dem field (df_dem_field)
	# print('list(df_dem_field.iloc[-1]):\n', list(df_dem_field.iloc[-1]))
	# print('dem_fields:\n', dem_fields)

	if any(df_dem_field.iloc[-1] != new_dem_field):
		print('!!!!!!!!!!!!!!!!!!!!!!! Dem field has changed')
		print('df_dem_field.iloc[-1]:\n', df_dem_field.iloc[-1])
		print('new_dem_field:\n', new_dem_field)
	if any(df_rep_field.iloc[-1] != new_rep_field):
		print('!!!!!!!!!!!!!!!!!!!!!!! Rep field has changed')
		print('df_rep_field.iloc[-1]:\n', df_rep_field.iloc[-1])
		print('new_rep_field:\n', new_rep_field)
	if any(df_pres_field.iloc[-1] != new_pres_field):
		print('!!!!!!!!!!!!!!!!!!!!!!! Pres field has changed:\n')
		print('df_pres_field.iloc[-1]:\n', df_pres_field.iloc[-1])
		print('new_pres_field:\n', new_pres_field)

	# Format csv derived Time column before plotting:
	df_dem['Time'] = pd.to_datetime(df_dem['Time'], format='%Y-%m-%d %H:%M:%S')
	df_rep['Time'] = pd.to_datetime(df_rep['Time'], format='%Y-%m-%d %H:%M:%S')
	df_pres['Time'] = pd.to_datetime(df_pres['Time'], format='%Y-%m-%d %H:%M:%S')
	# Check time formatting:
	# print('time type:\n', type(df_dem.iloc[0]['Time']))

	# # Append latest scraped data (dem_csv_fieldnames) to csv derived df's (df_dem)
	# # to plot and pickle out:
	# df_dem = df_dem.append(dem_dict, ignore_index=True)
	# df_rep = df_rep.append(rep_dict, ignore_index=True)
	# df_pres = df_pres.append(pres_dict, ignore_index=True)
	# df_dem_field = df_dem_field.append(dem_csv_fieldnames, ignore_index=True)
	# df_rep_field = df_rep_field.append(dem_csv_fieldnames, ignore_index=True)
	# df_pres_field = df_pres_field.append(dem_csv_fieldnames, ignore_index=True)

	# Pickle out:
	BettingOdds_df_dem_odds_pkl = df_dem.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_dem_odds.pkl')
	BettingOdds_df_rep_odds_pkl = df_rep.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_rep_odds.pkl')
	BettingOdds_df_pres_odds_pkl = df_pres.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_pres_odds.pkl')
	BettingOdds_df_dem_field_pkl = df_dem_field.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_dem_field.pkl')
	BettingOdds_df_rep_field_pkl = df_rep_field.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_rep_field.pkl')
	BettingOdds_df_pres_field_pkl = df_pres_field.to_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_pres_field.pkl')

	return



def PlotCampaignBetting():

	df_dem_odds = pd.read_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_dem_odds.pkl')
	df_rep_odds = pd.read_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_rep_odds.pkl')
	df_pres_odds = pd.read_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_pres_odds.pkl')

	print('df_dem_odds pickle in:\n', df_dem_odds.to_string())

	df_dem_odds.set_index('Time', inplace=True)
	df_rep_odds.set_index('Time', inplace=True)
	df_pres_odds.set_index('Time', inplace=True)

	# Filtering the top 4%, 8% and 5% of the dem, rep and pres odds to make legend manageable
	# Mask the odds dataframes, resulting in all values below 3% to be turned to nans,
	# grab values abot 3%, drop all columns that are entirely nans:
	df_dem_odds_top = df_dem_odds[df_dem_odds.gt(4)].dropna(axis=1, how='all')
	df_rep_odds_top = df_rep_odds[df_rep_odds.gt(8)].dropna(axis=1, how='all')
	df_pres_odds_top = df_pres_odds[df_pres_odds.gt(5)].dropna(axis=1, how='all')

	dem_odds_cols = df_dem_odds_top.columns
	rep_odds_cols = df_rep_odds_top.columns
	pres_odds_cols = df_pres_odds_top.columns

	plt.close()

	# Pandas plotting of odds data for all three races:
	fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12,6)) # figsize(width, height)
	print('ax:\n', ax); print('fig:\n', fig)
	df_dem_odds_top.plot(y=dem_odds_cols, use_index=True, title='Democratic Primary', drawstyle='steps-post', ax=ax[0])
	df_rep_odds_top.plot(y=rep_odds_cols, use_index=True, title='Republican Primary', drawstyle='steps-post', ax=ax[1])
	df_pres_odds_top.plot(y=pres_odds_cols, use_index=True, title='Presidential Race', drawstyle='steps-post', ax=ax[2])
	ax[0].set_ylabel('Odds, %')
	ax[0].legend(loc='center left')
	ax[1].legend(loc='center left')
	ax[2].legend(loc='center left')
	# Turn off x-axis labels and x-axis tick labels for top three plots:
	# x_axis = ax[0].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# x_axis = ax[1].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	plt.savefig('Betting Odds - All Races.png', bbox_inches='tight')
	plt.show()

	return



def SortCampaignBettingCSV():
	# How this works:
	# Problem:	One csv file's data (all strings of presidential candidates) needs to be sorted
	#			alphabetically along each row, and another csv file's data (the numerical odds of
	#			each candidate winning) need to follow the alphabetized data (e.g. Each
	#			candidate's odds of winning need to follow the candidate as it is reordered relative
	#			to other candidates in its row).
	#
	# Uses:		This function can be used on any two arrays of data where one comprises string
	#			values that need to be reordered according to particular criteria and the sister
	#			data in another array needs to follow suit.
	#
	# Notes:	One tempting option is to unravel both datasets into 1D arrays, merge them to pair them,
	#			and then sort each pair. You would end up with [..., ['Avenatti',1.2],['Avenatti',1.2]...]
	#			where each original row's neighbors are lost, and could be resolved by assembling
	#			every nth row into a single list, and so on until the end of the 1D array.
	#
	# This function takes in odds and field csv files and organizes them by the following:
	# 1) Create an array of arrays each containing a name-odds pair
	# 2) Sort the subarray tuples according to the name in each, thus making them alphabetical,
	#    e.g. [ [('Avenatti',odds), ('Biden',odds), ..., ('Zuckerberg',odds)], ..., [('Avenatti',odds), ('Biden',odds), ... , ('Zuckerberg',odds)] ]
	# 3) Unzip the names from the odds values using unzipped_list = [zip(*sub_list) for sub_list in list], resulting in
	#    e.g. [ [('Avenatti','Biden', ...,'Zuckerberg'),(odds, odds, ..., odds)], ..., [('Avenatti','Biden', ...,'Zuckerberg'),(odds,odds, ...,odds)] ]
	# 4) Separate each sublist's two tuples into df_pres_field and df_pres_odds dataframes using two list comprehensions
	# 5) Write the dataframes to csv's
	df_pres_field = pd.read_csv('/home/dp/Documents/Campaign/RaceFieldsPres.csv')
	df_pres_odds = pd.read_csv('/home/dp/Documents/Campaign/RacePres.csv')
	print('df_pres_odds:\n', df_pres_odds)

	# Convert to numpy array:
	pres_field_array = df_pres_field.values
	pres_odds_array = df_pres_odds.values

	# Delete the first Time column and datetime column
	pres_field_array = np.delete(pres_field_array, 0, axis=1)
	pres_odds_array = np.delete(pres_odds_array, 0, axis=1)

	print('pres_field_array:\n', pres_field_array)
	print('shape pres_field_array:\n', np.shape(pres_field_array))
	print('pres_odds_array:\n', pres_odds_array)
	print('shape pres_odds_array:\n', np.shape(pres_odds_array))

	# Bring separate field and odds sublists together into pairs for sorting:
	pres_field_odds_list = [list(zip(x,y)) for x,y in zip(pres_field_array,pres_odds_array)]
	print('pres_field_odds_list:\n', pres_field_odds_list)

	# Why does sub_list.sort(key=lambda tup: tup[0]) not work in the list comprehension? Possibly
	# because it alters sub_list directly, rather than returning a separate result like sorted?
	pres_field_odds_list_sorted = [sorted(sub_list, key=lambda tup: tup[0]) for sub_list in pres_field_odds_list]
	print('pres_field_odds_list_sorted:\n', pres_field_odds_list_sorted)

	# Unpack sorted list of tuples to separate numpy arrays or separate lists:
	l = [list(zip(*sub_list)) for sub_list in pres_field_odds_list_sorted] # pres_field_list, pres_odds_list
	print('l:\n', l)

	# Final sorted lists:
	pres_field_list = [list(x[0]) for x in l]
	pres_odds_list = [list(x[1]) for x in l]
	print('pres_field_list:\n', pres_field_list)
	print('pres_odds_list:\n', pres_odds_list)

	df_pres_field = pd.DataFrame(pres_field_list, columns=list(range(0,len(pres_field_list[-1]))))
	df_pres_odds = pd.DataFrame(pres_odds_list, columns=pres_field_list[-1])

	print('df_pres_field:\n', df_pres_field.to_string())
	print('df_pres_odds:\n', df_pres_odds.to_string())

	df_pres_field.to_csv('/home/dp/Documents/Campaign/RaceFieldsPres_Sorted.csv')
	df_pres_odds.to_csv('/home/dp/Documents/Campaign/RaceOddsPres_Sorted.csv')

	# Write to csv:

	''' --- Note about unzipping a list of tuples: First unzip works, second unzip rezips the data --- '''
	# >>> source_list = ('1','a'),('2','b'),('3','c'),('4','d')
	# >>> list1, list2 = zip(*source_list)
	# >>> list1
	# ('1', '2', '3', '4')
	# >>> list2
	# ('a', 'b', 'c', 'd')
	# Edit: Note that zip(*iterable) is its own inverse:

	# >>> list(source_list) == zip(*zip(*source_list))
	# True
	# When unpacking into two lists, this becomes:

	# >>> list1, list2 = zip(*source_list)
	# >>> list(source_list) == zip(list1, list2)
	# True
	''' ---------------------------------------------------------------------------------------------- '''
	return



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
	twitter_candidate_list = [s[s.rfind('/')+1:] for s in twitter_handle_list]
	print('twitter_candidate_list:\n', twitter_candidate_list)

	df_all_candidates = pd.DataFrame()
	for i, twitter_candidate in enumerate(twitter_candidate_list):
		url = 'https://socialblade.com/twitter/user/' + twitter_candidate + '/monthly'
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
		replacement_str = ' for ' + twitter_candidate

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
		csv_filename_base = '/home/dp/Documents/Campaign/TwitterMetrics/' + 'TwitterMetrics_'
		csv_filename = csv_filename_base + epo_list[0] + '.csv'
		print('csv_filename:\n', csv_filename)



		reshaped_dygraph_cleaned = [np.reshape(l, (int(len(l)/2),2)) for l in dygraph_cleaned]
		print('reshaped_dygraph_cleaned:\n', reshaped_dygraph_cleaned)
		print('reshaped_dygraph_cleaned[0]:\n', reshaped_dygraph_cleaned[0])

		# date_candidate_title_list will be used for column titles:
		# e.g. [['2019-02-28','AndrewYang','Daily Followers Gained'], ['2019-02-29','AndrewYang','Daily Followers Gained'], ...]
		date_list = ['Date']*len(title_list)
		date_title_list = [[date,title] for date,title in zip(date_list,title_list)]
		print('date_title_list:\n', date_title_list)

		data_arr = reshaped_dygraph_cleaned[0:6]
		col_arr = date_title_list[0:6]

		# Need to make name list for each reshaped dygraph numpy array:
		#l,r,c = np.shape(x)
		#name_list = np.full((l,r,1), twitter_candidate)
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
		name_list = [twitter_candidate]*len(df)
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
			df_all_candidates = df_all_candidates.append(df)
		else:
			df_all_candidates = pd.concat((df_all_candidates, df), axis=0, sort=True)
			''' ########################################### '''

		''' Creates csv, overwrites the current one of the same name: '''
		''' --- Only run once, then use append code block below --- '''
		# Writing percents to csv:
		df.to_csv(path_or_buf=csv_filename)

	# Adding the 'Name' column to the index (append does this):
	# Don't need name in the index
	#df_all_candidates.set_index(['Name'], append=True, inplace=True)

	# Export to csv
	csv_all_filename = csv_filename_base + 'AllCandidates.csv'
	df_all_candidates.to_csv(path_or_buf=csv_all_filename)
	print('df_all_candidates:\n', df_all_candidates.to_string())

	# Pickle out:
	TwitterMetrics_df_all_candidates_pkl = df_all_candidates.to_pickle('/home/dp/Documents/Campaign/pickle/TwitterMetrics_df_all_candidates.pkl')

	driver.quit()

	return dygraph_elements_list


def PlotWebMetrics(weeks, weekly_freq):
	df = pd.read_pickle('/home/dp/Documents/Campaign/pickle/TwitterMetrics_df_all_candidates.pkl')

	# Date column is already datetime64.
	# Dataframe is in tidy format. Will convert to short-form below.
	
	# Reset index so that dataframe can be pivoted later with index=Date column
	df.reset_index(inplace=True)
	print('df:\n', df.to_string())
	print('df.index:\n', df.index)

	# Dropping Donald Trump from df:
	df_no_dt_index = df[ df.Name=='realDonaldTrump' ].index
	df.drop(df_no_dt_index, inplace=True)
	print('df:\n', df.to_string())

	# The data is in tidy (long-form) format with dates and candidates repeated
	# Convert to short-form with pd.pivot
	df = df.pivot(index='Date', columns='Name')
	# Rename candidate names:
	name_dict = {'AndrewYang':'Yang', 'joebiden':'Biden', 'TulsiGabbard':'Gabbard', 'BernieSanders':'Sanders', 'ewarren':'Warren', 'BetoORourke':'ORourke', 'CoryBooker':'Booker', 'PeteButtigieg':'Buttigieg', 'amyklobuchar':'Klobuchar'}
	df.rename(name_dict, axis=1, level=1, inplace=True) # level 0 = data type names e.g. 'Daily Followers Gained', level 1 = candidate names
	# Getting only 2019 follower data:
	df_2019 = df[ df.index >= '2019-01-01' ].loc[:, ['Daily Followers Gained','Total Follower Count']]
	print('df_2019:\n', df_2019.to_string())
	print('df_2019.index:\n', df_2019.index)
	print('df_2019.index.dtype:\n', df_2019.index.dtype)
	# The level 0 columns lack a name. Call it 'Stat'
	df_2019.columns.rename('Stat', level=0, inplace=True)
	print('Column level names:\n', df.columns.names)
	# Identify an NaNs:
	print('df_2019 nulls:\n', df_2019.isnull().sum())
	# There is one NaN in Yang's Feb 27 data. Fill it with linear interpolation
	df_2019 = df_2019.interpolate(method='linear')
	# Check NaNs again:
	print('df_2019 nulls:\n', df_2019.isnull().sum())
	# No more NaNs remaining.
	# Baseline the 'Total Follower Count', assign to 'Total Follower Count Based' column
	min_followers = df_2019.loc['2019-01-01', 'Total Follower Count']
	follower_count_baseline = df_2019.loc[:, 'Total Follower Count'].subtract(min_followers)
	follower_count_baseline.columns = pd.MultiIndex.from_product([['Total Follower Count Based'], follower_count_baseline.columns], names=['Stat','Name'])
	print('follower_count_baseline:\n', follower_count_baseline)
	# Join the new Series to the df:
	df_2019 = df_2019.join(follower_count_baseline)
	# Convert all data to integers
	df_2019 = df_2019.astype(dtype='int32', copy=True)
	print('df_2019:\n', df_2019.to_string())


	# Questions: For each candidate...
	# 1. Raw follower growth from baseline on January 1, 2019, and average rate of follower growth
	# 2. % growth for each candidate, total follower count (Candidates with fewer followers can experience higher growth rates)
	# 3. Weekly % growth bar plot
	# 4. Percent of total growth amongst all candidates over the last X weeks

	# 1.
	df_count_based = df_2019.loc[:, 'Total Follower Count Based']
	print('df_count_based:\n', df_count_based)

	df_growth = df_2019.loc[:, 'Daily Followers Gained'].melt(value_name='Growth')
	# Calculating the averages, broadcasting to tidy formatted data for sorting,
	# hence why I use transform instead of apply, sorting by average, then dropping
	# the average column.
	# df_growth['Avg'] = df_growth.groupby('Name').transform('mean')
	# print('df_growth:\n', df_growth)
	# df_growth.sort_values(by='Avg', ascending=False, inplace=True)
	# df_growth.drop('Avg', axis=1, inplace=True)
	print('df_growth:\n', df_growth)

	cmap = plt.get_cmap('tab20c')
	colors = cmap(np.arange(len(df_count_based.columns))) # np.arange(3)*4)
	
	fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,4))
	df_count_based.plot(use_index=True, ax=ax1, color=colors)
	sns.barplot(x='Name', y='Growth', data=df_growth, estimator=np.mean, ax=ax2, capsize=0.2, palette=colors)
	ax1.set_xlabel('Day')
	ax1.set_ylabel('Followers')
	ax2.set_xlabel('Candidate')
	ax2.set_ylabel('Avg. Growth Rate, Followers/Day')
	plt.xticks(rotation=90)
	plt.subplots_adjust(left=0.1, bottom=0.2, wspace=0.3)
	plt.savefig('twitter_metrics__followers_gained.png', bbox_inches='tight')
	plt.show()
	# Buttigieg leads in the follower count growth and growth rate metric

	# 2. Percent growth:
	# Calculating percent growth since Jan 1 2019
	end_date = df_2019.index[-1].date()
	print('end_date:\n', end_date)
	print('last value:\n', df_2019.loc[end_date, 'Total Follower Count Based'])
	df_pcnt_growth = df_2019.loc[end_date, 'Total Follower Count Based'] / df_2019.loc['2019-01-01', 'Total Follower Count'] * 100
	print('Pcnt growth since Jan 1 2019:\n', df_pcnt_growth)
	df_pcnt_growth = df_pcnt_growth.sort_values(ascending=False).rename('Pcnt Growth')
	print('Pcnt growth since Jan 1 2019:\n', df_pcnt_growth)

	# Raw follower growth since Jan 1 2019
	print('df_2019:\n', df_2019)
	print('df_2019.iloc[-1]:\n', df_2019.iloc[-1])
	df_follower_growth = df_2019.loc[end_date, 'Total Follower Count Based'].rename('Follower Growth')
	print('Follower growth since Jan 1 2019:\n', df_follower_growth)
	print('df_follower_growth.name:\n', df_follower_growth.name)

	# Getting total number of followers:
	# Candidates like Biden haven't grown much this year but have enormous followings.
	# Making df_follower_count because it's used to make df_pcnt_growth later.
	df_follower_count = df_2019.loc[:, 'Total Follower Count']
	print('df_follower_count:\n', df_follower_count)
	df_total_followers = df_follower_count.max().sort_values(ascending=False).rename('Total Followers')
	print('df_total_followers:\n', df_total_followers)
	# Combining into one df:
	df_combined = pd.concat((df_pcnt_growth, df_follower_growth, df_total_followers), axis=1, sort=True).sort_values(by='Pcnt Growth', ascending=False) # No need to use .rename({0:'Pcnt Growth', 1:'Follower Growth', 2:'Total Followers'}, axis=1)
	print('df_combined:\n', df_combined)

	# Plot:
	plt.close()
	fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,5))
	df_combined.loc[:, ['Pcnt Growth', 'Total Followers']].plot.bar(use_index=True, secondary_y='Total Followers', ax=ax1, color=['blue','orange'], alpha=0.7)
	df_combined.loc[:, ['Pcnt Growth', 'Follower Growth']].plot.bar(use_index=True, secondary_y='Follower Growth', ax=ax2, color=['blue','green'], alpha=0.7)
	ax1.set_xlabel('Candidate')
	ax1.set_ylabel('Pcnt Growth (Jan 1 - Present)')
	ax2.set_xlabel('Candidate')
	ax2.set_ylabel('Pcnt Growth (Jan 1 - Present)')
	# plt.yscale('log')
	plt.xticks(rotation=90)
	plt.subplots_adjust(wspace=0.3)
	plt.savefig('twitter_metrics__pcnt_growth_and_total_followers.png', bbox_inches='tight')
	plt.show()

	# 3. Weekly percent growth and raw growth bar plot for each candidate:
	# First, transform df_follower_count into df_pcnt_growth_weekly
	print('df_follower_count from above:\n', df_follower_count)
	print('duplicate columns:\n', df_follower_count.index.duplicated().sum())
	print('index:\n', df_follower_count.index)
	# Resample to weekly, get max follower count for the week, percent change week to week, drop NaNs, only get last X weeks
	df_pcnt_growth_weekly = df_follower_count.resample(weekly_freq).max().pct_change().dropna().iloc[-weeks:-1]*100 # *100 converts to a readable percentage
	print('df_pcnt_growth_weekly.index before date conversion:\n', df_pcnt_growth_weekly.index)
	print('df_pcnt_growth_weekly.index before date conversion:\n', df_pcnt_growth_weekly.index)
	df_pcnt_growth_weekly.reset_index(inplace=True)
	df_pcnt_growth_weekly.Date = df_pcnt_growth_weekly.Date.dt.date
	df_pcnt_growth_weekly.set_index('Date', inplace=True)
	print('df_pcnt_growth_weekly.index after date conversion:\n', df_pcnt_growth_weekly.index)
	print('df_pcnt_growth_weekly.index after date conversion:\n', df_pcnt_growth_weekly.index.dtype)

	# Transpose so the candidate names are the index and appear in the x-axis in the bar plot
	df_pcnt_growth_weekly = df_pcnt_growth_weekly.T
	print('df_pcnt_growth_weekly:\n', df_pcnt_growth_weekly)
	# Need to get raw growth change for each week from Daily Followers Gained column:
	df_raw_growth_weekly = df_2019.loc[:, 'Daily Followers Gained']
	df_raw_growth_weekly = df_raw_growth_weekly.resample(weekly_freq).sum().dropna().iloc[-weeks:-1]
	print('df_raw_growth_weekly:\n', df_raw_growth_weekly)
	
	# Interesting stat: Candidate with the max raw growth for every week:
	max_growth_weekly = df_raw_growth_weekly.idxmax(axis=1)
	print('max_growth_weekly:\n', max_growth_weekly)
	# Yang and Warren dominate over June 27 to August 16

	df_raw_growth_weekly.reset_index(inplace=True)
	df_raw_growth_weekly.Date = df_raw_growth_weekly.Date.dt.date
	df_raw_growth_weekly.set_index('Date', inplace=True)
	df_raw_growth_weekly = df_raw_growth_weekly.T
	print('df_raw_growth_weekly:\n', df_raw_growth_weekly)
	
	# Plot
	plt.close()
	alpha_50 = '#a8a8a8'
	fig, ax = plt.subplots(figsize=(14,5))
	df_pcnt_growth_weekly.plot.bar(use_index=True, ax=ax)
	ax2 = df_raw_growth_weekly.plot.bar(use_index=True, secondary_y=True, legend=False, ax=ax, alpha=0.5) # Need to assign to ax2 to get ax2.set_ylabel to work
	ax.set_xlabel('Candidate')
	ax.set_ylabel('Follower Growth Rate, %/Week')
	ax.set_ylim(0, df_pcnt_growth_weekly.values.max()+5)
	ax2.set_ylabel('Follower Growth Rate, Followers/Week', color=alpha_50)
	ax2.tick_params(axis='y', color=alpha_50, labelcolor=alpha_50)
	ax2.set_ylim(0, df_raw_growth_weekly.values.max()+2000)
	plt.subplots_adjust(left=0.1, right=0.9, bottom=0.3)
	plt.savefig('twitter_metrics__percent_growth.png', bbox_inches='tight')
	plt.show()

	# 4. Growth comparison pie chart
	# Compare who is owning what percent of the total raw twitter growth in the last two weeks
	df = df_2019.loc['2019-07-29':'2019-08-14', 'Total Follower Count']
	df_raw_growth = (df.max() - df.min()) # Get raw growth in last couple weeks. Pie chart below automatically calculates percentage share of growth.
	# df_raw_growth_ownership = (df_raw_growth / df_raw_growth.sum() * 100).sort_values(ascending=False).round(1) # Divide by the sum of all candidates' raw growth
	# print('df_raw_growth_ownership:\n', df_raw_growth_ownership)

	# Plot
	size = 0.27
	vals = df_raw_growth
	cmap = plt.get_cmap("tab20c")
	outer_colors = cmap(np.arange(len(vals))) # np.arange(3)*4)

	# inner_colors = cmap(np.array([1, 2, 5, 6, 9, 10]))
	plt.close()
	fig, ax = plt.subplots()
	ax.pie(vals, radius=1, colors=outer_colors, labels=vals.index, autopct='%1.1f%%', wedgeprops=dict(width=size, edgecolor='w'))
	# ax.pie(vals.flatten(), radius=1-size, colors=inner_colors, wedgeprops=dict(width=size, edgecolor='w'))
	ax.set(aspect="equal", title='Share of Follower Growth:\nJuly 29 - Aug 13, 2019')
	plt.savefig('twitter_metrics__share_of_followers_gained.png', bbox_inches='tight')
	plt.show()

	return



def OddsPollsCorrelation():

	df_dem_odds = pd.read_pickle('/home/dp/Documents/Campaign/pickle/BettingOdds_df_dem_odds.pkl')
	df_dem_polls = pd.read_pickle('/home/dp/Documents/Campaign/pickle/NationalPolling_df.pkl')

	df_dem_odds.index = pd.to_datetime(df_dem_odds.index)
	df_dem_polls.index = pd.to_datetime(df_dem_polls.index)

	print('df_dem_odds:\n', df_dem_odds.to_string())
	print('df_dem_polls:\n', df_dem_polls.to_string())

	# Format Odds index (Time or Date) to Date, then average each day. Typically
	# I make multiple reads of the betting data per day.
	df_dem_odds.reset_index(inplace=True, drop=True)
	df_dem_odds['Date'] = df_dem_odds['Time'].dt.date
	df_dem_odds_day_avg = df_dem_odds.groupby(['Date']).mean()
	# df_dem_odds_day_avg.columns = [col+'_odds' for col in df_dem_odds_day_avg.columns]
	# print('df_dem_odds_day_avg:\n', df_dem_odds_day_avg)
	# NOTE: INDEX IS AUTO-SET TO 'DATE' DURING GROUPBY

	# Format Polls index (Time or Date) to Date, then average each day. Sometimes
	# there may be two polls released in one day.
	df_dem_polls.reset_index(inplace=True)
	df_dem_polls['Date'] = df_dem_polls['Date'].dt.date
	df_dem_polls_day_avg = df_dem_polls.groupby(['Date']).mean()
	# df_dem_polls_day_avg.columns = [col+'_polls' for col in df_dem_polls_day_avg.columns]
	# df_dem_polls_day_avg.set_index('Date', inplace=True)
	# NOTE: INDEX IS AUTO-SET TO 'DATE' DURING GROUPBY

	# print('df_dem_odds_day_avg:\n', df_dem_odds_day_avg.to_string())
	# print('df_dem_odds_day_avg.columns:\n', df_dem_odds_day_avg.columns)
	# print('df_dem_odds_day_avg[Biden]:\n', df_dem_odds_day_avg['Biden'])
	# print('df_dem_polls_day_avg.columns:\n', df_dem_polls_day_avg.columns)
	# print('df_dem_polls_day_avg[Biden ]:\n', df_dem_polls_day_avg['Biden '])

	# NOTE: THE CONCATENATION ADDS A SPACE TO ANY NAMES THAT ARE DUPLICATES.
	# BOTH DATAFRAMES HAVE THE SAME NAMES, RESULTING IN THE POLLING NAMES
	# HAVING A SINGLE SUCCEEDING SPACE
	# candidate_odds = candidate+'_odds'
	# candidate_polls = candidate+'_polls'
	# df_concat_candidate = pd.concat((df_dem_odds_day_avg[candidate_odds],df_dem_polls_day_avg[candidate_polls]), axis=1, ignore_index=False, join='inner')
	# df_concat = pd.concat((df_dem_odds_day_avg, df_dem_polls_day_avg), axis=1, ignore_index=False, join='inner')

	# print('df_concat:\n', df_concat.to_string())

	# ---------------------------------------------------------------------------------------
	# Currently df_dem_odds_day_avg and df_dem_polls_day_avg are formatted with candidates
	# as columns:
	# Date         Biden  Booker
	# 2019-03-25   19.6   2.0
	# 2019-04-01   12.1   2.1
	# 
	#
	# Reformat the odds and polls dataframes with candidates in one column (e.g. tidy format):
	# Candidate   Date         Odds  Polls
	# Biden       2019-03-25   19.6  20
	#			  2019-04-01   11.1  32
	# 
	# The reformat is accomplished by stack(), resetting the index (not sure why I need to name it 'Odds'),
	# then renaming the new column to 'Candidate' containing candidate names that were previously columns
	# Set the index to candidate and date, then sort the index.

	df_dem_odds_day_avg_stack = df_dem_odds_day_avg.stack().reset_index(name='Odds').rename(columns={'level_1':'Candidate'})
	df_dem_odds_day_avg_stack.set_index(['Candidate','Date'], inplace=True)
	df_dem_odds_day_avg_stack.sort_index(level=0, inplace=True)
	print('df_dem_odds_day_avg_stack:\n', df_dem_odds_day_avg_stack)

	df_dem_polls_day_avg_stack = df_dem_polls_day_avg.stack().reset_index(name='Polls').rename(columns={'level_1':'Candidate'})
	df_dem_polls_day_avg_stack.set_index(['Candidate','Date'], inplace=True)
	df_dem_polls_day_avg_stack.sort_index(level=0, inplace=True)
	print('df_dem_polls_day_avg_stack:\n', df_dem_polls_day_avg_stack)

	a = df_dem_odds_day_avg_stack.loc[['Biden','2019-04-11']]
	print('a:\n', a)
	b = df_dem_polls_day_avg_stack.loc[['Biden','2019-04-11']]
	print('b:\n', b)

	# NOTE: THE RESULT OF THIS CONCATENATION LOOKS LIKE A MESS. NOT SURE WHY, BUT SORTING THE INDEX FIXES THE PROBLEM.
	# THE NON-CONCATENATION AXIS (ROWS) ARE NOT ALIGNED, AND THEREFORE NEED TO BE SORTED, DO SO BY SPECIFYING sort=True:
	df_odds_polls = df_dem_polls_day_avg_stack.join(df_dem_odds_day_avg_stack)
	print('df_odds_polls:\n', df_odds_polls.to_string())

	df_odds_polls['OddsPollsRatio'] = df_odds_polls['Odds']/df_odds_polls['Polls']
	df_odds_polls.replace(np.inf, np.nan, inplace=True) # Odds/Polls = 4.15/0.00 = inf. Replacing all inf.
	print('df_odds_polls:\n', df_odds_polls)

	candidate_list = df_odds_polls.index.get_level_values(0).unique().tolist()
	print('candidate list:\n', candidate_list)

	corr_list = []
	# Iterate through the candidate index and calculate the Odds-Polls correlation:
	for candidate in candidate_list:
		corr = df_odds_polls.loc[candidate]['Odds'].corr(df_odds_polls.loc[candidate]['Polls'])
		corr_list.append(corr)
	candidate_corr_list = [(x,y) for x,y in zip(candidate_list, corr_list)]
	df_candidate_corrs = pd.DataFrame(data=candidate_corr_list, columns=['Candidate', 'Correlation'])
	df_candidate_corrs.set_index('Candidate', drop=True, inplace=True)
	print('df_candidate_corrs:\n', df_candidate_corrs)
	# ---------------------------------------------------------------------------------------

	# Markers list for plots
	markers = ['o','s','D','v','^','<','>','+','d', '.','s','D','v','^','<','>','+','d','x'] # Unique markers for each candidate
	num_candidates = len(candidate_list)
	markers = markers[0:num_candidates]
	# ---------------------------------------------------------------------------------------
	# Bar plot of Correlation vs Candidate:
	f, ax = plt.subplots(figsize=(6,4))
	plt.gcf()
	df_candidate_corrs.plot.bar(y='Correlation', ax=ax, title='Candidate Odds-Polls Correlation', legend=False, color='gray')
	ax.set_xlabel('Candidate')
	ax.set_ylabel('Correlation, %')
	# plt.title('Odds-Polls Correlation')
	plt.savefig('Odds_Polls_Correlation.png', bbox_inches='tight')
	plt.show()
	# ---------------------------------------------------------------------------------------
	# Scatter of Odds vs Polls:
	df_odds_polls.reset_index(inplace=True) # Resetting index to make 'Candidate' available for 'hue' in sns pairplot

	p = sns.pairplot(x_vars='Polls', y_vars='Odds', data=df_odds_polls, hue='Candidate', height=5, markers=markers)
	p.set(xlim=(0,45))
	p.set(ylim=(0,45))
	# p.set(title='Betting Odds vs Polls')
	plt.savefig('Odds_vs_Polls.png', bbox_inches='tight')
	plt.show()
	# ---------------------------------------------------------------------------------------
	# Boxplot of odds:polls ratio for each candidate.
	# Averaging each candidates Odds and Polls data to create a ratio.
	df_odds_polls_ratio_sorted_avg = df_odds_polls[['Candidate','OddsPollsRatio']].groupby('Candidate').mean()
	df_odds_polls_ratio_sorted_avg.rename(columns={'OddsPollsRatio':'OddsPollsRatioAvg'}, inplace=True)
	df_odds_polls_ratio_sorted_avg.sort_index(by='OddsPollsRatioAvg', ascending=True, inplace=True)
	print('df_odds_polls_ratio_sorted_avg:\n', df_odds_polls_ratio_sorted_avg)
	order = df_odds_polls_ratio_sorted_avg.index.values.tolist()
	
	p = sns.boxplot(x='Candidate', y='OddsPollsRatio', order=order, data=df_odds_polls)
	p.set(ylabel='Betting Odds:National Polls')
	p.set_xticklabels(p.get_xticklabels(),rotation=30)
	# p.set(title='2020 Democratic Primary: Betting Odds - to - National Polls Ratio')
	print('df_odds_polls:\n', df_odds_polls)

	start_dt = df_odds_polls.Date.iloc[0].date().strftime('%b %d, %Y')
	end_dt = df_odds_polls.Date.iloc[-1].date().strftime('%b %d, %Y')
	plt.annotate('Time period: {} - {}\nBetting odds: electionbettingodds.com\nPolls: realclearpolitics.com'.format(start_dt, end_dt), xy=(-0.15,4.7))
	plt.savefig('Odds_to_Polls_Ratio.png', bbox_inches='tight')
	plt.show()

	# ---------------------------------------------------------------------------------------
	# Importing name recognition data:
	df = pd.read_csv('/home/dp/Documents/Campaign/CandidateNameRecognition.csv', header='infer')
	# print('df:\n', df)
	# print('df.columns:\n', df.columns)

	# Removing first names from df['Candidate']
	df.columns = df.columns.map(lambda x: str(x).replace(' ',''))
	candidates = df['Candidate'].values.tolist()
	space_index = [str(c).index(' ') for c in df['Candidate']]
	last_names = [c[i+1:] for c,i in zip(candidates, space_index)]
	df['Candidate'] = last_names

	# Removing the ' in O'Rourke:
	df['Candidate'] = df['Candidate'].map(lambda x: str(x).replace('\'',''))
	
	# Removing all % from column data, iterating through each column.
	# IS THERE A WAY TO REMOVE ALL %'S WITHOUT ITERATING THROUGH EACH COLUMN?
	for col in df.columns:
		df[col] = df[col].map(lambda x: str(x).replace('%',''))
		df[col] = pd.to_numeric(df[col], errors='ignore')

	# print('df after numeric conversion:\n', df)
	# print('df data types:\n', df.dtypes)

	df['UFR'] = df['Unfavorable']/df['Favorable']
	df['HO'] = 100 - df['NHO']

	df_name_rec = df
	df_name_rec.set_index('Candidate', inplace=True)
	print('df_name_rec:\n', df_name_rec)

	df_odds_polls_avg = df_odds_polls.groupby('Candidate').mean()
	print('df_odds_polls_avg:\n', df_odds_polls_avg)

	print('df_name_rec.index.dtype:\n', df_name_rec.index.dtype)
	print('df_odds_polls_avg.index.dtype:\n', df_odds_polls_avg.index.dtype)

	# df_odds_polls_name_rec = pd.concat((df_name_rec, df_odds_polls_ratio_sorted_avg), axis=1, ignore_index=False)
	df_odds_polls_name_rec = df_name_rec.join(df_odds_polls_avg, how='inner')
	print('df_odds_polls_name_rec:\n', df_odds_polls_name_rec)

	df_odds_polls_name_rec['OddsHORatio'] = df_odds_polls_name_rec['Odds'] / df_odds_polls_name_rec['HO']
	df_odds_polls_name_rec['PollsHORatio'] = df_odds_polls_name_rec['Polls'] / df_odds_polls_name_rec['HO']
	df_odds_polls_name_rec['Polarization'] = df_odds_polls_name_rec['Unfavorable'] / df_odds_polls_name_rec['Favorable']
	# Ceiling:
	df_odds_polls_name_rec['Agnostic'] = df_odds_polls_name_rec['NHO'] + df_odds_polls_name_rec['HONO']
	df_odds_polls_name_rec['PollsCeiling'] = df_odds_polls_name_rec['Agnostic'] / df_odds_polls_name_rec['Polls']
	df_odds_polls_name_rec['FavCeiling'] = df_odds_polls_name_rec['Agnostic'] / df_odds_polls_name_rec['Favorable']
	df_agnostic = df_odds_polls_name_rec['Agnostic'].sort_values()
	df_polls_ceiling = df_odds_polls_name_rec['PollsCeiling'].sort_values()
	df_fav_ceiling = df_odds_polls_name_rec['FavCeiling'].sort_values()
	print('df_polls_ceiling:\n', df_polls_ceiling)
	print('df_fav_ceiling:\n', df_fav_ceiling)
	print(df_fav_ceiling.index)
	print(df_fav_ceiling.values)



	# Plotting Odds to Heard-of ratio, Polls to Heard-of ratio:
	f, ax1 = plt.subplots(figsize=(5,4))
	df_odds_polls_name_rec.sort_values(by='OddsHORatio', inplace=True)
	df_odds_polls_name_rec.plot.bar(y='OddsHORatio', use_index=True, ax=ax1)
	plt.show()
	plt.close()
	f, ax2 = plt.subplots(figsize=(5,4))
	df_odds_polls_name_rec.sort_values(by='PollsHORatio', inplace=True)
	df_odds_polls_name_rec.plot.bar(y='PollsHORatio', use_index=True, ax=ax2)
	plt.show()
	plt.close()
	f, ax3 = plt.subplots(figsize=(5,4))
	df_odds_polls_name_rec.sort_values(by='Polarization', inplace=True)
	df_odds_polls_name_rec.plot.bar(y='Polarization', use_index=True, ax=ax3)
	plt.show()

	# Ceilings:
	agnostic_palette = []
	for c_agnostic in df_agnostic.index:
		if c_agnostic == 'Yang' or c_agnostic == 'Gabbard':
			agnostic_palette.append('#004ecc')
		else:
			agnostic_palette.append('#aaaaaa')

	polls_ceil_palette = []
	for c_polls in df_polls_ceiling.index:
		if c_polls == 'Yang' or c_polls == 'Gabbard':
			polls_ceil_palette.append('#004ecc')
		else:
			polls_ceil_palette.append('#aaaaaa')

	fav_ceil_palette = []
	for c_fav in df_polls_ceiling.index:
		if c_fav == 'Yang' or c_fav == 'Gabbard':
			fav_ceil_palette.append('#004ecc')
		else:
			fav_ceil_palette.append('#aaaaaa')
	# print('fav_ceil_palette:\n', fav_ceil_palette)

	# % Agnostic voters
	plt.close()
	f, ax = plt.subplots(figsize=(5,4))
	sns.barplot(x=df_agnostic.index, y=df_agnostic.values, palette=agnostic_palette, ax=ax)
	ax.set_ylabel('% Agnostic')
	ax.set_xticklabels(df_agnostic.index, rotation=90)
	plt.savefig('Odds_Polls_Correlation__Pcnt_Agnostic.png', bbox_inches='tight')
	plt.show()
	
	plt.close()
	f, (ax1, ax2) = plt.subplots(1,2, figsize=(9,4))
	sns.barplot(x=df_polls_ceiling.index, y=df_polls_ceiling.values, palette=polls_ceil_palette, ax=ax1)
	sns.barplot(x=df_fav_ceiling.index, y=df_fav_ceiling.values, palette=fav_ceil_palette, ax=ax2)
	ax1.set_ylabel('% Agnostic / % Polling')
	ax2.set_ylabel('% Agnostic / % Favorable')
	ax1.set_xticklabels(df_polls_ceiling.index, rotation=90)
	ax2.set_xticklabels(df_fav_ceiling.index, rotation=90)
	ax1.annotate('Agnostic: % of all Americans who\nare undecided or unaware.\nSource: morningconsult.com\nPolling: realclearpolitics.com', xy=(-0.15, 70.0))
	ax2.annotate('Favorable: % of all Americans who\nview the candidate favorably.\nSource: morningconsult.com', xy=(-0.15,3.6))
	plt.subplots_adjust(wspace=0.2)
	plt.suptitle('Room for Growth in Polls and Favorability Among Undecided Voters')
	plt.savefig('Odds_Polls_Correlation__Polls_Favorability_Ceilings.png', bbox_inches='tight')
	plt.show()

	return



def NameRecognition():
	df = pd.read_csv('/home/dp/Documents/Campaign/CandidateNameRecognition.csv', header='infer')
	# print('df:\n', df)
	# print('df.columns:\n', df.columns)

	# Removing first names from df['Candidate']
	df.columns = df.columns.map(lambda x: str(x).replace(' ',''))
	candidates = df['Candidate'].values.tolist()
	space_index = [str(c).index(' ') for c in df['Candidate']]
	last_names = [c[i+1:] for c,i in zip(candidates, space_index)]
	df['Candidate'] = last_names

	# Removing the ' in O'Rourke:
	df['Candidate'] = df['Candidate'].map(lambda x: str(x).replace('\'',''))

	# Removing all % from column data, iterating through each column.
	# IS THERE A WAY TO REMOVE ALL %'S WITHOUT ITERATING THROUGH EACH COLUMN?
	for col in df.columns:
		df[col] = df[col].map(lambda x: str(x).replace('%',''))
		df[col] = pd.to_numeric(df[col], errors='ignore')

	# print('df after numeric conversion:\n', df)
	# print('df data types:\n', df.dtypes)

	df['UFR'] = df['Unfavorable']/df['Favorable']
	df['HO'] = 100 - df['NHO']

	# -----------------------------------------------
	# Bar plots of all stats:
	f, (ax1,ax2,ax3,ax4) = plt.subplots(1,4, figsize=(14,3))
	df.plot.bar(x='Candidate', y='Favorable', ax=ax1)
	df.plot.bar(x='Candidate', y='HONO', ax=ax2)
	df.plot.bar(x='Candidate', y='NHO', ax=ax3)
	df.plot.bar(x='Candidate', y='Unfavorable', ax=ax4)
	plt.show()

	# -----------------------------------------------
	# Plot: Unfavorability to Favorability ratio:
	# Unfavorability to Favorability ratio sorted
	df.sort_values(by='UFR', axis=0, inplace=True)
	print('df after sorting by UFR:\n', df)

	plt.close()
	f, ax = plt.subplots(figsize=(5,4))
	df.plot.bar(x='Candidate', y='UFR', ax=ax)
	plt.show()

	# -----------------------------------------------
	df.sort_values(by='HO', axis=0, inplace=True)
	print('df after sorting by HO:\n', df)

	plt.close()
	f, ax = plt.subplots(figsize=(5,4))
	df.plot.bar(x='Candidate', y='HO', ax=ax)
	plt.show()

	return


''' ----------------------------------------- Campaign 2020 ----------------------------------------- '''

# ''' Initialize donor dict and dataframe. Only do once. '''
# donor_dict = {	'time':[],
# 				'donor_count':[],
# 				'donor_goal':[],
# 				'donor_percent':[]}
# df = pd.DataFrame(data=donor_dict, columns=['Time','Count','Goal','Pcnt'])
# ''' -------------------------------------------------- '''


''' --- Run YangDonorCounter() --- '''
# WARNING: THE DONOR COUNTER HAS BEEN REPLACED BY A MONEY COUNTER.
# RUN YangMoneyRaised() INSTEAD.
# YangDonorCounter()
''' -------------------------- '''

''' --- Run YangMoneyRaised() --- '''
YangMoneyRaised()
''' --------------------------- '''


''' --- Scheduling the YangDonorCounter() data collection: --- '''
''' --- Uncomment to schedule YangDonorCounter(), specify time --- '''
# Seconds can be replaced with minutes, hours, or days
# sched.start()
# sched.add_job(DonorCounter, 'interval', seconds=3)
# while True:
#     time.sleep(1)
# sched.shutdown()

''' --- Federal Election Commission --- '''
# df = FEC()
''' ----------------------------------- '''


''' --- Run NationalPolling() --- '''
# NationalPolling()
''' ----------------------------- '''


''' ----------------------------------------- CampaignBetting() ----------------------------------------- '''

''' --- Initialize dem, rep, and pres dictionaries and dataframes. --- '''
''' Only do once. Not sure if this code is doing anything '''
# dem_dict = {}; rep_dict = {}; pres_dict = {};
# df_dem = pd.DataFrame([]); df_rep = pd.DataFrame([]); df_pres = pd.DataFrame([])
# df_dem_field = pd.DataFrame([]); df_rep_field = pd.DataFrame([]); df_pres_field = pd.DataFrame([])
''' ------------------------------------------------------------------ '''


''' --- Run CampaignBetting() --- '''
CampaignBetting()
PlotCampaignBetting()
# --- Sorting Campaign ---
# Only run if there's an issue
# with betting odds getting
# matched to the wrong candidates:
# SortCampaignBettingCSV()
''' --------------------------- '''

''' --- Run OddsPollsCorrelation() --- '''
# OddsPollsCorrelation()
''' ---------------------------------- '''

''' --- Run NameRecognition() --- '''
# NameRecognition()
''' ---------------------------------- '''


''' ----------------------------------------- WebMetrics() ----------------------------------------- '''

''' --- Run WebMetrics() --- '''
# df_all = WebMetrics()   # WARNING: RUNNING THIS WILL NOT UPDATE CURRENT CSV DATA BUT WILL OVERWRITE IT WITH
# 						# THE LATEST 30 DAYS OF TWITTER DATA. CURRENT CSV FILES ARE BACKED UP BY DATE IN THE
# 						# FOLDER 'Campaign/TwitterMetrics csv backup'. WebMetrics() NEEDS THE CAPABILITY
# 						# TO LOAD CSV DATA, ADD THE MOST RECENT SCRAPED DATA TO IT AND WRITE BACK TO CSV.
# 						# WILL HAVE TO ADD THIS CAPABILITY AT SOME POINT BUT FOR NOW COPY AND PASTE WILL BE USED.
# PlotWebMetrics(8, 'W-FRI')		# For trend plots, plot 7 weeks into the past, weekly frequency to 'W-SAT' or any of your choice
''' ------------------------- '''


