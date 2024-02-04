import shutil
import base64
import random
import json
import os
import re
import time

from functools import cmp_to_key
from flask_app.utils.database import database
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, current_app as app, _showDataFile
from flask_app.utils.globalUtils import _tempDirectory, _tryListDir, _dataBatchesFile, _tryRemoveFile, winsort
db = database()

BATCHED_SEND_COUNT = 16

####################################################################
#                  GENERAL PURPOSE FUNCTIONS                       #
####################################################################


# Copy a file from it's source directory to user's temp directory
def _copyFilesToTemp(filenames, subdir=""):
    if subdir:
        os.makedirs(f"{_tempDirectory()}\\{subdir}", exist_ok=True)

    for file in filenames:
        if file[0] in _tryListDir(_tempDirectory()) or file[0] == "CONTENT_END":
            continue

        source = open(file[1], 'rb')

        destPath = f"{_tempDirectory()}"

        if subdir:
            destPath = f"{destPath}\\{subdir}"

        dest = open(f"{destPath}\\{file[0]}", "wb")

        shutil.copyfileobj(source, dest)

        source.close()
        dest.close()


# Removes url-unsafe characters
def _urlsafe(filename):    
    filename = filename.replace("#", "")
    return filename


# Hides a filename behind base64 encoding scheme
def _hideFilename(filename, decode=False):
    if decode:
        return base64.urlsafe_b64decode(filename).decode()

    return base64.urlsafe_b64encode(filename.encode()).decode()


# Validates if content should be displayed
def _validContent(contentName):
    VALID_EXTENSIONS = {'mp4', 'mov', 'jpg', 'jpeg', 'png', 'gif'}

    ext = contentName.split(".")[-1].lower()

    if ext in VALID_EXTENSIONS:
        return True
    
    return False


def _distributeBatches(filenames, directory):
    data_batches = {'directory': directory, 'batches': {}}

    batch_num = -BATCHED_SEND_COUNT

    for i, file_data in enumerate(filenames):
        if i % BATCHED_SEND_COUNT == 0:
            batch_num += BATCHED_SEND_COUNT
            data_batches['batches'][batch_num] = []

        data_batches['batches'][batch_num].append(file_data)

    data_batches['batches'][batch_num].append(('CONTENT_END', "CONTENT_END", 'CONTENT_END'))

    with open(_dataBatchesFile(), 'w') as jsonFile:
        json.dump(data_batches, jsonFile)


def _loadBatchFromJSON(displayed):
    with open(_dataBatchesFile(), "r") as jsonFile:
        data = json.load(jsonFile)
        return data['directory'], data['batches'][str(displayed)]


# Handles the shuffling of data in a way that batched returns
# will continue to function normally   
def _sortStyle(filenames, sorting):
    if sorting == "shuffle":
        random.shuffle(filenames)
    elif sorting == "newest":
        filenames.sort(key=lambda x: os.path.getctime(x[1]), reverse=True)
    elif sorting == "oldest":
        filenames.sort(key=lambda x: os.path.getctime(x[1]))
    elif sorting == "z-a":
        filenames.sort(key=cmp_to_key(lambda x, y: winsort()(x[0], y[0])), reverse=True)
    else:
        filenames.sort(key=cmp_to_key(lambda x, y: winsort()(x[0], y[0])))
    
    return filenames
    

def _handleBatch(file_data, altText):
    _copyFilesToTemp(file_data)
    filename_dict = {}

    contentEnd = False

    for file in file_data:
        if file[0] == "CONTENT_END":
            contentEnd = True
            continue

        filename_dict[_hideFilename(file[0])] = {'file': f"{_tempDirectory(True)}/{file[0]}", 'type': file[2], 'alt': altText}

    if contentEnd:
        filename_dict['CONTENT_END'] = {"file": 'CONTENT_END', 'type': "CONTENT_END", 'alt': 'CONTENT_END'}

    return filename_dict


####################################################################
#                   COMIC BOOK HANDLING                            #
####################################################################


def _sortComics(fileDict, sorting):
    tempAuthorSort = dict(sorted(fileDict.items(), key=lambda x: x[1]['author']))
    tempTitleSort = dict(sorted(fileDict.items(), key=cmp_to_key(lambda x, y: winsort()(x[0], y[0]))))

    if sorting == "author":
        return dict(sorted(tempTitleSort.items(), key=lambda x: x[1]['author']))
    elif sorting == "author-reverse":
        return dict(sorted(tempTitleSort.items(), key=lambda x: x[1]['author'], reverse=True))
    elif sorting == "z-a":
        return dict(sorted(tempAuthorSort.items(), key=cmp_to_key(lambda x, y: winsort()(x[0], y[0])), reverse=True))
    else:
        return dict(sorted(tempAuthorSort.items(), key=cmp_to_key(lambda x, y: winsort()(x[0], y[0]))))

def _decodeDBData(data):
    convertFunc = {'comic_id': str, 'show_id': str, 'has_chapters': int}

    for column in data:
        data[column] = data[column].decode('utf-8') if column not in convertFunc else convertFunc[column](data[column])

    return data


def _handleDisplayingComic(comic_id):
    comicData = _decodeDBData(db.getComic(comic_id))
    comic = []

    loc = comicData['comic_loc']

    for page in os.listdir(loc):
        comic.append((page, f"{loc}\\{page}"))

    _copyFilesToTemp(comic, comic_id)

    return comicData


def _listComicNames():
    data = _openJSONDirectoriesFile()
    comicData = []

    for search_dir in data['retrieve-comic-content-dirs']['search-directories']:
        for subgenre in search_dir['sub-genres']:
            subOption = subgenre.replace("\\", "")
            subOption = f"----- {subOption} -----"
            comicData.append({'name': subOption, 'optionPath': f"{search_dir['main-dir']}{subgenre}", 'disabled': True})

            subgenre_comics = []
            for file in os.listdir(f"{search_dir['main-dir']}{subgenre}"):
                if os.listdir(f"{search_dir['main-dir']}{subgenre}\\{file}"):
                    subgenre_comics.append({'name': file, 'data': json.dumps({'name': "__".join(file.split(" ")), 'optionPath': f"{search_dir['main-dir']}{subgenre}\\{file}"})})

            comicData.extend(sorted(subgenre_comics, key=lambda x: x['name']))
    
                
    return comicData


def collectComics(franchise_name, sorting):
    comicContents = {'name': franchise_name.strip(), 'data': {}}

    comicData = db.query('SELECT * FROM comicData WHERE comic_franchise=%s AND comic_series=%s', [franchise_name.strip(), ""])

    for i, row in enumerate(comicData):
        comicData[i] = _decodeDBData(row)

        id = row['comic_id']
        name = comicData[i]['comic_name']
        author = comicData[i]['comic_author']
        series = comicData[i]['has_chapters']
        title = name.replace(f"{author}", "").strip()

        comicContents['data'][title] = {'id': id, 'name': title, 'author': author, 'has_chapters': series}

    comicContents['data'] = _sortComics(comicContents['data'], sorting)

    return comicContents


def collectComicSeries(seriesData):
    comicSeriesContents = {'data': {}}

    for i, row in enumerate(seriesData):
        seriesData[i] = _decodeDBData(row)

        id = row['comic_id']
        name = seriesData[i]['comic_name']
        author = seriesData[i]['comic_author']

    
        comicSeriesContents['data'][name] = {'id': id, 'name': name, 'author': author}

    comicSeriesContents['name'] = seriesData[i]['comic_series'].replace(author, "").strip()
    comicSeriesContents['data'] = _sortComics(comicSeriesContents['data'], None)

    return comicSeriesContents


####################################################################
#                   SHOW CONTENT HANDLING                          #
####################################################################

# List stored shows and movies
def _listShows():
    showOptions = {entry['show_search_dir'].decode('utf-8') for entry in db.query("SELECT show_search_dir FROM showData")}
    showOptions.discard('Extra Content')
    showOptions = list(showOptions)
    showOptions.sort()
    showOptions.append("Extra Content")

    showData = []

    for search_dir in showOptions:
        showData.append({"name": f"--- {search_dir} ---", 'disabled': True})

        shows = []

        showNames = {entry['show_name'].decode('utf-8') 
                     for entry in db.query("SELECT show_name FROM showData WHERE show_search_dir=%s", [search_dir])}

        for show in showNames:
            shows.append({'name': show, 'data': json.dumps({'name': "__".join(show.split(" "))})})

        showData.extend(sorted(shows, key=lambda x: x['name']))

    return showData


# Retrieves show content for listing purposes
def retreiveShowContent(name, sorting):
    content = []
    thumbnails = []
    
    showData = db.query("SELECT * FROM showData WHERE show_name=%s", [name])

    for i, row in enumerate(showData):
        showData[i] = _decodeDBData(row)

        id = showData[i]['show_id']
        name = showData[i]['show_episode']
        title = showData[i]['show_ep_num']
        loc = showData[i]['show_loc']
        thumb_loc = showData[i]['show_thumb']

        content.append((name, loc, id, title, thumb_loc))

    content = _sortStyle(content, sorting)

    returnableContent = {}

    for show in content:
        name = " - ".join(show[0].split(" - ")[1:])
        thumbnail = f"{_tempDirectory(True)}/{show[0]}.jpg" if show[4] else None

        if show[4]:
            thumbnails.append((f"{show[0]}.jpg", show[4]))

        returnableContent[show[0]] = {'id': show[2], 'name': name, 'title': show[3], 'thumbnail': thumbnail}

    _copyFilesToTemp(thumbnails)

    return returnableContent


####################################################################
#                   SHORTFORM CONTENT HANDLING                     #
####################################################################


# List the names of folders containing short form content
def _listNames(directory):
    names = _tryListDir(directory)

    validNames = []

    for name in names:
        # Directory for folder name
        name_dir = f"{directory}/{name}"

        # If search Uploaded Content subdirectory if it exists
        if "Uploaded Content" in _tryListDir(name_dir):
            name_dir = f"{name_dir}/Uploaded Content"

        name_dir_content = _tryListDir(name_dir)

        if "Images" in name_dir_content and "Videos" in name_dir_content:
            validNames.append({'name': name, 'data': json.dumps({'name': name, 'source_dir': name_dir})})
        
    return validNames


# Collect all valid folders with short-form content
def collectShortformFolders():
    SEARCH_DIRS = _openJSONDirectoriesFile()['short-form-search-dirs']

    validNames = []

    for directory in SEARCH_DIRS:
        dir_name = directory.split("\\")[-1]
        validNames.append({'name': f"--- {dir_name} --- ", 'disabled': True})
        validNames.extend(sorted(_listNames(directory), key=lambda x: x['name']))

    return validNames


# Pull all shortform content from selected folder name
def pullShortformContent(name, directory, displayed, resetFile, sorting, videosFirst):
    VIDEO_EXTENSIONS = {'mp4', 'mov'}

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    SUBDIRS = ["\\Images", "\\Scraped Content", "\\Videos"]

    if videosFirst:
        SUBDIRS.reverse()

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        filenames = []

        for subdir in SUBDIRS:
            subdir_files = []
            for content in _tryListDir(f"{directory}{subdir}"):
                ext = content.split(".")[-1].lower()

                if _validContent(content):
                    subdir_files.append((_urlsafe(content), f"{directory}{subdir}\\{content}", 
                                    "image" if ext not in VIDEO_EXTENSIONS else "video"))
                    
            filenames.extend(_sortStyle(subdir_files, sorting))

        if sorting == "shuffle":
            filenames = _sortStyle(filenames, sorting)

        _distributeBatches(filenames, directory)

    return _handleBatch(_loadBatchFromJSON(displayed)[1], f'Image/Video from {name}')


####################################################################
#                   PREMADE MEME HANDLING                          #
####################################################################


# Collect all valid folders with premade memes
def collectPremadeMemeAuthors():
    SEARCH_DIRS = _openJSONDirectoriesFile()['conditionally-included-routes']['premade-memes-dirs']
    validNames = []

    for directory in SEARCH_DIRS:
        source_dir = directory.split("\\")[-1]
        source_dir = f"--- {source_dir} ---"
        validNames.append({'name': source_dir, 'disabled': True})

        names = _tryListDir(directory)

        directory_valid = []

        for name in names:
            directory_valid.append({'name': name, 'data': json.dumps({'name': name, 'source_dir': f"{directory}\\{name}"})})
        
        validNames.extend(sorted(directory_valid, key=lambda x: x['name'].lower()))

    return validNames


# Pull premade meme data from long storage and move to temp directory
def pullPremadeMemes(name, directory, displayed, resetFile, sorting):
    VIDEO_EXTENSIONS = {'mp4', 'mov'}

    premadeMemeSubdirs = _openJSONDirectoriesFile()['conditionally-included-routes']['premade-memes-subdirs']

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        filenames = []

        for subdir in premadeMemeSubdirs:
            subdir_files = []
            for content in _tryListDir(f"{directory}{subdir}"):
                ext = content.split(".")[-1].lower()

                if _validContent(content):
                    subdir_files.append((_urlsafe(content), f"{directory}{subdir}\\{content}", 
                                    "image" if ext not in VIDEO_EXTENSIONS else "video"))
                    
            filenames.extend(_sortStyle(subdir_files, sorting))

        _distributeBatches(filenames, directory)

        if sorting == "shuffle":
            filenames = _sortStyle(filenames, sorting)
        
    return _handleBatch(_loadBatchFromJSON(displayed)[1], f'Image/Video by {name}')


####################################################################
#                   FINALIZED MEME HANDLING                        #
####################################################################


# Retrieves data of finalized memes that exist
def retreiveFinalizedMemes():
    IMG_DIR = _openJSONDirectoriesFile()['conditionally-included-routes']['finalized-memes-dirs']['image-directory']

    return [{'name': "Finalized Memes", 'data': json.dumps({'name': "Finalized Memes", 'source_dir': IMG_DIR})}]


# Handles collection of finalized memes
def collectFinalizedMemes(displayed, resetFile, sorting):
    IMG_DIR = _openJSONDirectoriesFile()['conditionally-included-routes']['finalized-memes-dirs']['image-directory']

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        filenames = []
        for content in _tryListDir(IMG_DIR):
            filenames.append((content, f"{IMG_DIR}\\{content}", 'image'))

        filenames = _sortStyle(filenames, sorting)

        _distributeBatches(filenames, IMG_DIR)

    return _handleBatch(_loadBatchFromJSON(displayed)[1], "Finalized meme image")