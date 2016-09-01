# coding=utf-8
from datetime import datetime

import csv
def readCSV(filename):
	with open(filename) as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		return list(reader)


def isDate(date_txt):
	try:
		datetime.strptime(date_txt, '%Y.%m.%d')
		return True
	except ValueError:
		pass
	except:
		import sys
		print "Error: ", sys.exc_info()[0]
	return False


def getResources(filename, rows):
	attrs = rows[1]

	startDate_index = -1
	endDate_index = -1
	res_id_index = -1
	domain_index = -1

	for num in range(len(attrs)):
		if attrs[num] == '發佈期間(起)':
			startDate_index = num
		elif attrs[num] == '發佈期間(迄)':
			endDate_index = num
		elif attrs[num] == '資源編號':
			res_id_index = num
		elif attrs[num] == '適用學科':
			domain_index = num

	if startDate_index == -1 or endDate_index == -1 or res_id_index == -1 or domain_index == -1:
		return False
	
	resources = []
	for row in rows:
		if isDate(row[startDate_index]) and isDate(row[endDate_index]) and row[res_id_index]:
			resources.append( { "startDate": row[startDate_index], \
								"endDate": row[endDate_index], \
								"resource_id": row[res_id_index], \
								"domain": row[domain_index] })
	return resources

def getResources2(filename, rows):
	attrs = rows[1]

	web_index = -1
	link_index = -1

	for index, attr in enumerate(attrs):
		if attr.find("資源所屬網站") != -1:
			web_index = index
		elif attr.find("連結網址") != -1:
			link_index = index

	if web_index == -1 or link_index == -1:
		return False

	left = filename.rfind('_')
	right = filename.rfind('.')
	date_txt = filename[left+1:right]
	date = datetime.strptime(date_txt, "%Y%m%d")

	resources = []
	for row in rows:
		if row[web_index] == "教育大市集":
			res_id = split_ResourceID(row[link_index])
			if res_id != -1:
				resources.append( { "startDate": date, \
									"endDate": datetime.now(), \
									"resource_id": res_id })

	return resources

def split_ResourceID(url_link):
	url_link = url_link.strip()
	right = url_link.rfind('/')
	res_id = url_link[right+1:]
	if res_id != "" and res_id.isdigit():
		return res_id
	else:
		return -1
	

from pymongo import MongoClient
def insertCollection(collect_name, res_list):
	
	col_name = collect_name
	client = MongoClient('localhost')
	db = client['edumarket_tmp']

	if col_name not in db.collection_names():
		for res in res_list:
			#print res
			db[col_name].insert(res)

		print "{} Finish!".format(col_name)
	else:
		print "{} collection Exists!".format(col_name)



import os
if __name__ == "__main__":
	for dirPath, subdirs, fileNames in os.walk("../Resources/RecommendData/"):
		for fn in fileNames:
			if fn.endswith('.csv'):
				print "{} Start!".format(fn)
				rows = readCSV(filename)
				res = getResources(os.path.join(dirPath, fn), rows)
				if res == False:
					res = getResources2(os.path.join(dirPath, fn), rows)
				col_name = fn[:-4]
				insertCollection(col_name, res)






