import os
import json
from PIL import Image



def main():
	currentdir = os.path.dirname(os.path.abspath(__file__))
	imgdir = os.path.join(currentdir, "ship img\\")
	blenddir = os.path.join(currentdir, "ship blend\\")

	render_info = {}
	name = ""
	sprite = ""
	shape = []
	blend = ""

	missing_blends = []

	# loop through data for each sprite image
	for imgfile in os.listdir(imgdir):
		# name_full includes the frame number for animated images
		name_full = os.path.splitext(imgfile)[0]
		# make sure it is a PNG
		if os.path.splitext(imgfile)[1] != ".png":
			print("skipping " + imgfile)
			continue
		# if it is, make sure its only processing one entry (or two if there are more than 10 frames, what can ya do)
		elif name_full[-3:].find("-") != -1 or name_full[-3:].find("=") != -1 or name_full[-3:].find("+") != -1:
			# if its a duplicate, just continue
			if name_full[-1:] != "0":
				print("skipping " + imgfile)
				continue
			# split the frame counter off of the name
			elif name_full[-3:].find("-") != -1:
				name = name_full.rsplit("-")[0]
			elif name_full[-3:].find("=") != -1:
				name = name_full.rsplit("=")[0]
			elif name_full[-3:].find("+") != -1:
				name = name_full.rsplit("+")[0]

		else:
			name = name_full
		with Image.open(os.path.join(imgdir, imgfile)) as img:
			shape = list(img.size) #size outputs as width, height but the data needs to be height, width
			shape.reverse()
			sprite = imgfile

		# loop through each blend file to see if we can automatically pick it up based on ship name
		for blendfile in os.listdir(blenddir):
			if str(os.path.splitext(blendfile)[0]).casefold() == name:
				blend = blendfile
				break
			else:
				blend = "data missing"

		if blend == "data missing":
			missing_blends.append(name)
		render_info[name.upper()] = {"sprite": sprite, "shape": shape, "blend": blend}




	# dump collected data to render_info.json
	with open(os.path.join(currentdir, "render_info.json"), 'w') as f:
		json.dump(render_info, f, indent=4)

	# print the missing files
	print("\nMissing blends for:")
	print(missing_blends)

	return

if __name__ == "__main__":
	main()