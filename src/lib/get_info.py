from collections import defaultdict

def getMemberInfo(db, member_collectname="memberinfo"):
	"""
		This function is a generator.
		First, get a list of sorted user id and then return a list of member information according \
		the list of user id.

		Args:
			member_collectname (str): collection which contains member informations.

		Returns:
			member_list (list):	a list of member informations.
	"""

	fields = {"id":1, "roletype":1, "edutype":1}
	query = {}
	collect_member = db[member_collectname]
	members = list(collect_member.find(query, fields))

	sorted_user_list = yield
	while True:
		index = 0
		member_list = []
		for user_id in sorted_user_list:
			if user_id == -1:
				member_list.append(user_id)
				continue

			for index, member in enumerate(members[index:], start=index):
				if member["id"] == user_id:
					member_list.append(member)
					break
				elif member == members[-1]:
					member_list.append("H")

		sorted_user_list = yield member_list

def getResourceInfo(db, res_collectname="resources_type"):
	"""
		This function is a generator.
		First, get a list of sorted resource id and then return a list of resource information according \
		the list of resource id.

		Args:
			res_collectname (str): collection which contains resource informations.

		Returns:
			member_list (list):	a list of resource informations.
	"""

	collect_res = db[res_collectname]
	ress = list(collect_res.find())
	
	sorted_res_list = yield
	while True:
		index = 0
		getRes_list = []
		for res_id in sorted_res_list:
			for index, res in enumerate(ress[index:], start=index):
				if res["id"] == res_id:
					getRes_list.append(res)
					break
				elif res_id == ress[-1]:
					getRes_list.append("-1")
		
		sorted_res_list = yield getRes_list


def get_res_to_discipline(db, domain_collectname="domain"):
	"""
		This function maps resource id to discipline id.

		Args:
			domain_collectname (str): collection which contains resource's discipline id.

		Returns:
			res_to_discipline (dict): a dict which key is resource id and value is resource id's discipline id.
	"""

	collect_domain = db[domain_collectname]

	res_to_discipline = {}
	for res in collect_domain.find():
		res_to_discipline[res['resources_id'] ] = res['discipline_id']

	return res_to_discipline


def get_obj_to_res(db, upload_collectname='resources_objfile'):
	"""
		This function maps objectfile id to resource id.

		Args:
			upload_collectname (str): collection which contains objectfile id's resource id.

		Returns:
			obj_to_res (dict): a dict which key is objectfile id and value is objectfile id's resource id.
	"""

	collect_up = db[upload_collectname]

	obj_to_res = {}
	fields = {'objectfile_id': 1, 'resources_id': 1}
	query = {'resources_id': {'$ne': -1} }

	for up in collect_up.find(query, fields):
		obj_to_res[up['objectfile_id'] ] = up['resources_id']

	return obj_to_res


def get_all_res(db, res_collectname='resources_type'):
	"""
		This function gets all resource informations and split by resource's edugrade.

		Args:
			res_collectname (str): collection which contains all resources informations.

		Returns:
			all_res (default(dict)): a dict, level one splits by edugrade, level two stores the discipline id.
	"""

	collect_all_res = db[res_collectname]
	
	res_to_dis = get_res_to_discipline(db)
	all_res = defaultdict(dict)
	for res in collect_all_res.find():
		dis_id = res_to_dis[res['id'] ] if res['id'] in res_to_dis else -1
		all_res[res['edugrade'] ].setdefault(dis_id, 0)
		all_res[res['edugrade'] ][dis_id] += 1
		all_res[res['edugrade'] ].setdefault('total_num', 0)
		all_res[res['edugrade'] ]['total_num'] += 1

	return all_res







