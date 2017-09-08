#!flask/bin/python

# IMPORT MODULES
from app import app
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from bs4 import BeautifulSoup as BS
import pandas as pd
import numpy as np
from flask import Flask, render_template, redirect
from .forms import ClubIndexForm, StatisticsForm

# GLOBAL VARIABLES
hyperlinks = {}
team = {}
selected_club = ' '

base_website_url = r'http://www.espnfc.co.uk/english-premier-league/23/table'
template_url = r'http://www.espnfc.co.uk/english-premier-league/23/table?season={0}'
Location = r'C:\Users\nbagewad\Desktop\UCSC\Python for Programmers\Final_Project\app\espn.xlsx'

# get hyperlinks for teams to be displayed on top of the page
def get_team_hyperlinks():

	page = requests.get(base_website_url)
	soup = BS(page.content, 'html.parser')
	current_table = soup.find(class_='responsive-table-content')
	table = current_table.find("tr", {"class":"groups"}).find_parent('table')
	# extract table body from the points table
	table_body = table.find('tbody')
	table_body_links = table_body.find_all('a')

	for i in table_body_links:
		if (i.text.lower() == 'liverpool'):
			hyperlinks['liverpool'] = i['href']
		if (i.text.lower() == 'chelsea'):
			hyperlinks['chelsea'] = i['href']
		if (i.text.lower() == 'manchester united'):
			hyperlinks['manchester united'] = i['href']
		if (i.text.lower() == 'manchester city'):
			hyperlinks['manchester city'] = i['href']
		if (i.text.lower() == 'tottenham hotspur'):
			hyperlinks['tottenham hotspur'] = i['href']
		if (i.text.lower() == 'arsenal'):
			hyperlinks['arsenal'] = i['href']
			
get_team_hyperlinks()

# get table from the website based on the year selected by user
def retrieve_data_from_site(years, clubs):
	
	# Create a Pandas Excel writer using XlsxWriter as the engine.
	writer = pd.ExcelWriter(Location, engine = 'xlsxwriter')
	global team
	team = {}
	for year in years.split(','):
		data = []
		my_url = template_url.format(year)
		page = requests.get(my_url)
		soup = BS(page.content, 'html.parser')
		current_table = soup.find(class_='responsive-table-content')
		table = current_table.find("tr", {"class":"groups"}).find_parent('table')

		# extract table body from the points table
		table_body = table.find('tbody')
		table_body_columns = table_body.find(class_='columns')
		table_body_columns_th = table_body_columns.find_all('th')
		# columns headings only from first row are required
		for col in table_body_columns_th[0]:
			col = [elem.text.strip() for elem in table_body_columns_th]
			data.append(col)
			
		table_body_rows = table_body.find_all('tr')
		for row in table_body_rows:
			col = row.find_all('td')
			col = [elem.text.strip() for elem in col]
			data.append(col)

		# convert to pandas dataframe
		df = pd.DataFrame(data)
		# replace all empty cells with NaN values inplace
		df.replace('', np.nan, inplace=True)
		# drop all cells with NAN values inplace		
		df.dropna(axis='columns', how='all', inplace=True) 
		# drop all cells with NAN values inplace
		df.dropna(axis='index', how='all', inplace=True)
		# write to a sheet in excel file
		df.to_excel(writer, index = None, header = None, sheet_name = year, freeze_panes = (1,2)) 
	writer.save() # save excel file

	# read all sheets of the excel file
	df = pd.read_excel(Location, sheetname = None) 

	for year in years.split(','):
		team[year] = {}
		
		# mask to retrieve only the selected club's data
		mask = df[year]['TEAM'] == clubs 
		# Position of selected club
		team[year]['POSITION'] = int((df[year][mask]['POS'].get_values())[0]) 
		# Points of selected club
		team[year]['POINTS'] = int((df[year][mask]['PTS'].get_values())[0]) 
		# Goals scored by selected club
		team[year]['GOALS SCORED'] = int((df[year][mask]['F'].get_values())[0]) 
		# Goals conceeded by selected club
		team[year]['GOALS CONCEEDED'] = int((df[year][mask]['A'].get_values())[0]) 

		# sort dataframe by goals scored column, descending
		df_goals_for = df[year].sort_values(by=['F'], ascending=False) 
		df_goals_for = df_goals_for.reset_index(drop=True)
		# T-? in goals scored of selected club
		team[year]['GOALS SCORED RANK'] = 'T-'+str(int((df_goals_for[df_goals_for['TEAM'] == clubs].index.tolist())[0])+1) 
		
		# sort dataframe by goals conceeded column, ascending
		df_goals_against = df[year].sort_values(by=['A'], ascending=True) 
		df_goals_against = df_goals_against.reset_index(drop=True)
		# T-? in goals conceeded of selected club
		team[year]['GOALS CONCEEDED RANK'] = 'T-'+str(int((df_goals_against[df_goals_against['TEAM'] == clubs].index.tolist())[0])+1) 
 
def plot_statistics():
	global team
	global selected_club
	x_axis_years = []
	y_axis_position = []	
	y_axis_points = []	
	y_axis_goals_scored = []
	y_axis_goals_conceeded = []

	for key1, value1 in team.items():
		x_axis_years.append(key1)  
		for key2, value2 in value1.items():
			if key2 == 'POSITION':
				y_axis_position.append(value2)
			elif key2 == 'POINTS':
				y_axis_points.append(value2)
			elif key2 == 'GOALS SCORED':
				y_axis_goals_scored.append(value2)		
			elif key2 == 'GOALS CONCEEDED':
				y_axis_goals_conceeded.append(value2)
	'''
	print(x_axis_years)
	print(y_axis_position)
	print(y_axis_points)
	print(y_axis_goals_scored)
	print(y_axis_goals_conceeded)
	'''
	plot1 = plt.bar(np.arange(len(x_axis_years))-0.25, y_axis_goals_scored, color='g', 
					align='edge', width=0.25)
	plot2 = plt.bar(np.arange(len(x_axis_years)), y_axis_goals_conceeded, color='r', 
					align='edge', width=0.25)
	plt.ylabel('Goals')
	plt.xlabel('Seasons')
	plt.title(selected_club + ': Goals scored and conceeded each season')
	plt.xticks(range(len(x_axis_years)), x_axis_years)
	plt.yticks(range(0, 111, 10))
	plt.legend((plot1[0], plot2[0]), ('Goals scored','Goals conceeded'))
	#plt.show()
	plt.savefig('app/static/plot.png')
	plt.close()
	
	
# HOME PAGE
@app.route('/', methods = ["GET", "POST"])
@app.route('/homepage', methods = ["GET", "POST"])
def homepage():
	clubindexform = ClubIndexForm()
	if clubindexform.validate_on_submit():
		retrieve_data_from_site(clubindexform.years.data, clubindexform.clubs.data)
		global selected_club
		selected_club = clubindexform.clubs.data
		return redirect('/statistics')
	else:
		print (clubindexform.errors)
	return render_template('homepage.html', title='EPL', 
							hyperlinks=hyperlinks, form=clubindexform)
	
# STATISTICS PAGE
@app.route('/statistics', methods = ["GET", "POST"])
def statistics():
	global team
	global selected_club
	statisticsform = StatisticsForm()
	if statisticsform.validate_on_submit():
		return redirect('/graphs')
	else:
		print (statisticsform.errors)
	return render_template('statistics.html', title=selected_club, hyperlinks=hyperlinks, 
	                        club=selected_club, team=team, form=statisticsform)
	
# GRAPH PAGE
@app.route('/graphs', methods = ["GET", "POST"])
def graphs():
	plot_statistics()
	return render_template('graphs.html', title=selected_club, 
							hyperlinks=hyperlinks, club=selected_club)
	
	
	