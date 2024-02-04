import json
import os
import re

from ctypes import wintypes, windll
from flask import session, current_app
from flask_app.utils.database import database
db = database()

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


def _showDataFile(name_only=False, dir_only=False):
    filename = "show_data.json"

    directory = f"flask_app\\utils\\HelperFiles"

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


def _addComicsToDatabase():
    data = _openJSONDirectoriesFile()

    db_entries = {entry['comic_loc'].decode('utf-8') for entry in db.query("SELECT comic_loc FROM comicData")}

    for search_dir in data['retrieve-comic-content-dirs']['search-directories']:
        for subgenre in search_dir['sub-genres']:
            subgenre_dir = f"{search_dir['main-dir']}{subgenre}"

            for franchise in _tryListDir(subgenre_dir):
                franchise_dir = f"{subgenre_dir}\\{franchise}"

                for comic in _tryListDir(franchise_dir):
                    comic_loc = f"{franchise_dir}\\{comic}"
                    dirContents = list(os.walk(comic_loc))[0]

                    if not dirContents[1] and not dirContents[2]:
                        continue

                    match = re.search("\[(.*?)\]", comic)
                    author = ""
                    
                    if match:
                        author = comic[match.start():match.end()]

                    has_chapters = 0
                    if len(dirContents[1]) > 0:
                        has_chapters = 1
                        for comic_part in dirContents[1]:
                            comic_part_loc = f"{dirContents[0]}\\{comic_part}"
                            db.storeComic(comic_id=hash(comic_part_loc), comic_name=comic_part, comic_franchise=franchise, 
                                          comic_series=comic, comic_author=author, comic_loc=comic_part_loc, has_chapters=0)
                            
                            db_entries.discard(comic_part_loc)
                            
                    db.storeComic(comic_id=hash(comic_loc), comic_name=comic, comic_franchise=franchise, 
                                      comic_author=author, comic_loc=comic_loc, has_chapters=has_chapters)
                    
                    db_entries.discard(comic_loc)

    for entry in db_entries:
        db.query('DELETE FROM comicData WHERE comic_loc=%s', [entry])