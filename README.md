# 1.0.0
This toolkit is a Blender addon/plugin for the video game Spider-Man: Web of Shadows

This addon is designed on Blender 4.5.0 mainly, then compatibility has been tested and confirmed for Blender 5.0.0
and it could very possibly work on other untested versions of Blender, especially 4.1+

# Features:
- Import and Export the game's model format (.wrap.mesh) to/from Blender (drag-and-drop supported for import)

- Import/Export the game's skeleton format (.wrap.skel) to Blender (drag-and-drop supported for import)

- Convert the game's texture format (.wrap.tex) to DDS and vice versa (drag-and-drop feature)

Use latest version of [WebOfShadowsTools](https://github.com/kirbystealer/WebOfShadowsTools) to extract said files

- The addon presents an extra feature which you can find in the side-panel. Press N to open Blender's side-panel, then go to the WOS Tools tab, there you can find the Rename Vertex Groups Utility.
	- Use this utility to rename a model's vertex groups from the "bone_{index}" naming to the real bone names imported with the skeleton (Armature needs to be in same collection or the utility will raise an error)

- The addon also presents some options on importing/exporting model format, which are:
	- Flip UV V-Axis 
	- Flip Face Normals
	- Flip Vertex Normals
	- Convert Triangle Strips
	


# Notes:
- Max vertex groups count for each submesh is 48, otherwise the mesh deformation will look off

- For custom model ports, rename your materials to the name of any material file the original model uses, full name could work but preferred to only take the hash part, like: `0x9E8F3E7F`

- It is advised to use Data Transfer modifier to transfer weights from original models to modded ones, use Replace as Mix Mode and a Mapping of Nearest Vertex

- Each submesh needs a vertex color attribute of some value, use Face Corner and Byte Color when creating the attribute, then make it White if you want fully opaque vertex color
	- If you don't set a vertex color, the model will look complete black in-game
	
- All submeshes under a single collection need to be parented to the armature so that weights can be exported correctly

- To convert to the game's texture files you need a DDS file to drag and drop into Blender's 3D Viewport
  - If you don't have your image file ready in the DDS format, then you can use this [SimpleTextureConverter](https://www.nexusmods.com/site/mods/1539) tool to convert back-and-forth between a lot of image formats including DDS
	
- It is advised to use the default values of the Import Options for original game models and models that have been tweaked to match the game settings when exported

- For custom model ports, try tweaking the Export Options to match the best result for you in-game
	- If textures don't look right, use the Flip UV V-Axis option
	- If model looks transparent/see-through, use the Flip Face Normals option
	- If model lighting/shading looks off, use the Flip Vertex Normals option
		
- It is advised to turn off the Convert Triangle Strips option on import for models that have been exported using this toolkit, so as not to double convert an already-ready Triangle List

Reasoning:
- Blender doesn't use Triangle Strips, which is the Primitive Type used in almost all the game's original models for face polygons, so they need to be converted to normal Triangle List for Blender to consume.
  - However, the default export setting in this addon is to use Triangle List, which luckily the game can accept to consume if a certain field in the data is tweaked to a value of 4.
	


# Credits: 
- kirbystealer for `get_string_lookup.py` and `stringtable_pcapk.zip`

Join the [Web of Shadows](https://discord.gg/NftyUNJw) discord server for any questions
