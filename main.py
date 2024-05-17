import json
import distutils.dir_util  # needs setuptools package
import os
import pathlib

with open("data.json") as file:
    data = json.load(file)

for folder in data["folders"]:
    originIsNotEmpty = folder["origin"] != ""
    targetIsNotEmpty = folder["target"] != ""
    originExists = os.path.exists(folder["origin"])
    targetExists = os.path.exists(folder["target"])
    if originIsNotEmpty and targetIsNotEmpty and originExists and targetExists:
        targetName = pathlib.PurePosixPath(folder["origin"]).stem
        distutils.dir_util.copy_tree(folder["origin"], folder["target"] + targetName)
        print(f"Copied contents of {folder["origin"]} to {folder["target"] + targetName}")

# To-do: add "temp" to dest directory, zip all files in temp when all folders have been processed, delete temp files
# or maybe just add the source files straight to the zip if possible, idk
