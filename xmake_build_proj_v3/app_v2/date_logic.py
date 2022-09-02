import deeppavlov
from datetime import datetime # https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
from dateutil.parser import parse
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import *
import re

dateformat='%Y-%m-%dT%H:%M:%S'

def from_to_date(dstring):
	""" converts date in from_date and to_date format, returns smaller one as from_date and larger one as to_date """
	if len(dstring)==1:
		# date is in yesterday, today, last month etc format
		set1=set(['yesterday', 'today', 'tomorrow', 'current'])
		set2=set(['last','previous','before'])
		set3=set(['next','upcoming','after'])
		query_string_set=set(dstring[0].split(' '))

		if set1.intersection(query_string_set):
			if 'yesterday' in query_string_set:
				from_date = date.today() - timedelta(days=1)
			if 'today' in query_string_set or 'current' in query_string_set:
				from_date = date.today()
			if 'tomorrow' in query_string_set:
				from_date = date.today() + timedelta(days=1)
			to_date = from_date # this case both are same
		elif set2.intersection(query_string_set):
			duration = 1
			for ele in query_string_set:
				if re.search('[0-9]',ele):
					duration = int(ele)

			to_date = date.today()
			if 'month' in query_string_set or 'months' in query_string_set:
				from_date = date.today() - relativedelta(months=duration) 
			if 'year' in query_string_set or 'years' in query_string_set:
				from_date = date.today() - relativedelta(months=12*duration)
			if 'day' in query_string_set or 'days' in query_string_set:
				from_date = date.today() - timedelta(days=duration)
		elif set3.intersection(query_string_set):
			duration = 1
			for ele in query_string_set:
				if re.search('[0-9]',ele):
					duration = int(ele)
			from_date = date.today()
			if 'month' in query_string_set or 'months' in query_string_set:
				to_date = date.today() + relativedelta(months=duration) 
			if 'year' in query_string_set or 'years' in query_string_set:
				to_date = date.today() + relativedelta(months=12*duration)
			if 'day' in query_string_set or 'days' in query_string_set:
				to_date = date.today() + timedelta(days=duration)
		else:
			query_string_set=set(dstring[0].split(' '))
			# print (query_string_set)
			if 'and' in query_string_set:
				fullstring=dstring[0].replace('-',' ').split('and')
				str1=fullstring[0]
				str2=fullstring[1]
				from_date=parse(str1,fuzzy=True)
				to_date=parse(str2,fuzzy=True)
			elif 'to' in query_string_set:
				fullstring=dstring[0].replace('-',' ').split("to")
				str1=fullstring[0]
				str2=fullstring[1]
				from_date=parse(str1,fuzzy=True)
				to_date=parse(str2,fuzzy=True)
			else:
				from_date = parse(dstring[0], fuzzy=True)
				to_date = from_date

			if to_date < from_date : # swap 
				from_date,to_date = to_date,from_date

	else:
		# parse the two strings and lower one should be from_date and higher date should be to_date
		from_date=parse(dstring[0],fuzzy=True)
		to_date=parse(dstring[1],fuzzy=True)
		if to_date < from_date : # swap 
			from_date,to_date = to_date,from_date
	return from_date.strftime(dateformat),to_date.strftime(dateformat)


if __name__ == '__main__':
	config_model='ner_ontonotes_bert'
	download=False
	ner_model=deeppavlov.build_model(deeppavlov.configs.ner[config_model], download=download)

	query = "Display the sum of all payments between 25-11-2019 to 30-12-2020 post code 2901"
	result = ner_model([query])

	tokens, labels = result[0][0], result[1][0]
	print(tokens)
	print(labels)
	dateset=set()
	twoDate=False # will be true if ner gives two dates separately
	count=0
	for i,label in enumerate(labels):
		if label=='B-DATE' or label=='I-DATE':
			dateset.add(tokens[i])
		if label=='B-DATE':
			count += 1
	# print(dateset)
	if count > 1:
		twoDate = True
	dstring = ['between 25-11-2019', '30-12-2020']
	print('dstring',dstring)
	if len(dstring) > 2:
		print("cannot parse date")
	else:
		from_date,to_date = from_to_date(dstring)
		print(from_date,to_date)