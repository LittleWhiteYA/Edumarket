from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict, OrderedDict, Counter
from itertools import groupby
from operator import itemgetter
import sys
sys.path.append('lib')
from get_info import getMemberInfo, getResourceInfo, get_res_to_discipline, get_all_res


class user_SocialNetwork:
	def __init__(self, db, join_collname="JOIN_ResToUser"):
		self.db = db
		self.join_collname = join_collname
		self.coll_join = db[join_collname]

	
	def find_member_network(self):
		"""
			This function finds the relation between uploader and member, 
			finds all member who used uploader's resources and prints the results.

			Args:
				Don't have arguments.
			
			Returns:
				No return value.
		
			the result example is at ../result/upID_FLR.

		"""
		
		# change all user_id with download, link, click behavior from str to int
		# and merge together
		res_to_user = defaultdict(list)
		for res in self.coll_join.find():
			up_id = int(res['value']['upload'])
			res_to_user[up_id] += map(int, res['value']['download'])	
			res_to_user[up_id] += map(int, res['value']['link'])
			res_to_user[up_id] += map(int, res['value']['click_res'])
		res_to_user = dict(res_to_user)

		# Counter user_id's usage count
		for up_id in res_to_user:
			id_list = res_to_user[up_id]
			res_to_user[up_id] = {}
			res_to_user[up_id] = Counter(id_list)
			res_to_user[up_id] = OrderedDict(sorted(res_to_user[up_id].items()))
		
		
		print "count uploader number: {}".format(len(res_to_user))
		print "=========="
		res_list = []

		#generator, send user_id list and return user's information list
		mem_gener = getMemberInfo(self.db)
		mem_gener.next()
		for uploader, user_and_time in res_to_user.items():
			print uploader, user_and_time

			edutype_list = []
			memberInfo_list = mem_gener.send(user_and_time.keys())

			for member in memberInfo_list:
				print member
				if member == -1:
					edutype_list.extend("-1" for i in range(user_and_time[member]))
				elif member == "H" or member["edutype"] == "":
					edutype_list.append("H")
				else:
					edutype_list.append(member["edutype"])
			

			member_to_edutype = {}
			member_to_edutype['uploader'] = uploader
			member_to_edutype['edutype'] = Counter(edutype_list)
			res_list.append(member_to_edutype)
			print member_to_edutype
			print '-----'
			#break

		for res in res_list:
			print res
		mem_gener.close()

		return res_list
	


	def find_hot_resources(self, res_clicked_num):

		"""
			This function finds out the resources which most of users like and
			prints the results.
			
			Args:
				res_clicked_num (int): the number which differentiates resource is popular or not.

			Returns:
				hot_res_list (list): the hot resources list
			
			The hot_res_list results example is at ../result/hot_res_list_100 which sets res_clicked_num = 100.

		"""	
		print "==========\nfunction find_hot_resources:"
		
		res_to_user = {}
		hot_res_list = []
		
		#generator, send users' id list and return users' information list
		mem_gener = getMemberInfo(self.db)
		mem_gener.next()
		
		#get resource id maps to its discipline id
		res_to_dis = get_res_to_discipline(self.db)

		for res in self.coll_join.find(no_cursor_timeout=True):	#avoid running time more than 10 mins and collection closed
			id_list = []
			id_list += res['value']['download']
			id_list += res['value']['link']
			id_list += res['value']['click_res']
			id_list = map(int, id_list)

			if len(id_list) < res_clicked_num:
				continue	

			res_id = res["_id"]
			res_to_user[res_id] = Counter(id_list)
			res_to_user[res_id] = OrderedDict(sorted(res_to_user[res_id].items()))
			
			edutype_list = []
			memberInfo_list = mem_gener.send(res_to_user[res_id])

			# count members' educational type
			for member in memberInfo_list:
				#print member
				if member == -1:
					edutype_list.extend("-1" for i in range(res_to_user[res_id][member]))
				elif member == "H" or member["edutype"] == "":
					edutype_list.append("H")
				else:
					edutype_list.append(member["edutype"])

			res_and_user = {}
			res_and_user['resource_id'] = res_id
			res_and_user['res_edugrade'] = res['value']['edugrade']
			res_and_user['res_discipline_id'] = res_to_dis[int(res_id)] if int(res_id) in res_to_dis else -1
			res_and_user['user_info'] = memberInfo_list
			res_and_user['user_edutype'] = Counter(edutype_list)
			res_and_user['total_num'] = len(id_list)
			hot_res_list.append(res_and_user)
			#break

		mem_gener.close()

		return hot_res_list


	def find_userlinks(self, hot_res_list, link_number):

		"""
			This function finds the link between two users.
			Two users will have a link If they use the same resource.
			This function also prints the results.

			Args:
				hot_res_list (list): this list contains all hot resources' informations.
				link_number (int): this link number decides how many time \
									does resources was clicked by both users could define as a link.

			Returns:
				No return value.
			
			The results example is at ../result/link_100 which sets hot_res_list's res_clicked_num = 100.
		"""

		print "==================\nfunction find_userlinks:"
		user_links = []
		for res in hot_res_list:
			res_id = res['resource_id']
			memberInfo_list = res['user_info']
			
			for idx, member in enumerate(memberInfo_list):
				if member == -1:
					continue
				for idx2, member2 in enumerate(memberInfo_list[idx+1:], start=idx+1):
					if member2 == 'H':
						continue

					user_link = {}
					user_link['user1_id'] = member['id']
					user_link['user2_id'] = member2['id']
					user_link['user1_edutype'] = member['edutype']
					user_link['user2_edutype'] = member2['edutype']
					user_link['user1_roletype'] = member['roletype']
					user_link['user2_roletype'] = member2['roletype']
					user_link['res_id'] = int(res_id)
					
					user_links.append(user_link)
			

		print "user_links number: {}".format(len(user_links))
		
		sort_func = lambda link: (link['user1_id'], link['user2_id'], link['res_id'])
		user_links.sort(key = sort_func)
		total_size = 0	
		num = 0
		
		#generator, send resources' id list and return resources' information list
		res_gener = getResourceInfo(self.db)
		res_gener.next()

		user_links2 = []
		for key, value_gener in groupby(user_links, key = lambda link: (link['user1_id'], link['user2_id'])):
			
			value_list = list(value_gener)
			size = len(value_list)	#the link number between two users
			if size >= link_num:
				hot_res_list = [value['res_id'] for value in value_list]
				
				ResInfo_list = res_gener.send(hot_res_list)
				res_edugrade_list = [res['edugrade'] for res in ResInfo_list]

				user_link = value_list[0]
				del user_link['res_id']
				user_link['link_num'] = size
				user_link['res_edutype_list'] = Counter(res_edugrade_list)
				user_links2.append(user_link)
		

		user_links2.sort(key = lambda link: link['link_num'])
		for link in user_links2:
			print "---------------"
			print link
			try:
				print link['link_num'], link['user1_edutype'], link['user2_edutype']
			except Exception:
				pass


	def count_userEdu_to_resEdu(self, hot_res_list):
		"""
			This function counts different edutype's user using different edugrade's resources.
			This function also prints the results.
			
			Args:
				hot_res_list (list): this list contains all hot resources' informations.

			Returns:
				No return value.
			
			The results example is at ../result/userEdu_to_resEdu_100 which sets hot_res_list's res_clicked_num = 100.
		"""

		print "==================\nfunction count_userEdu_to_resEdu:"
		userEdu_to_resEdu = defaultdict(dict)
		for res in hot_res_list:
			for user_edu, count in res['user_edutype'].iteritems():
				userEdu_to_resEdu[user_edu].setdefault(res['res_edugrade'] ,{})
				userEdu_to_resEdu[user_edu][res['res_edugrade'] ].setdefault('total_use_num', 0)
				userEdu_to_resEdu[user_edu][res['res_edugrade'] ]['total_use_num'] += count
				userEdu_to_resEdu[user_edu][res['res_edugrade'] ].setdefault(res['res_discipline_id'], 0)
				userEdu_to_resEdu[user_edu][res['res_edugrade'] ][res['res_discipline_id'] ] += 1

		for user_edu, res_edu_dict in sorted(userEdu_to_resEdu.iteritems()):
			print "user_edu: {}".format(user_edu)
			for res_edu, res in sorted(res_edu_dict.iteritems()):
				print "\tres_edu: {}, {}".format(res_edu, sorted(res.items(), key = itemgetter(1) , reverse=True) )
			print '------'

				
	def get_hot_res_list(self, res_clicked_num):
		"""
			This function gets hot resources list by running function "find_hot_resources" or \
			reading pickle file.
		
			Args:
				res_clicked_num (int): the number which differentiates resource is popular or not.

			Returns:
				hot_res_list (list): the hot resources list.

		"""
		#self.coll_join.drop();

		hot_res_list = None
		from join_MR import join_res_and_user_MR
		if self.join_collname in self.db.collection_names() or join_res_and_user_MR(self.db, self.join_collname):

			import cPickle as pickle
			print "Click_num: {}".format(res_clicked_num)
			try:
				with open('tmp/hot_res_list_'+str(res_clicked_num)+'.pic', 'rb') as fp:
					hot_res_list = pickle.load(fp)
			except IOError:
				hot_res_list = self.find_hot_resources(res_clicked_num)
				with open('tmp/hot_res_list_'+str(res_clicked_num)+'.pic', 'wb') as fp:
					pickle.dump(hot_res_list, fp)
		
		return hot_res_list

	# I use this function to run each results.
	def __call__(self, res_clicked_num):
		self.find_member_network()
		hot_res_list = self.get_hot_res_list(res_clicked_num)
		if hot_res_list != None:	
			self.find_userlinks(hot_res_list)
			self.count_userEdu_to_resEdu(hot_res_list)
			pass

		'''
		# get all resources from collection "Resources_type"
		all_res = get_all_res(db)
		for edu, dis in sorted(all_res.iteritems()):
			print "res_edu: {}".format(edu)
			print sorted(dis.items(), key = itemgetter(1), reverse=True)
		'''

	

client = MongoClient('localhost')
db = client['edumarket_tmp']

if __name__ == "__main__":
	start = datetime.now()
		
	user_network = user_SocialNetwork(db)
	user_network(res_clicked_num = 500)

	print datetime.now() - start

client.close()




