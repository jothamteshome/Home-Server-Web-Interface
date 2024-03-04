import json
import os
import re

from flask_app.utils.database import database
from flask_app.utils.globalUtils import _tryListDir, _openJSONDirectoriesFile

db = database()


####################################################################
#                  GENERAL PURPOSE FUNCTIONS                       #
####################################################################
# Validates if content should be displayed
def _validContent(contentName):
    VALID_EXTENSIONS = {'mp4', 'mov', 'jpg', 'jpeg', 'png', 'gif'}

    ext = contentName.split(".")[-1].lower()

    if ext in VALID_EXTENSIONS:
        return True
    
    return False


def _checkCaptionExistence(directory, content_name):
    caption_dir = _tryListDir(f"{directory}\\Captions")

    split_name = content_name.split(".")
    name, ext = ".".join(split_name[:-1]), split_name[-1].lower()

    caption_name = f"{name}_{ext}.txt"

    if not caption_dir or caption_name not in caption_dir:
        return False
    
    return f"{directory}\\Captions\\{caption_name}"


####################################################################
#                   COMIC BOOK HANDLING                            #
####################################################################    
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


####################################################################
#                   SHOW CONTENT HANDLING                          #
####################################################################
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

                add_to_database = []

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

                    add_to_database.append((hash(show[1]), show[0], show_dir, title, search_dir.split("\\")[-1], thumbnail, show[1]))
                    
                    db_entries.discard(show[1])

                db.storeShow(add_to_database)
                    

    for show_dir_path in data['retrieve-show-content-dirs']['extra-directories']:
        show_contents = []

        show_contents.extend(_collectShowContent(show_dir_path))

        add_to_database = []

        for show in show_contents:
            show_name_split = show[0].split(" - ")

            title = ""

            if len(show_name_split) > 1:
                title = show_name_split[0].strip()


            add_to_database.append((hash(show[1]), show[0], show_dir_path.split("\\")[-1], title, "Extra Content", "", show[1]))
            
            db_entries.discard(show[1])

        db.storeShow(add_to_database)

    for entry in db_entries:
        db.query('DELETE FROM showData WHERE show_loc=%s', [entry])


####################################################################
#                   SHORTFORM CONTENT HANDLING                     #
####################################################################
def _addShortformContentToDatabase():
    data = _openJSONDirectoriesFile()

    VIDEO_EXTENSIONS = {'mp4', 'mov'}

    db_entries = {entry['content_loc'].decode('utf-8') for entry in db.query("SELECT content_loc FROM shortContentData WHERE content_style=%s", ['Shortform Content'])}

    SEARCH_DIRS = data['short-form-search-dirs']

    for search_dir in SEARCH_DIRS:
        search_dir_name = search_dir.split("\\")[-1]

        content_directories = _tryListDir(search_dir)

        for content_dir in content_directories:
            content_dir_name = content_dir.split("\\")[-1]
            content_dir_path = f"{search_dir}\\{content_dir}"

            if "Uploaded Content" in _tryListDir(content_dir_path):
                content_dir_path = f"{content_dir_path}\\Uploaded Content"

            add_to_database = []

            for subdir in ["\\Images", "\\Scraped Content", "\\Videos"]:
                subdir_path = f"{content_dir_path}{subdir}"

                for content in _tryListDir(subdir_path):
                    ext = content.split(".")[-1].lower()

                    if _validContent(content):
                        content_path = f"{subdir_path}\\{content}"

                        content_type = "image" if ext not in VIDEO_EXTENSIONS else "video"

                        caption_loc = _checkCaptionExistence(content_dir_path, content)

                        has_caption = 0 if not caption_loc else 1

                        if not has_caption:
                            caption_loc = ""

                        add_to_database.append((hash(content_path), content, content_type, content_path, search_dir_name, content_dir_name, 'Shortform Content', has_caption, caption_loc, "", ""))

                        db_entries.discard(content_path)

            db.storeShortContent(add_to_database)


    for entry in db_entries:
        db.query('DELETE FROM shortContentData WHERE content_loc=%s', [entry])


####################################################################
#                   PREMADE MEME HANDLING                          #
####################################################################
def _addPremadeMemesToDatabase():
    data = _openJSONDirectoriesFile()

    VIDEO_EXTENSIONS = {'mp4', 'mov'}

    db_entries = {entry['content_loc'].decode('utf-8') for entry in db.query("SELECT content_loc FROM shortContentData WHERE content_style=%s", ['Premade Meme'])}

    SEARCH_DIRS = data['conditionally-included-routes']['premade-memes-dirs']

    for search_dir in SEARCH_DIRS:
        search_dir_name = search_dir.split("\\")[-1]
        
        content_directories = _tryListDir(search_dir)

        for content_dir in content_directories:
            content_dir_name = content_dir.split("\\")[-1]
            content_dir_path = f"{search_dir}\\{content_dir}"

            add_to_database = []

            for subdir in data['conditionally-included-routes']['premade-memes-subdirs']:
                subdir_path = f"{content_dir_path}{subdir}"

                for content in _tryListDir(subdir_path):
                    ext = content.split(".")[-1].lower()

                    if _validContent(content):
                        content_path = f"{subdir_path}\\{content}"
                        
                        content_type = "image" if ext not in VIDEO_EXTENSIONS else "video"

                        caption_loc = _checkCaptionExistence(content_dir_path, content)

                        has_caption = 0 if not caption_loc else 1

                        if not has_caption:
                            caption_loc = ""
                        
                        add_to_database.append((hash(content_path), content, content_type, content_path, search_dir_name, content_dir_name, 'Premade Meme', has_caption, caption_loc, "", ""))

                        db_entries.discard(content_path)

            db.storeShortContent(add_to_database)

    for entry in db_entries:
        db.query('DELETE FROM shortContentData WHERE content_loc=%s', [entry])


####################################################################
#                   FINALIZED MEME HANDLING                        #
####################################################################
def _addFinalizedMemesToDatabase():
    data = _openJSONDirectoriesFile()

    db_entries = {entry['content_loc'].decode('utf-8') for entry in db.query("SELECT content_loc FROM shortContentData WHERE content_style=%s", ['Finalized Meme'])}

    VIDEO_EXTENSIONS = {'mp4', 'mov'}

    content_dir = data['conditionally-included-routes']['finalized-memes-dir']
    content_dir_name = content_dir.split("\\")[-1]

    add_to_database = []

    for subdir in data['conditionally-included-routes']['finalized-memes-subdirs']:
        subdir_path = f"{content_dir}{subdir}"

        for content in _tryListDir(subdir_path):
            ext = content.split(".")[-1].lower()

            if _validContent(content):
                content_path = f"{subdir_path}\\{content}"
                
                content_type = "image" if ext not in VIDEO_EXTENSIONS else "video"

                caption_loc = _checkCaptionExistence(content_dir, content)

                has_caption = 0 if not caption_loc else 1

                if not has_caption:
                    caption_loc = ""

                add_to_database.append((hash(content_path), content, content_type, content_path, 'Finalized Meme', content_dir_name, 'Finalized Meme', has_caption, caption_loc, "", ""))
                
                db_entries.discard(content_path)

    db.storeShortContent(add_to_database)

    for entry in db_entries:
        db.query('DELETE FROM shortContentData WHERE content_loc=%s', [entry])


def _addAllShortContentToDatabase():
    _addShortformContentToDatabase()
    _addFinalizedMemesToDatabase()
    _addPremadeMemesToDatabase()