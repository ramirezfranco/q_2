import pandas as pd 
import math
import os

all_states = [state[:2] for state in os.listdir('data')]

def new_names(df, year):
	'''
	Identifies the new or reintroduced names for a given year
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore.
	Returns a set with names.
	'''
	previous = df[(df['year']>=year-11)&(df['year']<=year-1)]
	previous_names = list(set(previous['name']))
	current_names = list(set(df[df['year']==year]['name']))

	new_names = [name for name in current_names if name not in previous_names]
	return set(new_names)

def states_with_name(df, year, name):
	'''
	Identifies those states where a name were used in a given year.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore.
		- name (str): name to search.
	Returns a set with names of states
	'''
	return set(df[(df['year']==year)&(df['name']==name)]['state'])


def popular_names(df, year):
	'''
	Identifies those names in the top decil of counts nationwide in a 
	given year.
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore.
	Returns a set with names
	'''
	current = df[df['year']==year]
	current = current [['name', 'count']].groupby(['name']).sum()
	total = current['count'].sum()
	current['percentage'] = (current['count']/total)*100
	top = math.ceil(len(current)*.1)
	current = current.sort_values(by='percentage', ascending=False)[:top]
	return set(current.index)


def becomed_popular(df, year):
	'''
	Identifies those new names in a given year that reached the top decil 
	of counts nationwide in at least one year in the following 10 years 
	period.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore.
	Returns a set with names.
	'''
	becomed = {}
	new = new_names(df, year)
	for y in range(year, year+10):
		inter = list(new.intersection(popular_names(df, y)))
		for name in inter:
			if name not in becomed.keys():
				becomed[name]=[y]
			else:
				becomed[name].append(y)
	return becomed


def trend_setter(df, year):
	'''
	Identifies those states that adopted popular names
	during the first year it appears in the database in a 
	given year.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore.
	Returns a list of states
	'''
	names = becomed_popular(df, year)
	states = []
	for name in names:
		states+=list(states_with_name(df, year, name))
	return states


def trend_setter_period(df, start, end):
	'''
	Identifies those states that adopted popular names
	during the first year it appears in the database whithin a
	period of years.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- start (int): year when the period to explore begins (inclusive).
		- end (int): year when the period to explore finishes (inclucive).
	Returns a dictionary where every key is a state and every value is the
	count of times the state was a trend setter for any popular name.
	'''
	states = {}
	for year in range(start, end+1):
		states_year = trend_setter(df, year)
		if len(states_year)>0:
			for s in states_year:
				if s not in states.keys():
					states[s]=1
				else:
					states[s]+=1
	return states 


def late_adopters(df, year):
	'''
	Identifies those states that adopted popular names
	up to 3 years after the year it became popular nationwide. The
	'year' parameter refers to the year where the popular names appears.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- year (int): year to explore (when the new names are generated).
	Returns a list of states
	'''
	names = becomed_popular(df, year)
	names = {name:min(years)+1 for name, years in names.items()}
	states = []
	for name, y in names.items():
		early, late = [], []
		for p in range(year, y):
			early+= list(states_with_name(df, p, name))
		for q in range(y, y+3):
			late+=list(states_with_name(df, q, name))
		late = [state for state in late if state not in early]
		states+=late
	return states


def late_adopters_period(df, start, end):
	'''
	Identifies those states that adopted popular names
	up to 3 years after the year it became popular nationwide
	whithin a period of years.
	Inputs:
		- df (pandas DataFrame): Combined data frame with information of
		  names, count, gender, year and state from from Social Security 
		  Card Applications.
		- start (int): year when the period to explore begins (inclusive).
		- end (int): year when the period to explore finishes (inclucive).
	Returns a dictionary where every key is a state and every value is the
	count of times the state was a late adopter for any popular name.
	'''
	states = {}
	for year in range(start, end+1):
		late = late_adopters(df, year)
		if len(late) > 0:
			for s in late:
				if s not in states.keys():
					states[s]=1
				else:
					states[s]+=1
	return states


