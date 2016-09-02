from pymongo import MongoClient
from datetime import datetime
from collections import Counter

import sys
sys.path.append('lib')
from get_info import getResourceInfo, get_res_to_discipline

def find_loyal_members(db, user_click_res_num, user_click_within_days):

	#----------inner function----------	
	def get_user_to_res(collect_join, user_click_res_num, user_click_within_days):
		"""
			This function gets resources which user used before within the time.

			Args:
				collect_join (collection): collection stores resources informations which user used before.
				user_click_res_num (int): use to filter users used less resources.
				user_click_within_days (int): days, use to filter users used resources long time ago.

			Returns:
				No return value.

			The result example is at ../result/top_user_res200_days300 which sets user_click_res_num = 200, \
			user_click_within_days = 300 (days).
		"""
		print "user clicks resources number: {}".format(user_click_res_num)
		print "Find the log within days: {}".format(user_click_within_days)
		print "===================="
		user_to_res_list = []
		res_gener = getResourceInfo(db)
		res_gener.next()
		res_to_dis = get_res_to_discipline(db)
		
		res_to_keys = read_keywords(keyword_weight=1)

		for user in collect_join.find():

			if 'res_and_since' in user['value']:
				res_id_list = [res['res_id'] for res in user['value']['res_and_since'] \
								if (datetime.now() - res['since']).days <=  user_click_within_days]

				if len(res_id_list) < user_click_res_num:
					continue
				
				user_to_res = {}
				resinfo_list = []
				key_list = []

				resinfo_list = res_gener.send(sorted(res_id_list))
				user_to_res['user_id'] = user['_id']
				user_to_res['res_edugrade'] = Counter([resinfo['edugrade'] for resinfo in resinfo_list])
				user_to_res['res_discipline'] = Counter([res_to_dis[resinfo['id'] ] \
														if resinfo['id'] in res_to_dis else -1 \
														for resinfo in resinfo_list] )
				for res_id in res_id_list:
					if res_id in res_to_keys:
						key_list += res_to_keys[res_id].keys()
					else:
						print "res_id not in keyword file: {}".format(res_id)
					
				user_to_res['keywords'] = Counter(key_list).most_common(20)
				
				print "user_id: {}".format(user_to_res['user_id'])
				for k,v in user_to_res['keywords']:
					print k,v,
				print ""
				print user_to_res['res_edugrade']
				print user_to_res['res_discipline']
				print "==============="
				user_to_res_list.append(user_to_res)
				#break
		
		
		#for each in user_to_res_list:
		#	print each
	
		return user_to_res_list

	#----------outer function----------	
	join_collectname = "join_user_to_res"
	#db[join_collectname].drop()

	# check collection exists or not, if not than call join_user_and_res_MR to create a collection.
	from join_MR import join_user_and_res_MR
	if join_collectname in db.collection_names() or join_user_and_res_MR(db, join_collectname):
		get_user_to_res(db[join_collectname], user_click_res_num, user_click_within_days)
		pass



def read_keywords(keyword_weight, filename='keywordResult.txt'):
	"""
		This function reads keywords of resources from keyword file.
		
		Args:
			keyword_weight (int): this weight filter some keyword weight below it.
			filename (str): the keyword file name, "keywordResult.txt" is default.

		Returns:
			res_to_keys (dict): return a dictionary, key is resource id, and value is a dict \
								contains keywords and keywords' number.
	"""
	res_to_keys = {}
	with open('../Resources/'+filename, 'rb') as fp:
		for line in fp:
			res_id = int(line.strip().split(' ')[1])
			keys = next(fp).strip().split(' ')
			word_to_num = {}

			for key in keys[1:]:
				word, num = key.split(':')
				num = float(num)
				if num < keyword_weight:
					continue
				
				word_to_num[word] = num

			res_to_keys[res_id] = word_to_num
			#print res_id
			#print word_to_num
					
	return res_to_keys				



client = MongoClient('localhost')
db = client['edumarket_tmp']

if __name__ == "__main__":
	start = datetime.now()

	find_loyal_members(db, user_click_res_num=1000, user_click_within_days=365)

	print "{} End !".format(__name__)
	print datetime.now()-start

client.close()




