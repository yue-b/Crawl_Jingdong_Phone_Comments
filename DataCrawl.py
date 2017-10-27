#coding=utf-8
#!/usr/bin/env python
from urllib2 import *
from bs4 import BeautifulSoup as bs
import chardet
import re,requests,json,glob,os
global null,true,false
from selenium import webdriver
import time
import random
import ConnectMongodb

null = 'null'
true = 'true'
false = 'false'
phone_url = 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&pvid=cccef57ef22549a18662b71ef28e8096'
brandList = [] #存放手机品牌
linkList = [] #存放某品牌手机型号
CommentsList = [] #存放某品牌的某型号手机的所有评论
score_type = ['poor','general','good']
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

###获得手机的品牌,参数京东手机网址，
###返回phone_dic[]（其结构：[vivo]）
def getPhoneBrands(href):
	fopen1 = urlopen(href)
	html_data = fopen1.read()
	chardit1 = chardet.detect(html_data)
	#print chardit1['encoding']
	html_string=html_data.decode(chardit1['encoding'],'ignore')
	# print html_string

	soup = bs(html_string, 'html.parser')    
	phone= soup.find_all('ul', attrs={'class':'J_valueList v-fixed'})
	# print "phone : ",len(phone)
	phoneBrand_list = []
	phoneBrandName_list = []
	brand_dic = []
	for list1 in phone:
		# print list1
		phoneBrand_list = list1.find_all('li')
		# print "phoneBrand_list : ",len(phoneBrand_list)
		for list2 in phoneBrand_list:
			# print "list2",list2
			tmp = list2.find('a')
			phoneBrandName_list.append(tmp)
			# print "phoneBrandName_list : ",len(phoneBrandName_list)
			brand_href = "https://search.jd.com/" + tmp.get('href')
			brand_name = tmp.get('title')
			# print brand_name," : ",brand_href
			brand_dic.append(brand_name)

	# for list0 in brand_dic:
	# 	print list0
	return brand_dic

###获得某品牌的所有手机，参数（手机品牌name），
###返回link_list[]（其结构[{'id':**,'name':**},{'id':**,'name':**}]）
def get_all_brand_links(per_brand):
	# firefox_login=webdriver.Firefox()
	content = urlopen(
	    'https://search.jd.com/search?keyword=手机&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&ev=exbrand_' + per_brand + '%5E&page=1')
	soup = bs(content, "html.parser")
	# print soup.original_encoding

	pages_count = soup.find_all('div', id='J_topPage')[0].find_all('i')[0].get_text()
	pages_count = int(pages_count) * 2
	# print 'pages_count', pages_count
	link_list = []
	for i in range(1, pages_count, 2):

		url = 'https://search.jd.com/search?keyword=手机&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&ev=exbrand_' + per_brand + '%5E&page=' + str(
		    i)
		print "当前页数：",(i+1)/2
		print "url:",url
		firefox_login.get(url)
		js = "var q=document.documentElement.scrollTop=1000"  # 移动滚动条的高度
		firefox_login.execute_script(js)
		time.sleep(random.randint(2, 3))
		js = "var q=document.documentElement.scrollTop=2000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(2, 3))
		js = "var q=document.documentElement.scrollTop=3000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(2, 3))
		js = "var q=document.documentElement.scrollTop=4000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(2, 3))
		js = "var q=document.documentElement.scrollTop=5000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(4, 5))
		js = "var q=document.documentElement.scrollTop=6000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(4, 5))
		js = "var q=document.documentElement.scrollTop=7000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(4, 5))
		js = "var q=document.documentElement.scrollTop=8000"
		firefox_login.execute_script(js)
		time.sleep(random.randint(4, 5))

		data = firefox_login.page_source
		# firefox_login.quit()

		soup = bs(data, "html.parser")
		goods = soup.find_all('div', id="J_goodsList")
		# print str(goods).decode('unicode-escape')

		goods_list = goods[0].find_all('li', class_='gl-item')
		# print str(goods_list).decode("unicode-escape")
		# print i, len(goods_list)

		for item in goods_list:
			goods_dict = {'id': item['data-sku']}
			# for tag_em_item in item.find_all('em'):
			#     goods_dict['name'] = tag_em_item.get_text()
			# print 'goods_dict[name]', goods_dict['name']

			for tag_em_item in item.find_all('em'):
			    fullname = tag_em_item.get_text()
			print 'fullname', fullname
			try:
				splitname = str(fullname).split()
				print 'splitname:', splitname
				name = splitname[0] + ' ' + splitname[1] + ' ' + splitname[2] + ' ' + splitname[3]
			except:
				name = fullname
			goods_dict['name'] = name

			link_list.append(goods_dict)
	print len(link_list)
	# print str(link_list).replace('u\'', '\'').decode('unicode-escape')
	json.loads(json.dumps(link_list, encoding="UTF-8", ensure_ascii=False, sort_keys=False, indent=4))
	return link_list


###获得某型号手机的附加信息（好评度，好评数，中评数，差评数）,参数（手机的ID)
def getOtherInfo(phone_id):
	s = requests.session()
	url = 'https://club.jd.com/comment/productPageComments.action'
	data = {
			'productId':phone_id,
			'score':0,
			'sortType':5,
			'page':0,
			'pageSize':10,
			'isShadowSku':0,
			'fold':1
		}
	r = s.get(url,params=data)
	print r.text
	dic = {}
	try:
		# hotCommentTagStatistics_list = []#关注热点
		# hotCommentTagStatistics_list = r.json()['hotCommentTagStatistics']#关注点
		productCommentSummary = r.json()['productCommentSummary']
		dic['goodRateShow'] = productCommentSummary['goodRateShow']#好评度（百分制）
		dic['goodCount'] = productCommentSummary['goodCount']#好评数
		dic['generalCount'] = productCommentSummary['generalCount']#中评数
		dic['poorCount'] = productCommentSummary['poorCount']#差评数
	except:
		return null
	print dic
	return dic

###获得某型号手机的关注点
def getConcern(phone_id):
	s = requests.session()
	url = 'https://club.jd.com/comment/productPageComments.action'
	data = {
			'productId':phone_id,
			'score':0,
			'sortType':5,
			'page':0,
			'pageSize':10,
			'isShadowSku':0,
			'fold':1
		}
	r = s.get(url,params=data)
	# print r.text
	hot_list = []
	try:

		tmp = r.json()['hotCommentTagStatistics']

		for list0 in tmp:
			dic = {}

			dic['name'] = list0['name']
			dic['count'] = list0['count']
			dic['stand'] = list0['stand']

			hot_list.append(dic)
	except:
		return null
	print len(hot_list)
	return hot_list

###获得手机评论，参数（手机的ID，flag＝是否有下一页,score代表评价类型），
###返回Comments[]（其结构[{'replyCount':**,'creationTime':**,'content':**,'score':**,'usefulVoteCount':**,'nickname':**}]）
###score=1代表差评，score＝2代表中评，score＝3代表好评

def getComment(phone_id,flag,score):
	page = 0
	Comments = []
	while flag==True:
		s = requests.session()
		url = 'https://club.jd.com/comment/productPageComments.action'
		data = {
			'productId':phone_id,
			'score':score,
			'sortType':5,
			'page':page,
			'pageSize':10,
			'isShadowSku':0,
			'fold':1
		}
		r = s.get(url,params=data)
		try:

			comment_list = []
			
			comment_list =  r.json()['comments']#评论
			
			print 'comment_list',len(comment_list)
			if(len(comment_list)==0):
				flag==False
				break
			else:
				page = page + 1
				for list0 in comment_list:
					# print type(list0),json.dumps(list0, encoding="UTF-8", ensure_ascii=False, sort_keys=False, indent=4) #type: dict
					tmp = json.dumps(list0, encoding="UTF-8", ensure_ascii=False, sort_keys=False, indent=4)
					dic_tmp = {}
					dic_tmp['nickname'] = list0['nickname']
					dic_tmp['content'] = list0['content']
					dic_tmp['score'] = list0['score']
					dic_tmp['creationTime'] = list0['creationTime']
					dic_tmp['usefulVoteCount'] = list0['usefulVoteCount']
					dic_tmp['replyCount'] = list0['replyCount']
					dic_tmp['score_type'] = score_type[score-1]
					json.dumps(dic_tmp,encoding="UTF-8", ensure_ascii=False,sort_keys=False, indent=4)
					Comments.append(dic_tmp)

			time.sleep(random.randint(4,5))
		except:
			print "page",page,len(Comments)
			return Comments

	print "page",page,len(Comments)
	return Comments



conn = ConnectMongodb.Connect(10001)#连接数据库 
brandList = getPhoneBrands(phone_url)
firefox_login=webdriver.Firefox()
for x in range(0,15):
	brand = conn[str(brandList[x])]
	linkList = get_all_brand_links(brandList[x])


	for y in range(0,len(linkList)):
		#将list0['name']写入mongodb数据库中，代表手机型号
		phone_type = brand[linkList[y]['name']] #创建集合

		otherInfo = getOtherInfo(linkList[y]['id'])
		phone_type.insert(otherInfo)

		hot_list = getConcern(linkList[y]['id'])
		if(len(hot_list)>0):
			phone_type.insert(hot_list)


		for z in range(1,4):
			CommentsList = getComment(linkList[y]['id'],True,z)
			#将Comments字典写入mongodb数据库中，代表手机所有评论
			if(len(CommentsList)>0):
				phone_type.insert(json.loads(json.dumps(CommentsList)))
firefox_login.quit()

#写入rep2分片
conn1 = ConnectMongodb.Connect(10002)#连接数据库 
brandList = getPhoneBrands(phone_url)
firefox_login=webdriver.Firefox()
for x in range(15,30):
	brand = conn1[str(brandList[x])]
	linkList = get_all_brand_links(brandList[x])


	for y in range(0,len(linkList)):
		#将list0['name']写入mongodb数据库中，代表手机型号
		phone_type = brand[linkList[y]['name']] #创建集合

		otherInfo = getOtherInfo(linkList[y]['id'])
		phone_type.insert(otherInfo)

		hot_list = getConcern(linkList[y]['id'])
		if(len(hot_list)>0):
			phone_type.insert(hot_list)
		
		for z in range(1,4):
			CommentsList = getComment(linkList[y]['id'],True,z)
			#将Comments字典写入mongodb数据库中，代表手机所有评论
			if(len(CommentsList)>0):
				phone_type.insert(json.loads(json.dumps(CommentsList)))
firefox_login.quit()

#写入rep3分片
conn2 = ConnectMongodb.Connect(10003)#连接数据库 
brandList = getPhoneBrands(phone_url)
firefox_login=webdriver.Firefox()
for x in range(30,41):
	brand = conn2[str(brandList[x])]
	linkList = get_all_brand_links(brandList[x])


	for y in range(0,len(linkList)):
		#将list0['name']写入mongodb数据库中，代表手机型号
		phone_type = brand[linkList[y]['name']] #创建集合

		otherInfo = getOtherInfo(linkList[y]['id'])
		phone_type.insert(otherInfo)

		hot_list = getConcern(linkList[y]['id'])
		if(len(hot_list)>0):
			phone_type.insert(hot_list)

		for z in range(1,4):
			CommentsList = getComment(linkList[y]['id'],True,z)
			#将Comments字典写入mongodb数据库中，代表手机所有评论
			if(len(CommentsList)>0):
				phone_type.insert(json.loads(json.dumps(CommentsList)))
firefox_login.quit() 










		







