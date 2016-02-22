#!/usr/bin/env python


import sys
from arfile import ArFile





def main():
	if len(sys.argv) < 2:
		print ".deb package filepath required"
	else:
		filepath = sys.argv[1]
		deb = ArFile(filepath)
		print "files: ", deb.filenames()
		deb.extractAll('test')

if __name__ == '__main__':
	main()
