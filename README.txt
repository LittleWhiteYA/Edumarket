環境: Ubuntu 16.04
語言: Python 2.7
資料庫: MongoDB 2.6

Resources:
裡面放的都是和 member、resource 的相關 json 檔
詳細內容在軟體設計規格書v0.5  裡面找的到
RecommendData 資料夾則都放有關於過去教育大市集網站推薦過的資源紀錄
原始檔皆為 xlsx 檔，我是自己手動轉成 csv 檔，並用程式寫入 MongoDB
原始檔: 推薦資源記錄_2016.07.25更新.xlsx、20160227 50個知識節點審查結果.xlsx、Data_20160108(現階段final).xlsx

build:
裡面主要是放 Sphinx doc 的東西，在 doc/ 輸入 make html，則會自動產生 html
html 會顯示有註解過的 function、class 的 API，如果有更動 py 檔的名字或新的 py 檔，
則需要修改 doc/source/index.rst

result:
裡面都是放由 src 裡的 py 執行出來的結果範例
uploader_and_user => user_SocialNetwork.py function find_member_network 的結果
hot_res_list_100 => user_SocialNetwork.py function find_hot_resources 在參數 res_clicked_num = 100 的結果
link_100 => user_SocialNetwork.py function find_userlinks 在參數 res_clicked_num = 100 的結果
userEdu_to_resEdu_100 => user_SocialNetwork.py function count_userEdu_to_resEdu 在參數 res_clicked_num = 100 的結果
recommend_0902 => recommend_res.py function __log_split_by_time 以"half month"為分割的時間單位的結果
find_good_res_100 => recommend_res.py function find_good_res 以 res_clicked_num = 100 得到 hot_res_list and recommend_res list 的結果
top_user_res200_days300	=> find_loyal_member.py inner function get_user_to_res 以 user_click_res_num = 200、user_click_within_days = 300 (days) 的結果

src:
python source 檔都放在這
	recommend_res.py:
		class 的 __call__ 會 call user_SocialNetwork.get_hot_res_list 拿到熱門資源的List，
		然後再 call self.get_recommend_res，讀取 tmp/rec_res.pkl 裡的 recommendResources list，
		如果沒有該檔會 call self.__log_split_by_time 並會將結果存在 self.RecommendResources list 並寫入 pickle file，
		之後確保 hot_res_list and recommendResources 都有了之後，
		就會 call self.find_good_res 以兩個 List 找出交集，得出 good_res_list。
		另外也可用以上兩個 List 找出推薦資源 location 是否會影響結果。
		* 這份 py 會使用到 MongoDB collection "search_log" and 推薦資源紀錄和 user_SocialNetwork.py
	user_SocialNetwork.py:
		class 的 __call__ 會 call self.get_hot_res_list，先檢查 collection "join_res_to_user" 是否存在，
		如果不存在的話會 call join_MR.join_res_and_user_MR 產生 join collection，之後 call self.find_hot_resources
		或是讀取 tmp/hot_res_list_<res_clicked_num>.pkl 拿到 hot_res_list 並回傳，
		之後便可以 call self.find_member_network 找到上傳者和使用者的使用關係，
		也可以 call self.find_userlinks 找到使用者彼此之間的連結關係，
		也可以 call self.count_userEdu_to_resEdu 找到不同教育類型的使用者使用不同資源的統計資訊。
		* 這份 py 會產生並使用到 MongoDB collection "join_res_to_user 和 get_info.py functions
	find_loyal_member.py
		call outer function find_loyal_members 會先檢查 collection "join_user_to_res" 是否存在，
		如果不存在的話會 call join_MR.join_user_and_res_MR 產生 join collection，之後 call inner function
		get_user_to_res，找到各個使用者使用了哪些資源和學科並統計關鍵字，並可以判斷誰為 heavy user。
		* 這份 py 會產生並使用到 MongoDB collection "join_user_to_res" 和 keywordResult.txt 和 get_info.py functions
	lib/get_info.py
		主要提供各種 API，從資料庫拿到想要的 data 並回傳。
		* 這份 py 會使用 MongoDB collection "memberInfo"、"resources_type"、"resources_objfile"、"domain"
	lib/join_MR.py
		提供兩個 MapReduce functions，分別是以 user_id or resource id 為 key
		* 這份 py 會使用 MongoDB collection "resources_objfile", "search_log", "resources_type"
	lib/insertCSV.py
		會自動讀取放在 Resources 的推薦資源紀錄的 csv 檔並寫入 db
	tmp/*
		放各函數會產生的 pickle file 和 function 的範例輸出
		
		
MongoDB 資料格式:
	collection join_res_to_user
	E.g.
	{
			"_id" : "10021",		# resource id
			"value" : {
					"upload" : 13834,	# uploader id
					"edugrade" : "B",	# resource id's edugrade, B 表示國小，有可能為其他 A(幼教), C(國中), D(高中) ...
					"formtype" : "B",	# resource id's formtype, B 表示國中小 Web 教育資源、D 表示高中職、E 表示電子書...
					"download" : [ ],	# list of download users' id
					"link" : [
							74588,
							74588,
							-1,
							74205
					],	# list of clicked link users' id, 這裡有 4 個人次點擊過，分別是 user id = 74588, -1 (guest), 74205
					"click_res" : [
							74588,
							-1
					]	# list of clicked resource users' id, 這裡有 2 個人次點擊過，分別是 user id = 74588, -1 (guest)
			}
	}
	
	collection join_user_to_res
	E.g.
	{
        "_id" : 64,		# user id
        "value" : {
                "res_and_since" : [	# list of resources is clicked
                        {
                                "res_id" : 1732093,	# resource id
                                "since" : ISODate("2015-12-16T19:48:44.621Z")	# clicked time
                        },
                        {
                                "res_id" : 1732093,
                                "since" : ISODate("2015-12-16T19:48:50.903Z")
                        },
                        {
                                "res_id" : 1731115,
                                "since" : ISODate("2015-12-16T19:49:06.995Z")
                        },
						...
                ]
        }
}
		
		
		
