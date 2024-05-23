from os import path
from json import load
from pathlib import PurePosixPath, Path
from shutil import make_archive
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from time import time
from math import floor
from argparse import ArgumentParser

backupCount = 4

parser = ArgumentParser(description="Python backup script")
parser.add_argument("-v", "--verbose", action="store_true", required=False, help="Enable output to console with -v")
args = parser.parse_args()
verbose = args.verbose

with open("data.json") as file:
    data = load(file)

for backupDir in data["folder"]:
    sourceIsNotEmpty = backupDir["source"] != ""
    targetIsNotEmpty = backupDir["target"] != ""
    sourceExists = path.exists(backupDir["source"])
    targetExists = path.exists(backupDir["target"])

    if sourceIsNotEmpty and targetIsNotEmpty and sourceExists and targetExists:
        logFile = backupDir["target"] + ".log.txt"

        with open(logFile, "a") as logFile:
            try:
                targetName = PurePosixPath(backupDir["source"]).stem
                targetFileName = targetName + "_" + datetime.today().strftime("(%Y-%m-%d %H:%M:%S.%f)")
                targetFileNameWithExt = targetFileName + ".zip"
                targetFullPath = backupDir["target"] + targetFileName
                targetFullPathWithExt = targetFullPath + ".zip"

                # Create backup archive
                timeStart = time()
                make_archive(targetFullPath, "zip", backupDir["source"])
                with ZipFile(targetFullPathWithExt, "a", compression=ZIP_DEFLATED) as archive:
                    archive.writestr("source_" + targetName + ".txt", backupDir["source"])
                timeEnd = time()
                logMessage = (
                    datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                    f"Backup of {backupDir['source']} " +
                    f"created as {targetFileNameWithExt} " +
                    f"in {floor(timeEnd - timeStart)} seconds" +
                    "\n"
                )
                if verbose:
                    print(logMessage)
                logFile.write(logMessage)

                # Create tracking file for the backups
                trackingFile = (
                    backupDir["target"] +
                    "." +
                    backupDir["source"].replace("/", "%").replace("\\", "%") +
                    ".txt"
                )
                if not path.isfile(trackingFile):
                    with open(trackingFile, "w") as file:
                        file.write(targetFileNameWithExt)
                        logMessage = (
                            datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                            f"Created new tracking file for {backupDir['source']}" +
                            "\n"
                        )
                        if verbose:
                            print(logMessage)
                        logFile.write(logMessage)

                else:
                    with open(trackingFile, "r+") as file:
                        trackedBackups = file.read().splitlines()
                        trackedBackups.insert(0, targetFileNameWithExt)
                        if len(trackedBackups) > backupCount:
                            fileToDelete = trackedBackups[-1]
                            del trackedBackups[-1]
                            Path(backupDir["target"] + fileToDelete).unlink()
                            logMessage = (
                                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                                f"Deleted old backup {fileToDelete} of {backupDir['source']}" +
                                "\n"
                            )
                            if verbose:
                                print(logMessage)
                            logFile.write(logMessage)
                        file.seek(0)
                        file.write("\n".join(trackedBackups))

            except PermissionError:
                logMessage = (
                    datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                    f"Permission denied for {backupDir['source']}, skipping" +
                    "\n"
                )
                if verbose:
                    print(logMessage)
                logFile.write(logMessage)
