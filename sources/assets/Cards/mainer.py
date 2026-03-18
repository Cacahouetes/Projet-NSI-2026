import os 
cnum = 0
def compress(path):
	global cnum
	
	fl = path.split("/")[-1]

	if not "." in fl:
		for file in os.listdir(path):
			compress(path+"/"+file)
	else:
		cnum+=1
		os.system(f"ffmpeg -i {path[:-4]}.png -vf scale=720:1008 -v quiet {path[:-4]}.jpg")
		print(path)

compress(os.getcwd())
print(cnum)
