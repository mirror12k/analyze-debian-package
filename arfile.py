

# couldn't file .ar file support in python
# so i made my own
# so much for 'import antigravity'



class ArFileException(Exception):
	'''generic error in reading or parsing the .ar file'''
	pass


class ArFileDescriptor(object):
	'''simple container for metadata about a file in a .ar archive'''
	def __init__(self, filename, timestamp, ownerID, groupID, filemode, filesize):
		self.filename = self.chomp(filename)
		self.timestamp = int(self.chomp(timestamp))
		self.ownerID = int(self.chomp(ownerID))
		self.groupID = int(self.chomp(groupID))
		self.filemode = self.chomp(filemode)
		self.filesize = int(self.chomp(filesize))

		self.offset = None # offset to the raw file data inside the archive
	def chomp(self, s):
		'''chomps off space characters from the end of the string'''
		while len(s) > 0 and s[-1] == ' ':
			s = s[:-1]
		return s
	def __str__(self):
		return "<ar file descriptor>("+\
			"filename='"+self.filename+"',"+\
			"timestamp="+str(self.timestamp)+","+\
			"ownerID="+str(self.ownerID)+","+\
			"groupID="+str(self.groupID)+","+\
			"filemode='"+self.filemode+"',"+\
			"filesize="+str(self.filesize)+","+\
			"offset="+str(self.offset)+\
			")"

class ArFile(object):
	'''
	class for reading unix ar archives ('.ar' and '.deb' files)
	writing archives is currently unsupported
	'''
	def __init__(self, filepath):
		self.magic = "!<arch>\n"
		self.readChunk = 16 * 4096

		self.filepath = filepath
		self.handle = open(filepath, 'rb')
		self.fileDescriptors = []
		self.readStructure()
	def readStructure(self):
		fileMagic = self.handle.read(len(self.magic))
		offset = len(self.magic)
		if fileMagic != self.magic:
			raise ArFileException('invalid file magic: "'+fileMagic+'" (expected "'+ self.magic+'")')
		eof = False
		while eof is False:
			if offset % 2 == 1: # ar file descriptors always start on an even boundary
				padding = self.handle.read(1)
				if len(padding) == 0:
					eof = True
				else:
					if padding != "\n":
						raise ArFileException('invalid file padding: "'+padding+'"')
					offset += 1
			if eof is False:
				descriptor = self.readFileDescriptor()
				if descriptor is None:
					eof = True
				else:
					offset += 60
					descriptor.offset = offset
					# print "got descriptor:", str(descriptor)
					self.fileDescriptors.append(descriptor)

					offset += descriptor.filesize
					self.handle.seek(offset)

	def readFileDescriptor(self):
		header = self.handle.read(60)
		if len(header) == 0: # eof reached
			return None
		elif len(header) < 60: # didn't get a complete header
			raise ArFileException('eof before complete header!')
		else: # got a header block
			if header[58:60] != "`\n":
				print "debug: ", header
				raise ArFileException('invalid file header magic: "'+header[58:60]+'"')
			else:
				return ArFileDescriptor(
					filename=header[0:16],
					timestamp=header[16:28],
					ownerID=header[28:34],
					groupID=header[34:40],
					filemode=header[40:48],
					filesize=header[48:58],
				)
	def files(self):
		return self.fileDescriptors
	def filenames(self):
		return [ desc.filename for desc in self.fileDescriptors ]
	def extract(self, desc, path='.'):
		filepath = path+'/'+desc.filename.replace('/', '_') # a little bit of security
		with open(filepath, 'w') as dest:
			self.handle.seek(desc.offset)
			bytesLeft = desc.filesize
			while bytesLeft > 0:
				if bytesLeft >= self.readChunk:
					dest.write(self.handle.read(self.readChunk))
					bytesLeft -= self.readChunk
				else:
					dest.write(self.handle.read(bytesLeft))
					bytesLeft = 0
	def extractAll(self, path='.'):
		for desc in self.files():
			self.extract(desc, path)










