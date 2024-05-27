from os import path
from json import load
from pathlib import PurePosixPath, Path
from shutil import make_archive, copytree, rmtree, Error as shutilError
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from time import time
from math import floor
from argparse import ArgumentParser

def log(message):
    if verbose:
        print(message)
    logFile.write(message)


def createArchive(altSrc = None):
    global logMessage

    if altSrc is None:
        src = backupDir["source"]

    else:
        src = altSrc

    timeStart = time()
    make_archive(targetFullPath, "zip", src)
    with ZipFile(targetFullPathWithExt, "a", compression=ZIP_DEFLATED) as archive:
        archive.writestr("source_" + targetName + ".txt", backupDir["source"])
    timeEnd = time()

    logMessage = (
            datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
            f"BACKUP of {backupDir['source']} " +
            f"CREATED as {targetFileNameWithExt} " +
            f"in {floor(timeEnd - timeStart)} seconds" +
            "\n"
    )
    log(logMessage)


def createTrackingFile():
    global logMessage, file

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
                    f"CREATED new tracking file for {backupDir['source']}" +
                    "\n"
            )
            log(logMessage)

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
                        f"DELETED old backup {fileToDelete} of {backupDir['source']}" +
                        "\n"
                )
                log(logMessage)

            file.seek(0)
            file.write("\n".join(trackedBackups))


def tryFallback():
    global logMessage

    try:
        copytree(backupDir["source"], targetFullPathTemp, dirs_exist_ok=True)

    except shutilError:
        logMessage = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: some files could not be copied" +
                "\n"
        )
        log(logMessage)

    try:
        logMessage = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: Creating archive from {targetFullPathTemp}" +
                "\n"
        )
        log(logMessage)

        createArchive(targetFullPathTemp)
        createTrackingFile()
        # Delete temp files
        rmtree(targetFullPathTemp)

        logMessage = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: SUCCESSFUL for {targetFullPathTemp}" +
                "\n"
        )
        log(logMessage)

    except PermissionError:
        logMessage = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: FAILED for {targetFullPathTemp}" +
                "\n"
        )
        log(logMessage)

        # Delete failed zip
        Path(targetFullPathWithExt).unlink()
        # Delete temp files
        rmtree(targetFullPathTemp)


# Script start
parser = ArgumentParser(description="Python backup script")
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    required=False,
    help="Enable output to console with -v"
)
args = parser.parse_args()

verbose = args.verbose
backupCount = 4

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
        targetFullPathTemp = backupDir["target"] + "temp/" + targetFileName

        logFile = backupDir["target"] + ".log.txt"
        with open(logFile, "a") as logFile:
            try:
                createArchive()
                createTrackingFile()

            except PermissionError:
                logMessage = (
                        datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                        f"Permission DENIED for {backupDir['source']}, FALLING BACK to copying files" +
                        "\n"
                )
                log(logMessage)

                # Delete failed zip
                Path(targetFullPathWithExt).unlink()
                zipFailed = True

            if zipFailed:
                tryFallback()
