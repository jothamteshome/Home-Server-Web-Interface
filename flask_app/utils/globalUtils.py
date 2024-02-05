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


def _collectShowContent(directory):
    valid_contents = []
    for content in _tryListDir(directory):
        show_name = content.replace(".mp4", "")

        if content.split('.')[-1] == "mp4":
            valid_contents.append((show_name, f"{directory}\\{content}"))

    return valid_contents


def _listShowThumbnails(thumbnail_dir):
    thumbnails = _tryListDir(thumbnail_dir)
    thumbnailDict = {}

    for thumbnail in thumbnails:
        thumbName = thumbnail.split(".")[0]

        thumbnailDict[thumbName] = f"{thumbnail_dir}\\{thumbnail}"

    return thumbnailDict


def _addShowsToDatabase():
    data = _openJSONDirectoriesFile()

    db_entries = {entry['show_loc'].decode('utf-8') for entry in db.query("SELECT show_loc FROM showData")}

    SHOW_SUBDIRS = data['retrieve-show-content-dirs']['show-subdirs']

    for search_dir in data['retrieve-show-content-dirs']['search-directories']:
        for show_dir in _tryListDir(search_dir):
            show_dir_path = f"{search_dir}\\{show_dir}\\Movie Content"

            if _tryListDir(show_dir_path):
                
                show_contents = []
                thumbnails = _listShowThumbnails(f"{show_dir_path}\\Thumbnails")

                show_contents.extend(_collectShowContent(show_dir_path))

                if show_dir in SHOW_SUBDIRS:
                    for subdir in SHOW_SUBDIRS[show_dir]:
                        subdir_path = f"{show_dir_path}{subdir}"
                        show_contents.extend(_collectShowContent(subdir_path))

                for show in show_contents:
                    show_name_split = show[0].split(" - ")
                    title = ""

                    if len(show_name_split) > 1:
                        title = show_name_split[0].strip()

                    thumbnail = thumbnails.get(title, "")

                    db.storeShow(show_id=hash(show[1]), show_episode=show[0], show_name=show_dir, show_ep_num=title,
                                 show_search_dir=search_dir.split("\\")[-1], show_thumb=thumbnail, show_loc=show[1])
                    
                    db_entries.discard(show[1])
                    

    for show_dir_path in data['retrieve-show-content-dirs']['extra-directories']:
        show_contents = []

        show_contents.extend(_collectShowContent(show_dir_path))

        for show in show_contents:
            show_name_split = show[0].split(" - ")

            title = ""

            if len(show_name_split) > 1:
                title = show_name_split[0].strip()

            db.storeShow(show_id=hash(show[1]), show_episode=show[0], show_name=show_dir_path.split("\\")[-1], show_ep_num=title,
                        show_search_dir="Extra Content", show_thumb="", show_loc=show[1])
            
            db_entries.discard(show[1])

        for entry in db_entries:
            db.query('DELETE FROM showData WHERE show_loc=%s', [entry])
