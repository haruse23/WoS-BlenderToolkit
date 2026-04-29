This toolkit is a Blender addon/plugin for the video game Spider-Man: Web of Shadows

This addon is designed on Blender 4.5.0 mainly, then compatibility has been tested and confirmed for Blender 5.0.0
and it could very possibly work on other untested versions of Blender, especially 4.1+

### [Download WoS BlenderToolkit](https://github.com/haruse23/WoS-BlenderToolkit/releases/latest)

<img width="1920" height="1039" alt="4" src="https://github.com/user-attachments/assets/4652d35c-c55d-4286-9c84-b79e2e0124e0" />

# Features:
- Import/Export the game's model format (.wrap.mesh) to/from Blender (drag-and-drop supported for import)

- Import/Export the game's skeleton format (.wrap.skel) to Blender (drag-and-drop supported for import)

- Convert the game's texture format (.wrap.tex) to DDS and vice versa (drag-and-drop feature)

Use latest version of kirbystealer's [WebOfShadowsTools](https://github.com/kirbystealer/WebOfShadowsTools) or Devryx's [Toolkit](https://github.com/Devryx505/web-of-shadows-tools-wos-tools-) to extract said files

- The addon presents an extra feature which you can find in the side-panel. Press N to open Blender's side-panel, then go to the WOS Tools tab, there you can find the Rename Vertex Groups Utility.
	- Use this utility to rename a model's vertex groups from the "bone_{index}" naming to the real bone names imported with the skeleton (Armature needs to be in same collection or the utility will raise an error)

- The addon also presents some options on importing/exporting model format, which are:
	- Flip UV V-Axis
	- Reverse Triangle Winding Order
	- Convert to Triangle List

- Supported pixel formats: DXT1, DXT3, DXT5, D3DFMT_A8R8G8B8, D3DFMT_X8R8G8B8, D3DFMT_L8

# Tutorials:
[Porting Batman to Web of Shadows Part I](https://youtu.be/P3-AcD7pwpQ?si=igozY6xRtYtuqvfQ)
   
[Porting Batman to Web of Shadows Part II](https://youtu.be/4fldUmAR0pw?si=WAuIYQT_cietPRa5)

# Notes:
- Safe max vertex groups count for each submesh is 48, otherwise the mesh deformation might look off

- For custom model ports, rename your materials to the name of any material file the original model uses, full name could work but preferred to only take the hash part, like: `0x9E8F3E7F`

- It is advised to use Data Transfer modifier to transfer weights from original models to modded ones, use Replace as Mix Mode and a Mapping of Nearest Vertex

- Each submesh needs a vertex color attribute of some value, use Face Corner and Byte Color when creating the attribute, then make it White if you want fully opaque vertex color
	- If you don't set a vertex color, the model will look complete black in-game
	
- All submeshes under a single collection need to be parented to the armature so that weights can be exported correctly

- To convert to the game's texture files you need a DDS file to drag and drop into Blender's 3D Viewport
  - If you don't have your image file ready in the DDS format, then you can use this [SimpleTextureConverter](https://www.nexusmods.com/site/mods/1539) tool to convert back-and-forth between a lot of image formats including DDS

- It is advised to turn off the Convert to Triangle List option on import for models that have been exported using this toolkit, so as not to double convert an already-ready Triangle List

Reasoning:
- Blender doesn't use Triangle Strips, which is the Primitive Type used in almost all the game's original models for face polygons, so they need to be converted to normal Triangle List for Blender to consume.
  - However, the default export setting in this addon is to use Triangle List, which luckily the game can accept to consume if a certain field in the data is tweaked to a value of 4.

- Apply scale to the model before exporting, toolkit handles applying the rest of tranforms
	
#
📦 Recommended Model Import Settings
- ✔ Flip UV V-Axis
- ✔ Reverse Triangle Winding Order
- ✔ Convert to Triangle List (only if the model comes from the game directly, not exported through the addon)

📤 Recommended Model Export Settings
- ✔ Flip UV V-Axis
- ✔ Reverse Triangle Winding Order
#


# Credits: 
- kirbystealer for `get_string_lookup.py` and `stringtable_pcapk.zip`
- All the amazing Blender addons made for video-games, that I learned through reading them a lot, along with everybody who helped in my coding/reverse engineering journey so far, on Discord especially. Special mention: NSACloud's [RE Mesh Editor](https://github.com/NSACloud/RE-Mesh-Editor/)
  
Join the [Web of Shadows](https://discord.gg/NftyUNJw) discord server for any questions

# Changelog
### 1.0.2
- Fixed issues with TBN (Tangent, Bitangent, Normal) calculation and export from Blender
- Fixed issues with axis orientation and handedness
- Fixed issues with UVs after export from Blender
- Better model import speed
- Fixed issues with static model export related to the WRAPSectionPatchTable, that caused problems with static model mods
- Fixed issues with formatting hex numbers (pcapkFilenameHash) into strings, that caused key errors when fetching bone names for some skeletons.
	- Now should be correctly something like: "0x05102987" instead of "0x5102987"
- Rewrote some parts of the code cleanlier, and now supposedly all game meshes should be supported for import into Blender

### 1.0.1
- Minor changes and fixes

### 1.0.0
- Release
