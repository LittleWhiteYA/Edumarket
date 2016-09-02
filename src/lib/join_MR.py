from bson.code import Code

def join_res_and_user_MR(db, join_collectname):	
	"""
		This function uses mongoDB's MapReduce to join resource informations and user informations.
		The join collection uses resource id as key, \
		user id who uses or uploads it and resource informations as a dict of value.

		Args:
			db (database)
			join_collectname (str): expected joined collection name

		Returns:
			True: if join succeed.
	"""
	up_collectname = 'resources_objfile'
	log_collectname = 'search_log'	
	resInfo_collectname = 'resources_type'
	collect_up = db[up_collectname]
	collect_log = db[log_collectname]
	collect_resinfo = db[resInfo_collectname]

	up_dict = {}
	fields = {"objectfile_id":1, "resources_id":1}
	query = {"resources_id":{"$ne":-1}}
	for up in collect_up.find(query, fields):
		up_dict[str(up["objectfile_id"])] = str(up["resources_id"])

	cookie_to_user = _mapper_cookie_to_user_id(db)
	
	# uploader mapper
	up_mapper = Code(""" function(){
		emit(this.resources_id.toString(), {'upload': this.member_id});
	} """)

	# downloader
	down_mapper = Code(""" function(){
		res_id = obj_to_res[this.main_col];
		user_id = this.user_id;
		if(user_id == -1 && this.cookie_iden in cookie_to_user)
			user_id = cookie_to_user[this.cookie_iden];
		emit(res_id, {'download': user_id});	
	} """)

	# user clicks link
	link_mapper = Code(""" function(){
		res_id = obj_to_res[this.main_col];
		user_id = this.user_id;
		if(user_id == -1 && this.cookie_iden in cookie_to_user)
			user_id = cookie_to_user[this.cookie_iden];
		emit(res_id, {'link': user_id});	
	} """)

	# user clicks resource
	click_res_mapper = Code(""" function(){
		res_id = this.main_col;
		user_id = this.user_id;
		if(user_id == -1 && this.cookie_iden in cookie_to_user)
			user_id = cookie_to_user[this.cookie_iden];
		emit(res_id, {'click_res': user_id});	
	} """)

	# resource informations
	resInfo_mapper = Code(""" function(){
		res_id = this.id.toString();
		emit(res_id, {'edugrade': this.edugrade, 'formtype': this.formtype});
	} """)


	reducer = Code(""" function(key, values){
		var ids = {
			'upload' : -1,
			'edugrade' : '',
			'formtype' : '',
			'download' : [],
			'link' : [],
			'click_res' : []
		};
		values.forEach(function(value){
			if("upload" in value)
				ids.upload = value.upload;
			if("edugrade" in value)
				ids.edugrade = value.edugrade;
			if("formtype" in value)
				ids.formtype = value.formtype;
			if("download" in value){
				if(value.download instanceof Array)
					ids.download = ids.download.concat(value.download);
				else
					ids.download.push(value.download);
			}
			if("link" in value){
				if(value.link instanceof Array)
					ids.link = ids.link.concat(value.link);
				else
					ids.link.push(value.link);
			}
			if("click_res" in value){
				if(value.click_res instanceof Array)
					ids.click_res = ids.click_res.concat(value.click_res);
				else
					ids.click_res.push(value.click_res);
			}
		});	
		return ids;
	} """)

	up_query = {"resources_id": {"$ne":-1}}	
	down_query = {"class_code": { "$in": ["F", "M_F"] } }
	link_query = {"class_code": { "$in": ["L", "M_L"] } }
	click_res_query = {"class_code": { "$in": ["R", "M_R"] } }

	# get all resources profile like edugrade, formtype and join to the collection
	collect_resinfo.map_reduce(resInfo_mapper, reducer, out={ "reduce": join_collectname}, query={})
	# get each resource's uploader id and join
	collect_up.map_reduce(up_mapper, reducer, out={ "reduce": join_collectname}, query=up_query)
	
	# get all log users (dowload, click resource, click link) id and join
	# down_mapper and link_mapper has to change "main_col" which is objectfile id to resource id
	collect_log.map_reduce(down_mapper, reducer, out={ "reduce": join_collectname}, \
						scope={"obj_to_res": up_dict, "cookie_to_user": cookie_to_user}, query=down_query)
	collect_log.map_reduce(link_mapper, reducer, out={ "reduce": join_collectname}, \
						scope={"obj_to_res": up_dict, "cookie_to_user": cookie_to_user}, query=link_query)
	collect_log.map_reduce(click_res_mapper, reducer, out={ "reduce": join_collectname}, \
						scope={"cookie_to_user": cookie_to_user}, query=click_res_query)

	# remove some useless data 
	collect_join = db[join_collectname]
	remove_query = { "$or": [{"value.upload": {"$exists": False}}, {"value.upload": -1} ] }	
	collect_join.remove(remove_query)

	remove_query = { "$and": [ \
						{"$or":[ {"value.download": {"$exists": False} }, {"value.download":{"$size":0} } ] } \
						,{"$or":[ {"value.link": {"$exists": False} }, {"value.link":{"$size":0} } ] } \
						,{"$or":[ {"value.click_res": {"$exists": False} }, {"value.click_res": {"$size": 0} } ] }
					] }	
	collect_join.remove(remove_query)
	

	for each in collect_join.find():
		print each

	return True


def join_user_and_res_MR(db, join_collectname):
	"""
		This function uses MongoDB's MapReduce to join user informations and resource informations.
		The join collection uses user id as key, resources used by the user and when to use as a list of value.

		Args:
			db (database)
			join_collectname (str): expected joined collection name

		Returns:
			True: if join succeed.
	"""

	log_collectname = 'search_log'
	res_obj_collectname = 'resources_objfile'
	collect_log = db[log_collectname]
	collect_obj = db[res_obj_collectname]
	
	obj_to_res = {}
	fields = {"objectfile_id": 1, "resources_id": 1}
	query = {"resources_id": {"$ne": -1} }

	# just like get_obj_to_res function in get_info.py
	for obj in collect_obj.find(query, fields):
		obj_to_res[str(obj['objectfile_id']) ] = obj['resources_id']

	cookie_to_user = _mapper_cookie_to_user_id(db)
	

	user_mapper = Code(""" function(){
		user_id = this.user_id;
		if(user_id == -1 && this.cookie_iden in cookie_to_user)
			user_id = cookie_to_user[this.cookie_iden];

		if(user_id != -1){
			res_id = -1;
			if(this.class_code.indexOf('F') !== -1 || this.class_code.indexOf('L') !== -1){
				if(this.main_col in obj_to_res)
					res_id = obj_to_res[this.main_col];
			}
			else
				res_id = parseFloat(this.main_col);
			if(res_id != -1)
				emit(user_id, {'res_id': res_id, 'since': this.since});
		}
	} """ )

	user_reducer = Code(""" function(key, values){
		var res = {
			'res_and_since': []
		};
		values.forEach(function(value){
			if(value.res_and_since instanceof Array)
				res.res_and_since = res.res_and_since.concat(value.res_and_since);
			else
				res.res_and_since.push(value);
		});
		
		return res;
	} """ )

	#MongoDB query
	query = {"class_code": {"$in":["R", "M_R", "L", "M_L", "F", "M_F"] } }
	collect_log.map_reduce(user_mapper, user_reducer, out={ "reduce": join_collectname}, \
						scope={"cookie_to_user": cookie_to_user, "obj_to_res": obj_to_res}, query=query)
	
	return True



def _mapper_cookie_to_user_id(db, log_collectname='search_log'):
	"""
		This function checks a guest may be a user by the same cookie.

		Args:
			log_collectname (str): collection which contains user log.

		Returns:
			cookie_to_user (dict): cookie as key and user id as value.
	"""

	collect_log = db[log_collectname]

	result = collect_log.aggregate([
				{ "$match": { "cookie_iden": {"$ne": ""} } },
				{ "$group": { "_id": { "user_id": "$user_id", "cookie_iden": "$cookie_iden"},
				  "count": { "$sum": 1}
				} }
			])
	
	# let the same cookle together to find guest may be a user
	user_list = sorted(list(result), key = lambda cookie: (cookie["_id"]["cookie_iden"], cookie["_id"]["user_id"]) )
	cookie_to_user = {}
	for idx, user in enumerate(user_list):
		user_id = user['_id']['user_id']
		cookie = user['_id']['cookie_iden'] 
		if user_id != -1 and user_list[idx-1]['_id']['user_id'] == -1 and cookie == user_list[idx-1]['_id']['cookie_iden']:
			cookie_to_user[cookie] = user_id
	
	return cookie_to_user		


