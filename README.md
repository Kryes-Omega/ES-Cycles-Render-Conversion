# ES-Cycles-Render-Conversion
A python script using blender's API to convert the existing Endless Sky models to Cycles materials and lights, and automatically render them as properly sized sprites and thumbnails

## Requirements:
- Blender 2.83
- I have no idea if this runs on Mac or Linux as I only have Windows, so probably have Windows

## Usage
Place blend files you want to use in the "ship blend" folder, and if you have pre-rendered images of the correct scale you can place them in "ship img" 
jsongather.py will auto generate a JSON file with the dimensions and other data  from the images in the "ship img" folder. If you use jsongather.py I still recommend checking the JSON file for missing data. The JSON structure is as follows:

{
    "EXAMPLE": {
        "sprite": "example.png",
        "shape": [
            height,
            width
        ],
        "blend": "example.blend"
    }
}

To run the script, open "test.blend" in Blender 2.83 (highly recommended to open from the command prompt to see progress and script output) and press the run script button in the top bar of the text editor area. If you didn't open in the command prompt, Blender will just appear to freeze. This is normal, its working as long as you haven't gotten an error. Run time depends on the number and complexity of the blends. 

The script creates a new subfolder "output" where all the new files will be saved.
