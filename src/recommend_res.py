from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict, OrderedDict
import sys
sys.path.append('lib')

class recommendSystem:
	def __init__(self, db):
		self.db = db
		self.RecommendResources = []

	def __log_split_by_time(self, res_collectname, log_collectname='Search_log'):
		"""
			This function split user log by time.
			See all users using situation each two weeks and
			print the results.
			
			Args:
				res_collectname (str): records of recommend resources' collection name.
				log_collectname (str): search_log collection name.

			Returns:
				No return value.

			The result example is at ../result/recommend_0810.
		
		"""
		
		collect_log = self.db[log_collectname]

		rec_res_list = list(self.db[res_collectname].find())
		res_sets = set()

		for r in rec_res_list:
			if r['resource_id'] not in res_sets:
				r['resource_id'] = int(r['resource_id'])
				res_sets.add(r['resource_id'])
		
		from get_info import get_obj_to_res
		obj_to_res = get_obj_to_res(self.db)
		
		DateCount = {}
		res_to_date = {}

		query = {"class_code": {"$in":["R", "M_R", "L", "M_L", "F", "M_F"] } }	
		log_datas = collect_log.find(query).sort([("main_col",1), ("since",1)])

		for data in log_datas:
			try:
				main_col = int(data['main_col'])
			except (UnicodeEncodeError, ValueError):
				continue

			# translate main_col value to resource_id
			if 'R' in data['class_code']:
				res_id = main_col
			else:
				if main_col not in obj_to_res:
					continue
				res_id = obj_to_res[main_col]
		

			if res_id in res_sets:
				if data["since"].day <= 15:	# split time by two weeks
					date_block = datetime(data["since"].year, data["since"].month, 1)
				elif data["since"].day <= 31:	
					date_block = datetime(data["since"].year, data["since"].month, 16)
				DateCount.setdefault(date_block, 0)
				DateCount[date_block] += 1		
				
				if res_id not in res_to_date:
					res_to_date[res_id] = defaultdict(list)
				for res_each in rec_res_list:
					if res_each['resource_id'] == res_id:
						res_to_date[res_id][date_block].append(data)
						break
		
		self.__print_data(res_collectname, rec_res_list, DateCount, res_to_date)

	def __print_data(self, res_collectname, rec_res_list, dateCount, res_to_date):
		"""
			This function prints the result each two weeks and calculate the changing percent \
			in first and second two weeks.
			This function also prints the result.

			Args:
				res_collectname (str): collection name which stores recommended data information.
				rec_res_list (list): recommended resources list from source collections(res_collectname).
				dateCount (dict): count users using time each two weeks from all recommended collections.
				res_to_date (defaultdict(dict)): the resource which in rec_res_list and \
												 split users used time each two weeks.
		
			Returns:
				No return value.

		"""
		print res_collectname
		for res_each in rec_res_list:
			res_id = res_each['resource_id']
			startDate = datetime.strptime(res_each['startDate'].encode('utf-8'), '%Y.%m.%d')
			endDate = datetime.strptime(res_each['endDate'].encode('utf-8'), '%Y.%m.%d')
			#print "Res_id: {}, start: {}, End: {}".format(res_id, startDate, endDate)
			if res_id not in res_to_date:
				#print "Dont have Data!"
				#print "==============="
				continue
			
			recommend_resource = {}
			recommend_resource['source'] = res_collectname
			recommend_resource['res_id'] = res_id
			recommend_resource['startDate'] = startDate
			recommend_resource['endDate'] = endDate
			recommend_resource['domain'] = res_each['domain']
			
			prev_num = None
			prev_total_num = None
			prev_week = None
			res_to_date[res_id] = OrderedDict(sorted(res_to_date[res_id].items()))
			for week,value in res_to_date[res_id].iteritems():
				if prev_week is None or (week-prev_week).days > 16:
					prev_num = len(value)
					prev_total_num = dateCount[week]
					prev_week = week


				data_num = len(value)
				percent = round(float(data_num-prev_num)/prev_num*100, 2)
				total_num = dateCount[week]
				total_per = round(float(total_num-prev_total_num)/prev_total_num*100, 2)
				#print "Week: {}, numbers / total: {} / {}, num / total percent: {}% / {}%" \ 
				#												.format(week, data_num, total_num, \
				#												"+"+str(percent) if percent > 0 else str(percent), \
				#												"+"+str(total_per) if total_per > 0 else str(total_per))
				
				if (week-startDate).days <= 15:
					recommend_resource['FirstWeek_Change'] = round(percent/100, 4)
					recommend_resource['FirstWeek_TotalChange'] = round(total_per/100, 4)
				elif (week-startDate).days <= 31:
					recommend_resource['SecWeek_Change'] = round(percent/100, 4)
					recommend_resource['SecWeek_TotalChange'] = round(total_per/100, 4)

				

				prev_num = data_num
				prev_total_num = total_num
				prev_week = week
			#print recommend_resource
			self.RecommendResources.append(recommend_resource)
			#print "==============="
			#break


		'''
		# print the users number each two weeks
		prev_date_num = None
		for date, num in OrderedDict(sorted(dateCount.items())).items():
			if prev_date_num is None: prev_date_num = num
			per = round(float(num-prev_date_num)/prev_date_num*100, 2)
			print "Date: {} , Num: {} , Percent: {}%".format(date, num, "+"+str(per) if per > 0 else str(per))
			prev_date_num = num
		'''

		
	def find_good_res(self, recommend_res, hot_res_list):

		"""
			This function uses recommend resources from records of recommend resources and \
			hot resources list from analysizing users' log to do cross-analysis.
			This will find out which resource is users' favourites and also a good resources \
			which recommended by our team.
			This function also prints the results.

			Args:
				recommend_res (list): top resources in records of recommend resources.
				hot_res_list (list): the hot resource list according to users' log.

			Returns:
				No return value.

			The results example is at ../result/find_good_res_100 which sets click_num = 100.
		"""

		print "==========\nfunction find_good_res:"
		count = {}
		for rec_res in recommend_res:
			for hot_res in hot_res_list:
				if str(rec_res['res_id']) == hot_res['resource_id']:
					import pprint
					pp = pprint.PrettyPrinter(indent = 4, depth = 1)
					pp.pprint(hot_res)

					user_num = sum(hot_res['user_edutype'].values()) - hot_res['user_edutype']['-1']
					if user_num != 0:
						user_back_time = round(float(hot_res['total_num'] - hot_res['user_edutype']['-1']) / user_num, 2)
						print "each user use time: {}".format(user_back_time)
					print '\n'

					count.setdefault(hot_res['res_edugrade'], 0)
					count[hot_res['res_edugrade']] += 1
					count.setdefault(hot_res['res_discipline_id'], 0)
					count[hot_res['res_discipline_id']] += 1
					break

		from operator import itemgetter
		for i,v in sorted(count.items(), key=itemgetter(1), reverse=True):
			print i,v



	def check_rec_res_location(self, rec_res, hot_res_list):
		"""
			This function checks the influence to the resources which is recommended in different locations.

			Args:
				rec_res (list): recommended resources list.
				hot_res_list (list): popular resources list.

			Returns:
				No return value.

		"""
		print "function Check recommend resource location:"
		list1 = ['Home_WebEduResources', 'Home_EduAPP', 'Home_EduEbook']
		collect = list1[0]
		print "=======\n{}".format(collect)
		local_use_num = {}
		local_idx = 0
		index = 0
		for res in rec_res[index:]:
			if res['source'] == coll:
				for hot_res in hot_res_list:
					if str(res['res_id']) == hot_res['resource_id']:
						print hot_res['resource_id']
						local_use_num.setdefault(local_idx, 0)
						local_use_num[local_idx] += hot_res['total_num']
						break
				local_idx += 1
				# 9 is especially for Home_WebEduResources
				if local_idx % 9 == 0:
					break

		for local in sorted(local_use_num.items()):
			print local


	def get_recommend_res(self):
		"""
			This function returns the recommended resources list which can be created \
			by private function or read by pickle file.
		
			Args:
				Don't need argument.

			Returns:
				Returns recommended resources list.
			
		"""
		import cPickle as pickle
		try:
			with open('tmp/rec_res.pic', 'rb') as fp:
				self.RecommendResources = pickle.load(fp)
		except IOError:	
			resource_sets = {'Home_EduAPP', 'Home_EduEbook', 'Home_WebEduResources', 'Junior_resources', \
							 'Vocation_resources', 'Primary_resources', 'Senior_resources'}
			for res_collectname in self.db.collection_names():
				if res_collectname in resource_sets:
					self.__log_split_by_time(res_collectname)
					print '---------------------'
					#break

			with open('tmp/rec_res.pic', 'wb') as fp:
				pickle.dump(self.RecommendResources, fp)

		return self.RecommendResources

	def __call__(self):

		import user_SocialNetwork
		hot_res_list = user_SocialNetwork.user_SocialNetwork(db).get_hot_res_list(res_clicked_num = 100)
		recommend_res = self.get_recommend_res()

		if hot_res_list != None and len(recommend_res) != 0:
			self.find_good_res(recommend_res, hot_res_list)
			#self.check_rec_res_location(recommend_res, hot_res_list)




client = MongoClient('localhost')
db = client['edumarket_tmp']

if __name__ == "__main__":
	start = datetime.now()
	
	recommend_sys = recommendSystem(db)
	recommend_sys()

	print "{} End !".format(__name__)
	print datetime.now()-start





