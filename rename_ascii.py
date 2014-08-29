import os

folder = r"U:\HDEM_v3r3\Export\Variable\ascii_tiles"

for file in os.listdir(folder):
	#print file
	fileNameParts = file.split('.')
	if len(fileNameParts) == 3:
		base = fileNameParts[0]
		ext = fileNameParts[2]
		newName = base + '.' + ext
	elif len(fileNameParts) == 4:
		base = fileNameParts[0]
		ext1 = fileNameParts[2]
		ext2 = fileNameParts[3]
		newName = base + '.' + ext1 + '.' + ext2
	print newName
	os.rename(os.path.join(folder, file), os.path.join(folder, newName))