#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import ssl
import os
import operator
import sys


basepath = "https://www.udeler.com"
login_url = "/login"
proxy_url = "/proxy"
links_url = "/links"
course_link = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size={0}"


def print_success(toprint, ret=''):
	sys.stdout.write('\033[92m' + toprint +  '\033[0m' + ret)
	sys.stdout.flush()

	
def print_warning(toprint, ret=''):
	sys.stdout.write('\033[93m' + toprint +  '\033[0m' + ret)
	sys.stdout.flush()

	
def print_error(toprint, ret=''):
	sys.stdout.write('\033[91m' + toprint +  '\033[0m' + ret)
	sys.stdout.flush()

	
def valid_filename(s):
	s = u''.join(s).encode('utf-8').strip()
	for i in "/\-":
		s = s.replace(i, '')
	return s


def request(data, path):
	data = urllib.urlencode(data)
	req = urllib2.Request(basepath + path, data)
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
	return json.loads(urllib2.urlopen(req, context=gcontext).read())


def login(user, passwd):
	print_warning("Try to login")
	data = request([("email", user), ("password", passwd)], login_url)
	if 'access_token' in data:
		print_success(" successfully", "\n")
		return data['access_token']
	else:
		print_error(" failed", "\n")
		return False


def get_courses(token, courses=50):
	print_warning("Fetching courses...")
	link = course_link.format(courses)
	data = request([("url", link), ("access_token", token)], proxy_url)
	while data['next'] != None:
		other = request([("url", data['next']), 
		("access_token", token)], proxy_url)
		data['results'].extend(other['results'])
		data['next'] = other['next']
	data['count'] = len(data['results'])
	print_success("{0} courses found:".format(data['count']), "\n")
	if data['count']:
		return data['results']
	return False # no courses founded


def get_course_links(token, course):
	print_warning("Fetching course data...")
	cid = course['id']
	ctitle = course['title']
	curl = course['url']
	data = request([("sub_domain", "www"), ("course_id", cid), 
		("course_url", curl), ("course_name", ctitle), 
		("access_token", token),("skip_attachments", "true"), 
		("skip_subtitles", "true"), ("video_quality", "Highest")], 
		links_url)
	print_success("done", "\n")
	return data
	
	
def download_video(url, name):
	filedata = urllib2.urlopen(url)  
	datatowrite = filedata.read()
	with open(name + ".mp4", 'wb') as f:  
		f.write(datatowrite)
	
	
def download_chapter(count, chapter):
	name = "{0}. {1}".format(count, valid_filename(chapter['name']))
	print_warning("DOWNLOADING CHAPTER: " + chapter['name'], "\n")
	os.mkdir(name)
	os.chdir(name)
	lect = 1
	for lecture in chapter['lectures']:
		sys.stdout.write("Downloading lecture: " + lecture['name'])
		sys.stdout.flush()
		download_video(lecture['src'], "{0}. {1}".format(lect,
			valid_filename(lecture['name'])))
		print_success(" done", "\n")
		lect+=1
	os.chdir('..')
	print_success("FINISHED CHAPTER: " + chapter['name'], "\n")
	
	
def download_course(course):
	print_warning("Downloading...", "\n")
	chapters = sorted(course['chapters'])
	cname = valid_filename(course['name'])
	try:
		os.mkdir(cname)
	except OSError:
		print_error("Error: unable to create directory", "\n")
		return False
	os.chdir(cname)
	count = 1
	for i in chapters:
		download_chapter(count, course['chapters'][i])
		count+=1
	print_success("Done", "\n")
		
