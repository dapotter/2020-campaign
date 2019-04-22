# Operating this script in Conda environment 'fwp_venv'
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
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

import tabula
import PyPDF2

import re

import glob
import os

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
	time.sleep(3) # Allow the user see website load
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

	# Pickle out:
	DonorCountYang_df_pkl = df.to_pickle('/home/dp/Documents/Campaign/pickle/DonorCountYang_df.pkl')

	# ''' Make projection for 200,000 donors '''
	# Data from Time and Count column for 7 days prior to the current date
	# Fit line to Count vs Time data.
	# Plug 200,000 into y-value, solve for x (date)
	# Put date value into plot: 'Projected 200,000 donors'

	current_time = datetime.datetime.now()
	print('current time:', current_time)
	one_wk_timedelta = datetime.timedelta(days=7)
	print('one_wk_timedelta:', one_wk_timedelta)
	one_wk_prior_time = current_time - one_wk_timedelta
	print('one_wk_prior_time:', one_wk_prior_time)
	
	
	df['Time'] = pd.to_datetime(df['Time'])
	df.set_index('Time', inplace=True)
	df_one_wk = df.loc[one_wk_prior_time:current_time]
	print('df_one_wk:\n', df_one_wk)

	# mask = (df['Time'] >= one_wk_prior_time) & (df['Time'] <= current_time)
	# df_one_wk = df.loc[mask]
	# print('df_one_wk:\n', df_one_wk)
	dates_float = mdates.date2num(df_one_wk.index)
	print('dates_float:\n', dates_float)
	count_one_wk = df_one_wk.loc[:,'Count']
	print('df_one_wk.loc[:,"Count"]:\n', df_one_wk.loc[:,'Count'])

	pfit = np.polyfit(x=dates_float, y=count_one_wk, deg=1)
	linfit = np.poly1d(pfit)

	#df.reset_index(inplace=True)
	df_one_wk['Trendline'] = linfit(dates_float)
	print('df_one_wk with Trendline:\n', df_one_wk)

	# 200k donor prediction date:
	start_date = current_time
	date_step = datetime.timedelta(days=7)
	projected_dates = [datetime.timedelta(days=day)+current_time for day in list(range(1,400))]
	projected_dates_float = mdates.date2num(projected_dates)
	projected_donor_count = linfit(projected_dates_float)
	# print('projected_dates:', projected_dates)
	# print('projected_donor_count:\n', projected_donor_count)
	print('shape projected_donor_count:\n', np.shape(projected_donor_count))
	projected_datetime_200k = projected_dates[np.flatnonzero(projected_donor_count > 200000)[0]] # np.where also works but returns a 1-element tuple
	projected_date_200k = projected_datetime_200k.strftime('%b %d, %Y')
	print('projected_date_200k:', projected_date_200k)

	# ''' Plotting data: '''
	#fig = plt.figure()
	w = 3
	h = 3
	#fig = plt.figure(frameon=False)
	#fig.set_size_inches(w,h)
	plt.figure()
	plt.plot(df.index, df['Count'], linewidth=1, color='k', marker='o', markersize=3, markerfacecolor='none', markeredgecolor='k')
	plt.plot(df_one_wk.index, df_one_wk['Trendline'], color='r')
	plt.xlabel('DateTime'); plt.ylabel('Number of donors')
	plt.xticks(rotation=45)
	plt.legend(labels=['Donor count','7-day trend'])
	plt.title('200k donors projected date: {0}'.format(projected_date_200k))
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

	return


''' ----------------------------------------------------------------------------------------------- '''


def FEC():
	# Plots Federal Election Commission's public records of donations to each political candidate
	# Columns: contribution_receipt_date and contribution_receipt_amount

	FEC_files_path = '/home/dp/Documents/Campaign/FEC/'
	FEC_files = glob.glob(os.path.join(FEC_files_path, '*Itemized.csv')) # H500 file paths in a list

	
	fields = ['committee_name','contribution_receipt_date','contribution_receipt_amount', 'contributor_last_name'] # 'contributor_name'
	df_gen = (pd.read_csv(f, header='infer', usecols=fields) for f in FEC_files)
	df = pd.concat(df_gen, axis=0, sort=True)
	df.drop(labels = df[df['contributor_last_name']=='ActBlue'].index, axis=0, inplace=True)
	print('df:\n', df)

	FEC_contribution_size_files = glob.glob(os.path.join(FEC_files_path, '*ContributionSize.csv')) # H500 file paths in a list
	fields = ['committee_name', 'cycle', 'total', 'count', 'size']
	df_gen = (pd.read_csv(f, header='infer', usecols=fields) for f in FEC_contribution_size_files)
	df_contribution_size = pd.concat(df_gen, axis=0, sort=True)
	df_contribution_size.fillna(0, inplace=True)
	print('df_contribution_size:\n', df_contribution_size)


	# # Importing pdf files:
	# FEC_pdf_files = glob.glob(os.path.join(FEC_files_path, '*.pdf'))
	# print('FEC_pdf_files[0]:\n', FEC_pdf_files[0])

	# # PyPDF2:
	# pdfFileName = FEC_pdf_files[0] #filename of your PDF/directory where your PDF is stored
	# # creating a pdf file object
	# pdfFileObj = open(pdfFileName, 'rb')
	# # creating a pdf reader object
	# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	# # printing number of pages in pdf file
	# print(pdfReader.numPages)
	# # creating a page object
	# pageObj = pdfReader.getPage(30)
	# # extracting text from page
	# print(pageObj.extractText())
	# # closing the pdf file object
	# pdfFileObj.close()

	# # Tabula:
	# path = FEC_pdf_files[0]
	# print('pdf file path:\n', path)
	# path = path.replace('/','\\')
	# print('pdf file path formatted:\n', path)
	# # path = 'C:\\Users\\Himanshu Poddar\\Desktop\\datathon\\Himachal\\'  + file
	# df = tabula.read_pdf(path, pages = '1', multiple_tables = True)
	# print(df)



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



	''' Using Contribution Size data to determine fractions of various donation amounts: '''
	df_cs_below_200 = df_contribution_size[df_contribution_size['size']==0].set_index('committee_name')
	df_cs_200_to_499 = df_contribution_size[df_contribution_size['size']==200]
	df_cs_500_to_999 = df_contribution_size[df_contribution_size['size']==500]
	df_cs_1000_to_1999 = df_contribution_size[df_contribution_size['size']==1000]
	df_cs_above_2000 = df_contribution_size[df_contribution_size['size']==2000]
	print('df_cs_below_200:\n', df_cs_below_200)
	print('df_cs_1000_to_1999:\n', df_cs_1000_to_1999)
	df_cs_all = df_contribution_size.groupby('committee_name')['total'].sum()
	print('df_cs_all:\n', df_cs_all)
	df_cs_pcnt_below_200 = df_cs_below_200['total'] / df_cs_all * 100
	print('df_cs_pcnt_below_200:\n', df_cs_pcnt_below_200)
	df_cs_pcnt_above_2000 = df_cs_above_2000['total'] / df_cs_all * 100
	print('df_cs_pcnt_above_2000:\n', df_cs_pcnt_above_2000)


	plt.close()
	# Plotting bar plots of fraction of donors giving under $200:
	f,ax = plt.subplots(1,2, figsize=(8,4))
	df_cs_pcnt_below_200.plot.bar(use_index=True, ax=ax[0], rot=90, legend=False, color='gray')
	df_cs_pcnt_above_2000.plot.bar(use_index=True, ax=ax[1], rot=90, legend=False, color='gray')
	# df_below_200_pcnt_2019.plot.bar(use_index=True, ax=ax[0,1], rot=90, legend=False, color='#bf8957')
	# df_above_2700_pcnt.plot.bar(use_index=True, ax=ax[1,0], rot=90, legend=False, color='#3d5782')
	# df_above_2700_pcnt_2019.plot.bar(use_index=True, ax=ax[1,1], rot=90, legend=False, color='#5e85c4')
	# Modify axes:
	ax[0].set_ylabel('% Donations < $200'); ax[0].set_title('Q1 2019')
	# ax[0,1].set_title('Q1 2019')
	# ax[1,0].set_xlabel('Candidate'); ax[1,0].set_ylabel('% Donations > $2700')
	# ax[1,1].set_xlabel('Candidate')

	# Turn off x-axis labels and x-axis tick labels for top three plots:
	# x_axis = ax[0,0].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# x_axis = ax[0,1].axes.get_xaxis(); x_label = x_axis.get_label(); x_label.set_visible(False); x_axis.set_ticklabels([])
	# Savefig and show:
	plt.savefig('FEC_Pcnt_Donations_Under_200.png', bbox_inches='tight')
	plt.show()

	return

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
	f,ax = plt.subplots(2,2, figsize=(8,4))
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
	# Savefig and show:
	plt.savefig('FEC_Pcnt_Donations_Under_200.png', bbox_inches='tight')
	plt.show()


	plt.close()
	# Plotting histogram of Yang, Bernie and Klobuchar donation amounts:
	df_yang = df[df['committee_name'] == 'Yang']
	df_sanders = df[df['committee_name'] == 'Sanders']
	df_klobuchar = df[df['committee_name'] == 'Klobuchar']
	f,ax = plt.subplots(1,3, figsize=(8,4))
	df_yang.hist(column='contribution_receipt_amount', ax=ax[0], bins=100, rwidth=0.95)
	df_sanders.hist(column='contribution_receipt_amount', ax=ax[1], bins=100, rwidth=0.95)
	df_klobuchar.hist(column='contribution_receipt_amount', ax=ax[2], bins=100, rwidth=0.95)
	# Modify axes:
	ax[0].set_xlim(-50,5000)
	ax[0].set_title('Yang Donations')
	ax[0].set_xlabel('Donation Amount')
	ax[0].set_ylabel('Donation Count')
	ax[1].set_xlim(-50,5000)
	ax[1].set_title('Sanders Donations')
	ax[1].set_xlabel('Donation Amount')
	ax[2].set_xlim(-50,5000)
	ax[2].set_title('Klobuchar Donations')
	ax[2].set_xlabel('Donation Amount')
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
	df_stats['sum'] = df_stats['sum'] / 100000
	df_stats['count'] = df_stats['count'] / 1000
	print('df_stats:\n', df_stats)


	plt.close()
	# Plotting: Time Series of cumulative sum of donation amounts
	df_timeseries_donation_amount = df.set_index('contribution_receipt_date')[['committee_name', 'contribution_receipt_amount']]
	df_timeseries_donation_amount['cumsum'] = df_timeseries_donation_amount.groupby('committee_name')['contribution_receipt_amount'].apply(lambda x: x.cumsum())
	df_timeseries_donation_amount.groupby('committee_name')['cumsum'].plot(y='cumsum', legend=True)
	print('df_timeseries_donation_amount:\n', df_timeseries_donation_amount)
	plt.ylabel('Cumulative Donation Amount, $')
	plt.xlabel('Date')
	plt.savefig('FEC_Donation_Time_Series.png', bbox_inches='tight')
	plt.show()


	plt.close()
	# Plotting: Total donation amount, unique donors, average donation amount:
	fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(3,10))
	df_stats.plot.bar(y='sum', use_index=True, ax=ax[0], rot=0, legend=False, color='gray')
	df_stats.plot.bar(y='count', use_index=True, ax=ax[1], rot=0, legend=False, color='k')
	df_stats.plot.bar(y='mean', yerr='std', use_index=True, ax=ax[2], rot=0, legend=False, color='r')
	df.boxplot(column='contribution_receipt_amount', by='committee_name', ax=ax[3], rot=0)
	# Modify axes:
	ax[0].set_ylabel('Donation Total, $100k')
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
	plt.savefig('FEC_Donation_Data', bbox_inches='tight')
	plt.show()


	return


''' ----------------------------------------------------------------------------------------------- '''


def NationalPolling():
	df = pd.read_csv('/home/dp/Documents/Campaign/NationalPolling.csv', sep=',')
	print('df:\n', df.to_string())
	unparsed_dates = df['Date'].values.tolist()
	parsed_dates = [s[0:s.rindex('- ')].replace('- ','').replace(' ','') for s in unparsed_dates]
	print('df:\n', df.to_string())

	years = df['Year']
	complete_dates = [d+'/'+str(y) for d,y in zip(parsed_dates, years)]
	formatted_dates = [datetime.datetime.strptime(d, '%m/%d/%Y') for d in complete_dates]
	#print('formatted_dates:', formatted_dates)
	df['Date'] = formatted_dates
	print('df.iloc[10,"Date"]:\n', type(df['Date'].iloc[10]))
	df.drop('Year', axis=1, inplace=True)
	#print('-- character:\n', df.loc[df['Date']=='2019-03-25','Yang'])
	df.replace('--', np.nan, inplace=True)

	df.set_index('Date', inplace=True)
	print('df:\n', df.to_string())

	# Removing the apostrophe from O'Rourke
	df.columns = [s.replace("'","") for s in df.columns]
	# Dropping 'Poll' column
	candidates = df.columns[1:]
	df = df[candidates].apply(pd.to_numeric, errors='coerce')
	
	# Data associated with duplicate dates are averaged
	df = df.groupby(df.index).mean()

	print('df:\n', df.to_string())

	NationalPolling_df_pkl = df.to_pickle('/home/dp/Documents/Campaign/pickle/NationalPolling_df.pkl')

	print('Democratic Primary Candidates:\n', candidates)
	df.plot(y=candidates, title='National Polling - Democratic Primary')
	plt.show()

	return
''' --------------------------------------------------------------------------------------------- '''


def CampaignBetting():
	# soup = bs.BeautifulSoup(html_source, 'lxml')
	# print('soup')
	# tables = soup.findAll('table', {'src': 'detail'})

	# for table in tables:
 #     if table.findParent("table") is None:
 #         print str(table)

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
	# Not using this: name_pcnt_list = [[i,j] for i,j in zip(name_list,pcnt_list)]



	print('scraped name_list:\n', name_list)
	print('scraped pcnt_list:\n', odds_list)
	print('len scraped name_list:', len(name_list))
	print('len scraped pcnt_list:', len(odds_list))

	# Finding 'Other' in the names list to split the list into Democratic, Republican and Presidential primaries
	# A better way would be to grab each list with independent calls
	# [add 1 to every element x of [16, 47, 53 <- indices where 'Other' is located]]
	# Results in [17, 48, 54]
	end_indices = [x+1 for x in [i for i, n in enumerate(name_list) if n == 'Other']]
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

	return df_dem, df_rep, df_pres, df_dem_field, df_rep_field, df_pres_field



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
	fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(8,4))
	print('ax:\n', ax); print('fig:\n', fig)
	df_dem_odds_top.plot(y=dem_odds_cols, use_index=True, title='Democratic Primary', ax=ax[0]); ax[0].set_ylabel('Odds, %')
	df_rep_odds_top.plot(y=rep_odds_cols, use_index=True, title='Republican Primary', ax=ax[1])
	df_pres_odds_top.plot(y=pres_odds_cols, use_index=True, title='Presidential Race', ax=ax[2])
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
		csv_filename_base = '/home/dp/Documents/Campaign/Plots/' + 'TwitterMetrics_'
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


def PlotWebMetrics(datepoints_start_list, datepoints_end_list):
	df = pd.read_pickle('/home/dp/Documents/Campaign/pickle/TwitterMetrics_df_all_candidates.pkl')
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

	''' Time Series Line Plots '''
	cols = [col for col in df.columns if col != 'Name' and col != 'Date']
	print('cols:\n', cols)
	for title in cols:
		fig, ax = plt.subplots(figsize=(8,6))
		for label, d in df.groupby('Name'):
			d.plot(x='Date', y=title, kind='line', ax=ax, label=label, title=title)
		plt.legend(); plt.xlabel('Date'); plt.ylabel(title)
		plt.savefig('TwitterMetrics '+title, bbox_inches='tight')

	# Boxplot of Daily Followers Gained:
	df.boxplot(column='Daily Followers Gained', by='Name')#; plt.xlabel('Date'); plt.ylabel('Daily Followers Gained')
	plt.xticks(rotation='vertical'); plt.ylabel('Daily Followers Gained')
	plt.savefig('TwitterMetrics Daily Followers Gained Boxplot', bbox_inches='tight')
	plt.show()

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
			last_name_list.append('Buttigieg')
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
# DonorCounter()
''' -------------------------- '''


''' --- Scheduling the DonorCounter() data collection: --- '''
''' --- Uncomment to schedule DonorCounter(), specify time --- '''
# Seconds can be replaced with minutes, hours, or days
# sched.start()
# sched.add_job(DonorCounter, 'interval', seconds=3)
# while True:
#     time.sleep(1)
# sched.shutdown()

''' --- Federal Election Commission --- '''
FEC()
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
# df_dem_odds, df_rep_odds, df_pres_odds, df_dem_field, df_rep_field, df_pres_field = CampaignBetting()
# PlotCampaignBetting()
# --- Sorting Campaign ---
# SortCampaignBettingCSV()
''' --------------------------- '''


''' ----------------------------------------- WebMetrics() ----------------------------------------- '''

''' --- Run WebMetrics() --- '''
# df_all = WebMetrics() # WARNING: RUNNING THIS WILL NOT UPDATE CURRENT CSV DATA BUT WILL OVERWRITE IT WITH
						# THE LATEST 30 DAYS OF TWITTER DATA. CURRENT CSV FILES ARE BACKED UP IN THE
						# FOLDER 'Campaign/TwitterMetrics csv backup'. WebMetrics() NEEDS THE CAPABILITY
						# TO LOAD CSV DATA, ADD THE MOST RECENT SCRAPED DATA TO IT AND WRITE BACK TO CSV.
# PlotWebMetrics(['2019,3,15','2019,3,22','2019,3,29','2019,4,5'],['2019,3,22','2019,3,29','2019,4,5','2019,4,14'])
''' ----------------------------- '''


