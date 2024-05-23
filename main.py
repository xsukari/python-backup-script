from os import path
from json import load
from pathlib import PurePosixPath, Path
from shutil import make_archive
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime

with open("data.json") as file:
    data = load(file)

for backupDir in data["folder"]:
    sourceIsNotEmpty = backupDir["source"] != ""
    targetIsNotEmpty = backupDir["target"] != ""
    sourceExists = path.exists(backupDir["source"])
    targetExists = path.exists(backupDir["target"])

    if sourceIsNotEmpty and targetIsNotEmpty and sourceExists and targetExists:
        targetName = PurePosixPath(backupDir["source"]).stem
        targetFileName = targetName + "_" + datetime.today().strftime("(%Y-%m-%d %H:%M:%S.%f)")
        targetFileNameWithExt = targetFileName + ".zip"
        targetFullPath = backupDir["target"] + targetFileName
        targetFullPathWithExt = targetFullPath + ".zip"

        # Create backup archive
        make_archive(targetFullPath, "zip", backupDir["source"])
        with ZipFile(targetFullPathWithExt, "a", compression=ZIP_DEFLATED) as archive:
            archive.writestr("source_" + targetName + ".txt", backupDir["source"])

        # Create tracking file for the backups
        trackingFile = backupDir["target"] + "." + backupDir["source"].replace("/", "%").replace("\\", "%") + ".txt"
        if not path.isfile(trackingFile):
            with open(trackingFile, "w") as file:
                file.write(targetFileNameWithExt)
        else:
            with open(trackingFile, "r+") as file:
                trackedBackups = file.read().splitlines()
                trackedBackups.insert(0, targetFileNameWithExt)
                if len(trackedBackups) > 5:
                    fileToDelete = trackedBackups[-1]
                    del trackedBackups[-1]
                    Path(backupDir["target"] + fileToDelete).unlink()
                file.seek(0)
                file.write("\n".join(trackedBackups))
