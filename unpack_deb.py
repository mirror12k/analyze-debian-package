#!/usr/bin/env python


import sys






def main():
	if len(sys.argv) < 2:
		print ".deb package filepath required"
	else:
		filepath = sys.argv[1]
		print "got file:", filepath


if __name__ == '__main__':
	main()
