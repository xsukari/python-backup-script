import os
import json
import pathlib
import shutil

import distutils.dir_util  # needs setuptools package

with open("data.json") as file:
    data = json.load(file)

for folder in data["folders"]:
    originIsNotEmpty = folder["origin"] != ""
    targetIsNotEmpty = folder["target"] != ""
    originExists = os.path.exists(folder["origin"])
    targetExists = os.path.exists(folder["target"])

    if originIsNotEmpty and targetIsNotEmpty and originExists and targetExists:
        targetName = pathlib.PurePosixPath(folder["origin"]).stem
        tempTargetDir = folder["target"] + "temp/" + targetName
        targetDir = folder["target"] + targetName

        distutils.dir_util.copy_tree(folder["origin"], tempTargetDir)
        with open(tempTargetDir + "/origin_" + targetName + ".txt", "w") as file:
            file.write(folder["origin"])
        shutil.make_archive(targetDir, 'zip', tempTargetDir)
        shutil.rmtree(tempTargetDir)
