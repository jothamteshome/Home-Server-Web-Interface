import json
import os
import re

from ctypes import wintypes, windll
from flask import session, current_app

# Opens json file containing directories
def _openJSONDirectoriesFile():
    with open("flask_app/utils/HelperFiles/importantDirectories.json", "r") as jsonFile:
        data = json.load(jsonFile)

    return data

# Delete temp directory content
def _deleteTempDirectory():
    try:
        for directory in os.walk(_tempDirectory(), topdown=False):
            for file in directory[2]:
                os.remove(f'{directory[0]}\\{file}')

            os.rmdir(directory[0])
    except (OSError, PermissionError):
        pass


def _deleteUserDataBatches():
    try:
        for file in _tryListDir("flask_app/static/UserDataBatches"):
            os.remove(f"flask_app/static/UserDataBatches/{file}")
    except (OSError, PermissionError):
        pass


def _deleteAllTempDirectores():
    static_dir = "flask_app/static"

    try:
        for directory in _tryListDir(static_dir):
            if os.path.isdir(f"{static_dir}/{directory}") and "Temp-" in directory:
                for subdir in os.walk(f"{static_dir}/{directory}", topdown=False):
                    for file in subdir[2]:
                        os.remove(f"{subdir[0]}\\{file}")
                    
                    os.rmdir(subdir[0])

    except (OSError, PermissionError):
        pass


# Get user's temp directory
def _tempDirectory(folder_only=False):
    tempFolder = f"Temp-{session['user_info']['username']}"
    tempDir = f"flask_app\\static\\{tempFolder}"
    os.makedirs(tempDir, exist_ok=True)

    if folder_only:
        return tempFolder
    
    return tempDir


# Get user's data batch directory
def _dataBatchesFile(name_only=False, dir_only=False):
    filename = f"{_tempDirectory(True)}-data_batches.json"

    directory = f"flask_app\\static\\UserDataBatches"

    fullPath = f"{directory}\\{filename}"

    if name_only and not dir_only:
        return filename
    elif dir_only and not name_only:
        return directory
    
    return fullPath


def _tryRemoveFile(filepath):
    try:
        os.remove(filepath)
    except (FileNotFoundError, KeyError):
        pass


# Try to list the elements of a directory
# return empty list if directory does not exist
def _tryListDir(dir):
    try:
        return os.listdir(dir)
    except (FileNotFoundError, NotADirectoryError):
        return []
    

def winsort():
    _StrCmpLogicalW = windll.Shlwapi.StrCmpLogicalW
    _StrCmpLogicalW.argtypes = [wintypes.LPWSTR, wintypes.LPWSTR]
    _StrCmpLogicalW.restype = wintypes.INT

    return _StrCmpLogicalW
