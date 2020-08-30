import bpy
import os
import json
import sys
import mathutils
from mathutils import Vector


print("BEGINNING OF RUN")

# os.path.abspath(__file__) returns path to the script
currentdir = bpy.path.abspath("//")
print("script dir: " + currentdir)
shipdir = os.path.join(currentdir, "ships/")
print("ships dir: " + shipdir)
ships = os.listdir(shipdir)
print("affected files:")
print(ships)
print("\n")
ship_dict = {}
skipped = []

def cleanup():
	# delete unused data
	print("\n" + "Cleaning up for conversion...")
	for obj in bpy.data.lights:
		print("deleted" + str(obj))
		bpy.data.lights.remove(obj, do_unlink=True)

	for obj in bpy.data.cameras:
		print("deleted" + str(obj))
		bpy.data.cameras.remove(obj, do_unlink=True)

	for block in bpy.data.meshes:
		if block.users == 0:
			bpy.data.meshes.remove(block)

	for block in bpy.data.materials:
		if block.users == 0:
			bpy.data.materials.remove(block)

	for block in bpy.data.collections:
		if block.users == 0:
			bpy.data.collections.remove(block)
	return

# overrideArea will change the area context to whatever is specified. If the area is not present on the screen, it changes the first area to the needed one.
def overrideArea(override_area):
	# make a new copy of the context to edit
	override = bpy.context.copy()
	# redefine context manually
	for window in bpy.context.window_manager.windows:
		screen = window.screen

		override_success = False
		for area in screen.areas:
			if area.type == override_area:
				override = {"window": window, "screen": screen, "area": area}
				override_success = True
		if override_success == False:
			screen.areas[0].ui_type = override_area
			for area in screen.areas:
				if area.type == override_area:
					override = {"window": window, "screen": screen, "area": area}


	print(override)
	return override

def setup():
	# check to see if the json file exists. If not, the script wont work so exit. If it does, open it and load it as ship_dict
	global ship_dict # ship_dict needs to be referenced as global so when this function edits it, the global variable is edited as well.
	if not "render_info.json" in os.listdir(currentdir):
		print("Aborting: Missing render info json")
		sys.exit()
	else:
		jsonfile = os.path.join(currentdir, "render_info.json")
		with open(jsonfile) as f:
			ship_dict = json.load(f)

	# make two arrays to hold the missings
	in_ships_not_dict = []
	in_dict_not_ships = []
	blend_defs_list = []

	# check if each definition has a matching blend, if not: add it to in_dict_not_ships
	for key, value in ship_dict.items():
		blend_defs_list.append(value["blend"])
		if not value["blend"].casefold() in ships:
			in_dict_not_ships.append(value["blend"])

	# check if each file in the ships folder has a definition, if not: add it to in_ships_not_dict
	for file in ships:
		if not str(file).casefold() in blend_defs_list:
			in_ships_not_dict.append(file)

	# print both arrays showing whats missing
	print("Blend but no definition:")
	print(in_ships_not_dict)
	print("\n")
	print("Definition but no blend:")
	print(in_dict_not_ships)
	return

def render(angle, file, shape=[1080, 1080]):
	print("\n" + "Changing render settings...")
	bpy.context.scene.render.engine = "CYCLES"
	bpy.context.scene.cycles.device = "GPU"
	bpy.context.scene.cycles.samples = 512
	bpy.context.scene.render.tile_y = 128
	bpy.context.scene.render.tile_x = 128
	bpy.context.scene.render.image_settings.compression = 100
	bpy.context.view_layer.cycles.use_denoising = True
	bpy.context.view_layer.cycles.denoising_strength = 0.25
	bpy.context.view_layer.cycles.denoising_feature_strength = 0.25




	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[angle + " render"]
	bpy.context.scene.camera = bpy.data.objects[angle + "Camera"]

	for coll in bpy.data.collections:
		# if the collection is a render collection but is not the specified one, hide it.
		if coll.name[-6:] == "render" and not coll.name == (angle + " render"):
			print("Hiding " + coll.name)
			coll.hide_render = True
		else:
			print("Unhiding " + coll.name)
			coll.hide_render = False

	anim = False
	name_to_dir = str(os.path.splitext(file)[0]) + "/"
	if angle == "sprite":

		bpy.context.scene.render.resolution_x = shape[1]
		bpy.context.scene.render.resolution_y = shape[0]

		for obj in bpy.data.objects:
			if obj.animation_data is not None:
				anim = True
				break
		if anim == True:
			# render normal size
			outputpath = os.path.join(currentdir, "output/", name_to_dir, "sprite/", str(os.path.splitext(file)[0]), "-#")
			print("outputting to " + outputpath)
			bpy.context.scene.render.filepath = outputpath
			bpy.context.scene.render.resolution_percentage = 100
			print("Rendering " + angle + " animation...")
			bpy.ops.render.render(animation=True)

			# render 2x
			outputpath = os.path.join(currentdir, "output/", name_to_dir, "sprite/", str(os.path.splitext(file)[0]), "@2x-#")
			bpy.context.scene.render.filepath = outputpath
			bpy.context.scene.render.resolution_percentage = 200
			print("Rendering " + angle + " 2x animation...")
			bpy.ops.render.render(animation=True)

		else:
			outputpath = os.path.join(currentdir, "output/", name_to_dir, "sprite/", str(os.path.splitext(file)[0]))
			print("outputting to " + outputpath)
			bpy.context.scene.render.filepath = outputpath
			bpy.context.scene.render.resolution_percentage = 100
			print("Rendering " + angle + "image...")
			bpy.ops.render.render(write_still=True)

			# render 2x
			outputpath = os.path.join(currentdir, "output/", name_to_dir, "sprite/", str(os.path.splitext(file)[0]) + "@2x")
			bpy.context.scene.render.filepath = outputpath
			bpy.context.scene.render.resolution_percentage = 200
			print("Rendering " + angle + "2x image...")
			bpy.ops.render.render(write_still=True)

	elif angle == "thumb":

		bpy.context.scene.render.resolution_x = 260
		bpy.context.scene.render.resolution_y = 260

		outputpath = os.path.join(currentdir, "output/", name_to_dir, "thumb/", str(os.path.splitext(file)[0]))
		print("outputting to " + outputpath)
		bpy.context.scene.render.filepath = outputpath
		bpy.context.scene.render.resolution_percentage = 100
		print("Rendering " + angle + "image...")
		bpy.ops.render.render(write_still=True)

		outputpath = os.path.join(currentdir, "output/", name_to_dir, "thumb/", str(os.path.splitext(file)[0]) + "@2x")
		bpy.context.scene.render.filepath = outputpath
		bpy.context.scene.render.resolution_percentage = 200
		print("Rendering " + angle + "2x image...")
		bpy.ops.render.render(write_still=True)

	# hide collection from render view for next pass
	bpy.data.collections[angle + " render"].hide_render = True


def main():
	setup()
	# for defined ship in dict
	filepath = ""
	for key, value in ship_dict.items():
		file = ""
		for f in ships:
			if f == ship_dict[key]["blend"]:
				file = f
				filepath = os.path.join(shipdir, file)
				print(filepath)
				break
		if file == "":
			skipped.append(key)
			continue

		name_to_dir = str(os.path.splitext(file)[0]) + "/"
		print("running on " + filepath + " (" + str(ships.index(file)+1) + "/" + str(len(ships)) + ")" + "\n")
		# open the active file in the folder
		bpy.ops.wm.open_mainfile(filepath=filepath)
		
		cleanup()

		# before this point, a JSON file containing ship dimensions should be read and the dimensions passed to settings() so it can adjust accordingly
		shape = []
		for key, value in ship_dict.items():
			if str(value["blend"]).casefold() == file:
				shape = value["shape"]
				break

		print("\n" + "Duplicating ship mesh for render...")
		bpy.context.scene.cursor.location = (25.0, 25.0, 0.0) # move this before editing context because it fucks it up hard

		
		override = overrideArea(override_area="VIEW_3D")

		# move off to the side and make a copy of the original
		bpy.context.view_layer.objects.active = bpy.data.objects[0]
		bpy.ops.object.select_all(override, action="SELECT")
		bpy.ops.view3d.snap_selected_to_cursor(override, use_offset=True)
		bpy.ops.object.duplicate(override, linked=False, mode="INIT")


		# create the ship object for rendering and move it to center
		bpy.ops.object.convert(override, target="MESH")
		bpy.ops.object.join(override)

		bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

		bpy.ops.object.transform_apply(override, location=False, rotation=True, scale=True)
		bpy.ops.object.origin_set(override, type="ORIGIN_CENTER_OF_VOLUME")
		bpy.ops.view3d.snap_selected_to_cursor(override, use_offset=True)

		# resize, rename, and center the object
		for o in bpy.context.scene.objects:
			if o.select_get():
				o.name = "ship_obj"
				scale = 0
				if bpy.data.objects[o.name].dimensions[0] > bpy.data.objects[o.name].dimensions[1]:
					bpy.data.objects[o.name].dimensions[0] = 9.0
					scale = bpy.data.objects[o.name].scale[0]

				else:
					bpy.data.objects[o.name].dimensions[1] = 9.0
					scale = bpy.data.objects[o.name].scale[1]
				bpy.data.objects[o.name].scale = (scale, scale, scale)
				# the scale needs to be applied otherwise blender will act like a gremlin and you will hate your life.
				bpy.ops.object.transform_apply(override, scale=True)

		# math to find the bounding box center for the ship. This is will allow the script to actually center the object for the camera
		local_bbox_center = 0.125 * sum((Vector(b) for b in bpy.data.objects["ship_obj"].bound_box), Vector())
		print(local_bbox_center)
		print(bpy.data.objects["ship_obj"].matrix_world)
		global_bbox_center = bpy.data.objects["ship_obj"].matrix_world @ local_bbox_center
		print(global_bbox_center)
		bpy.context.scene.cursor.location = global_bbox_center
		print(bpy.context.scene.cursor.location)

		bpy.ops.object.origin_set(override, type="ORIGIN_CURSOR")
		bpy.data.objects["ship_obj"].location = (0.0, 0.0, 0.0)


		# convert materials to Principled shaders with basic settings
		print("\n" + "Converting materials...")
		for mat in bpy.data.materials:
			if mat.use_nodes == False:
				mat.use_nodes = True
				mat.node_tree.nodes["Principled BSDF"].inputs[4].default_value = 1.0 # fully metallic
				# change roughness depending on basic material name
				if mat.name[:7].casefold() == "painted":
					mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.75
				elif mat.name[:5].casefold() == "metal":
					mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.6
				elif mat.name[:6].casefold() == "bridge":
					mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.42
				else:
					mat.node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.57





		# loop creating new objects for both sprite and thumbnail collections
		layers = ["sprite", "thumb"]
		for name in layers:
			print("\n" + "Creating " + name + "lights and camera")
			# create new collection and link to scene
			view_layer = bpy.context.view_layer # reduce bpy.context spam
			coll = 0
			if bpy.data.collections.get(name + " render") is not None:
				coll = bpy.data.collections[name + " render"]
			else:
				coll = bpy.data.collections.new(name + " render")
				bpy.context.scene.collection.children.link(coll)

			layerColl = bpy.context.view_layer.layer_collection.children[coll.name]
			bpy.context.view_layer.active_layer_collection = layerColl

			# create new sprite lights and camera
			view_layer.active_layer_collection.collection.objects.link(bpy.data.objects.new(name=name + "Camera", object_data=bpy.data.cameras.new(name + "Camera")))
			view_layer.active_layer_collection.collection.objects.link(bpy.data.objects.new(name=name + "SunKey", object_data=bpy.data.lights.new(name + "SunKey", "SUN")))
			view_layer.active_layer_collection.collection.objects.link(bpy.data.objects.new(name=name + "AreaFill", object_data=bpy.data.lights.new(name + "AreaFill", "AREA")))
			view_layer.active_layer_collection.collection.objects.link(bpy.data.objects.new(name=name + "AreaBack", object_data=bpy.data.lights.new(name + "AreaBack", "AREA")))
			
			# write the object data locations as variables for ez access
			Camera = bpy.context.scene.objects[name + "Camera"]
			SunKey = bpy.context.scene.objects[name + "SunKey"]
			AreaFill = bpy.context.scene.objects[name + "AreaFill"]
			AreaBack = bpy.context.scene.objects[name + "AreaBack"]

			# setup lights and camera based on name
			if name == "sprite":
				Camera.location = (0.0, 0.0, 10.0)
				bpy.data.cameras[name + "Camera"].type = "ORTHO"
				bpy.data.cameras[name + "Camera"].ortho_scale = 9.3

				SunKey.location = (5.4, 4.65, 3.8)
				SunKey.rotation_euler = (0, 1.22, 0.909)
				SunKey.data.color = (1.0, 0.845, 0.812)
				SunKey.data.energy = 3.05
				SunKey.data.angle = 0.226

				AreaFill.location = (4.5, 2.0, 2.4)
				AreaFill.rotation_euler = (0.0, 1.1, 0.28)
				AreaFill.data.color = (0.335, 0.72, 1.0)
				AreaFill.data.energy = 205.0
				AreaFill.data.size = 9.12

				AreaBack.location = (-4.4, -3.4, 4.3)
				AreaBack.rotation_euler = (0.0, -0.94, 0.75)
				AreaBack.data.color = (1.0, 0.23, 0.18)
				AreaBack.data.energy = 20.0
				AreaBack.data.size = 12.0
				AreaBack.data.cycles.cast_shadow = False
			elif name == "thumb":
				Camera.location = (14.5, 23.8, 19.2)
				Camera.rotation_euler = (0.96, 0.0, 2.62)
				bpy.data.cameras[name + "Camera"].type = "ORTHO"
				bpy.data.cameras[name + "Camera"].ortho_scale = pow(1.17, bpy.data.objects["ship_obj"].dimensions[0]) + 6
				SunKey.location = (5.1, 1.3, 2.0)
				SunKey.rotation_euler = (0.0, 1.2, 0.12)
				SunKey.data.color = (1.0, 0.91, 0.66)
				SunKey.data.energy = 2.3
				SunKey.data.angle = 0.44

				AreaFill.location = (4.35, 3.15, 3.7)
				AreaFill.rotation_euler = (0.0, 0.94, 0.5)
				AreaFill.data.color = (0.244, 0.55, 1.0)
				AreaFill.data.energy = 220.0
				AreaFill.data.size = 8.22

				AreaBack.location = (-3.3, -1.7, 4.0)
				AreaBack.rotation_euler = (0.0, 0.8, -2.51)
				AreaBack.data.color = (1.0, 0.25, 0.1)
				AreaBack.data.energy = 30.0
				AreaBack.data.size = 8.03
				AreaBack.data.cycles.cast_shadow = False

		render(angle="sprite", file=file, shape=shape)
		render(angle="thumb", file=file, shape=shape)
		# should be the last thing the script does to a file for obvious reasons
		print("\n" + "Saving new blend...")
		outputpath = os.path.join(currentdir, "output/", name_to_dir, file)
		print("outputting to " + outputpath)
		bpy.ops.wm.save_mainfile(filepath=outputpath)
	

	print("\nTask finished.")
	print("skipped:\n")
	print(skipped)


if __name__ == "__main__":
	main()