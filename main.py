from os.path import isfile, exists, join, abspath, dirname
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
    log_file.write(message)


def create_archive(alt_src=None):
    global log_message

    if alt_src is None:
        src = source

    else:
        src = alt_src

    time_start = time()
    make_archive(target_full_path, "zip", src)
    with ZipFile(target_full_path_with_ext, "a", compression=ZIP_DEFLATED) as archive:
        archive.writestr("source_" + target_name + ".txt", source)
    time_end = time()

    log_message = (
            datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
            f"BACKUP of {source} " +
            f"CREATED as {target_file_name_with_ext} " +
            f"in {floor(time_end - time_start)} seconds" +
            "\n"
    )
    log(log_message)


def create_tracking_file():
    global log_message, file

    tracking_file = (
        target +
        "." +
        source.replace("/", "%").replace("\\", "%") +
        ".txt"
    )
    if not isfile(tracking_file):
        with open(tracking_file, "w") as file:
            file.write(target_file_name_with_ext)

            log_message = (
                    datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                    f"CREATED new tracking file for {source}" +
                    "\n"
            )
            log(log_message)

    else:
        with open(tracking_file, "r+") as file:
            tracked_backups = file.read().splitlines()
            tracked_backups.insert(0, target_file_name_with_ext)

            if len(tracked_backups) > backup_count:
                file_to_delete = tracked_backups[-1]
                del tracked_backups[-1]
                Path(target + file_to_delete).unlink()

                log_message = (
                        datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                        f"DELETED old backup {file_to_delete} of {source}" +
                        "\n"
                )
                log(log_message)

            file.seek(0)
            file.write("\n".join(tracked_backups))


def try_fallback():
    global log_message

    try:
        copytree(source, target_full_path_temp, dirs_exist_ok=True)

    except shutilError:
        log_message = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: Some files could not be copied" +
                "\n"
        )
        log(log_message)

    try:
        log_message = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: Creating archive from {target_full_path_temp}" +
                "\n"
        )
        log(log_message)

        create_archive(target_full_path_temp)
        create_tracking_file()
        # Delete temp files
        rmtree(target_full_path_temp)

        log_message = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: SUCCESSFUL for {target_full_path_temp}" +
                "\n"
        )
        log(log_message)

    except PermissionError:
        log_message = (
                datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                f"FALLBACK: FAILED for {target_full_path_temp}" +
                "\n"
        )
        log(log_message)

        # Delete failed zip
        Path(target_full_path_with_ext).unlink()
        # Delete temp files
        rmtree(target_full_path_temp)


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
backup_count = 4
data_file = join(abspath(dirname(__file__)), "data.json")

with open(data_file) as file:
    data = load(file)

for backup_dir in data["folder"]:
    source_is_not_empty = backup_dir["source"] != ""
    target_is_not_empty = backup_dir["target"] != ""
    source_exists = exists(backup_dir["source"])
    target_exists = exists(backup_dir["target"])

    if source_is_not_empty and target_is_not_empty and source_exists and target_exists:
        # Add trailing slash to path if it does not exist
        source = join(backup_dir["source"], "")
        target = join(backup_dir["target"], "")

        target_name = PurePosixPath(source).stem
        target_file_name = target_name + "_" + datetime.today().strftime("(%Y-%m-%d %H:%M:%S.%f)")
        target_file_name_with_ext = target_file_name + ".zip"
        target_full_path = target + target_file_name
        target_full_path_with_ext = target_full_path + ".zip"
        target_full_path_temp = target + "temp/" + target_file_name

        log_file = target + ".log.txt"
        with open(log_file, "a") as log_file:
            try:
                create_archive()
                create_tracking_file()
                archive_failed = False

            except PermissionError:
                log_message = (
                        datetime.today().strftime("%Y-%m-%d %H:%M:%S - ") +
                        f"Permission DENIED for {source}, FALLING BACK to copying files" +
                        "\n"
                )
                log(log_message)

                # Delete failed zip
                Path(target_full_path_with_ext).unlink()
                archive_failed = True

            if archive_failed:
                try_fallback()
