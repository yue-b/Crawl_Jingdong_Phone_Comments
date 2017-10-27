#coding=utf-8
#!/usr/bin/env python
import pymongo
from pymongo import MongoClient



# host = '127.0.0.1'
host = '172.17.189.140'

def Connect(port):
	conn = MongoClient(host,port)
	print conn
	return conn