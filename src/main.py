#!/usr/bin/env python
# -*- coding: utf-8 -*-
import getpass
import udemydl


__version__ = '0.1'
__author__ = 'Andrea Dipace'


def main():
	username = raw_input("Insert email: ")
	password = getpass.getpass("Insert password: ")
	
	token = udemydl.login(username, password)
	
	if not token:
		return
	
	courses = udemydl.get_courses(token)
	if not courses:
		return
		
	for i in range(len(courses)):
		print "{0}\t{1}".format(i, u''.join(courses[i]['title'])
			.encode('utf-8').strip())
	
	while True:
		try:
			select = input("Select a course: ")
		except KeyboardInterrupt:
			break
		except:
			print "Insert a number"
		else:
			if select >= 0 and select < len(courses):
				course = courses[select]
				chapters = udemydl.get_course_links(token, course)
				udemydl.download_course(chapters)
				break
			else:
				print "Insert a valid number"


if __name__ == "__main__":
	main()
