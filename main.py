import os
import json
import pathlib
import shutil
import zipfile

with open("data.json") as file:
    data = json.load(file)

for folder in data["folders"]:
    sourceIsNotEmpty = folder["source"] != ""
    targetIsNotEmpty = folder["target"] != ""
    sourceExists = os.path.exists(folder["source"])
    targetExists = os.path.exists(folder["target"])

    if sourceIsNotEmpty and targetIsNotEmpty and sourceExists and targetExists:
        targetName = pathlib.PurePosixPath(folder["source"]).stem
        targetDir = folder["target"] + targetName

        shutil.make_archive(targetDir, "zip", folder["source"])
        with zipfile.ZipFile(targetDir + ".zip", "a", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("source_" + targetName + ".txt", folder["source"])
