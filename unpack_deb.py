#!/usr/bin/env python3


import sys
from arfile import ArFile
import tarfile


# http://manpages.debian.org/cgi-bin/man.cgi?query=deb&manpath=unstable


def main():
	if len(sys.argv) < 2:
		print (".deb package filepath required")
	else:
		filepath = sys.argv[1]
		deb = ArFile(filepath)

		debbinDescriptor = deb.descriptorFromFilename('debian-binary')
		if debbinDescriptor is not None:
			print('debian-binary found')

			deb.extract(debbinDescriptor, 'test')
			with open('test/debian-binary', mode='r') as f:
				# print(f.read())
				binlines = [ s.strip() for s in f.readlines() ]

			if len(binlines) < 1:
				print('warning: empty debian-binary')
			else:
				if binlines[0] != '2.0':
					print('warning: unknown deb file version:', binlines[0])
				else:
					print('deb file version 2.0')

				if len(binlines) > 1:
					print('warning: unknown extraneous debian-binary lines:')
					for line in binlines[1:]:
						print(line)

		print()

		controlDescriptor = deb.descriptorFromFilename('control.tar.gz')
		if controlDescriptor is not None:
			print('control.tar.gz found')

			deb.extract(controlDescriptor, 'test')
			archive = tarfile.open('test/control.tar.gz', 'r')
			# print ('got archive files: ', archive.getnames())

			controlfile = archive.getmember('./control')
			if controlfile is not None and controlfile.isfile():
				print('found package control file: "'+controlfile.name+'"')
				archive.extract(controlfile, path='test')
				with open('test/control', 'r') as f:
					lines = [ s.strip() for s in f.readlines() ]

				print("control file lines:")
				for line in lines:
					print('\t'+line)
			else:
				print('warning: package control file missing!')

			preinst = archive.getmember('./preinst')
			if preinst is not None and preinst.isfile():
				print('found pre-installation script: "'+preinst.name+'"')
			postinst = archive.getmember('./postinst')
			if postinst is not None and postinst.isfile():
				print('found post-installation script: "'+postinst.name+'"')
			prerm = archive.getmember('./prerm')
			if prerm is not None and prerm.isfile():
				print('found pre-removal script: "'+prerm.name+'"')
			postrm = archive.getmember('./postrm')
			if postrm is not None and postrm.isfile():
				print('found post-removal script: "'+postrm.name+'"')

			conffiles = archive.getmember('./conffiles')
			if conffiles is not None and conffiles.isfile():
				print('found conffiles list: "'+conffiles.name+'"')
				archive.extract(conffiles, path='test')
				with open('test/conffiles', 'r') as f:
					lines = [ s.strip() for s in f.readlines() ]
				print('configuration files:')
				for line in lines:
					print('\t'+line)
			
			md5sums = archive.getmember('./md5sums')
			if md5sums is not None and md5sums.isfile():
				print('found md5sums list: "'+md5sums.name+'"')
				archive.extract(md5sums, path='test')
				with open('test/md5sums', 'r') as f:
					lines = [ s.strip() for s in f.readlines() ]
				print('md5 sums:')
				for line in lines:
					print('\t'+line)

			for file in [ mem for mem in archive.getmembers() ]:
				if not file.isdir():
					if file.name not in ['./control', './preinst', './postinst', './prerm', './postrm', './conffiles', './md5sums' ]:
						print('warning: unknown file in control archive: "'+file.name+'"')

		print()

		dataDescriptor = deb.descriptorFromFilename('data.tar.xz')
		if dataDescriptor is not None:
			print('data.tar.xz found')

			deb.extract(dataDescriptor, 'test')
			archive = tarfile.open('test/data.tar.xz', 'r')
			# print ('got archive files: ', archive.getnames())
			files = sorted([ mem for mem in archive.getmembers() if not mem.isdir() ], key=lambda mem: mem.name)
			print("all loaded files:")
			for file in files:
				if file.issym() or file.islnk():
					print ('\t'+file.name+' -> '+file.linkname)
				else:
					print ('\t' + file.name+' - '+str(file.size)+' bytes')

		print()

		for filename in deb.filenames():
			if filename not in ['debian-binary', 'control.tar.gz', 'data.tar.xz']:
				print('warning: unknown file in debian package: "'+filename+'"')

		print('end of debian package')



if __name__ == '__main__':
	main()
