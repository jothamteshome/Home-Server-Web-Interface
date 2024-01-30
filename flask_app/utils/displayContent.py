import shutil
import base64
import random
import json
import os
import re
import time

from functools import cmp_to_key
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, current_app as app, _showDataFile
from flask_app.utils.globalUtils import _tempDirectory, _tryListDir, _dataBatchesFile, _tryRemoveFile, winsort

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
    if sorting == "author":
        return dict(sorted(fileDict.items(), key=lambda x: x[1]['author']))
    elif sorting == "author-reverse":
        return dict(sorted(fileDict.items(), key=lambda x: x[1]['author'], reverse=True))
    elif sorting == "z-a":
        return dict(sorted(fileDict.items(), key=cmp_to_key(lambda x, y: winsort()(x[0], y[0])), reverse=True))
    else:
        return dict(sorted(fileDict.items(), key=cmp_to_key(lambda x, y: winsort()(x[0], y[0]))))


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
                    subgenre_comics.append({'name': file, 'data': json.dumps({'name': file, 'optionPath': f"{search_dir['main-dir']}{subgenre}\\{file}"})})

            comicData.extend(sorted(subgenre_comics, key=lambda x: x['name']))
    
                
    return comicData


def collectComics(directory, sorting):
    comicContents = {'name': directory.split("\\")[-1], 'data': {}}

    for comic in os.listdir(directory):
        dirContents = list(os.walk(f"{directory}\\{comic}"))[0]

        match = re.search("\[(.*?)\]", comic)
        author = ""
        
        if match:
            author = comic[match.start():match.end()]

        title = comic.replace(f"{author}", "").strip()

        if dirContents[1] or dirContents[2]:
            comicContents['data'][title] = {'name': title, 'loc': dirContents[0], 'series': len(dirContents[1]) > 0, 'author': author}

    comicContents['data'] = _sortComics(comicContents['data'], sorting)

    return comicContents


def collectComicSeries(name, directory):
    comicSeriesContents = {'data': {}}

    for comic in os.listdir(directory):
        dirContents = list(os.walk(f"{directory}\\{comic}"))[0]

        match = re.search("\[(.*?)\]", comic)
        author = ""
        
        if match:
            author = comic[match.start():match.end()]

        title = comic.replace(f"{author}", "").strip()

        if dirContents[2]:
            comicSeriesContents['data'][comic] = {'name': name, 'loc': dirContents[0], 'author': author, 'title': title}

    comicSeriesContents['name'] = name
    comicSeriesContents['data'] = _sortComics(comicSeriesContents['data'], None)

    return comicSeriesContents


####################################################################
#                   SHOW CONTENT HANDLING                          #
####################################################################

def _writeShowDataToJSON(showData):
    with open(_showDataFile(), 'w') as jsonFile:
        json.dump({'show-data': showData}, jsonFile)


def _loadShowData():
    with open(_showDataFile(), 'r') as jsonFile:
        showData = json.load(jsonFile)['show-data']

        return showData

# List stored shows and movies
def _listShows():
    # If time since last show data update is less than 30 minutes and show data json file exists, load previous data
    # otherwise perform os walk for updated data
    if (time.perf_counter() - app.showDataRefresh) < 1800 \
        and _showDataFile(name_only=True) in _tryListDir(_showDataFile(dir_only=True)) and not app.showsStartup:

        return _loadShowData()
    
    app.showDataRefresh = time.perf_counter()
    data = _openJSONDirectoriesFile()

    showData = []

    for search_dir in data['retrieve-show-content-dirs']['search-directories']:
        search_dir_name = search_dir.split("\\")[-1]
        showData.append({"name": f"--- {search_dir_name} ---", 'disabled': True})
        search_valid = []
        shows = []

        for movie_directory in _tryListDir(search_dir):
            movie_dir_path = f"{search_dir}\\{movie_directory}"
            if "Movie Content" in _tryListDir(movie_dir_path):
                shows.append(f"{movie_dir_path}\\Movie Content")

        for show_dir in shows:
            show = show_dir.replace("\\Movie Content", "").split("\\")[-1]
            search_valid.append({'name': show, 'data': json.dumps({'name': show, 'show-dir-path': show_dir})})
        
        showData.extend(sorted(search_valid, key=lambda x: x['name']))

    showData.append({'name': "--- Extra Content ---", 'disabled': True})

    for show_dir in data['retrieve-show-content-dirs']['extra-directories']:
        show = show_dir.split("\\")[-1]
        showData.append({'name': show, 'data': json.dumps({'name': show, 'show-dir-path': show_dir})})

    _writeShowDataToJSON(showData)
    app.showsStartup = False

    return showData


# Collect valid show names and directories
def _collectShowContent(directory):
    valid_contents = []
    for content in _tryListDir(directory):
        show_name = content.replace(".mp4", "")

        if ".mp4" in content:
            valid_contents.append((show_name, f"{directory}\\{content}"))

    return valid_contents


def _listThumbnails(thumbnailDir):
    thumbnails = _tryListDir(thumbnailDir)

    thumbnailDict = {}

    for thumbnail in thumbnails:
        thumbName = thumbnail.split(".")[0]

        thumbnailDict[thumbName] = f"{thumbnailDir}\\{thumbnail}"

    return thumbnailDict


def _getThumbnail(thumbnails, showTitle):
    if showTitle in thumbnails:
        return thumbnails[showTitle]
    else:
        return None


# Retrieves show content for listing purposes
def retreiveShowContent(name, show_dir_path, sorting):
    data = _openJSONDirectoriesFile()
    SHOW_SUBDIRS = data['retrieve-show-content-dirs']['show-subdirs']

    content = []

    if name in SHOW_SUBDIRS:
        subdirNames = SHOW_SUBDIRS[name]

        for subdir in subdirNames:
            full_dir = f"{show_dir_path}{subdir}"
            content.extend(_collectShowContent(full_dir))

    content.extend(_collectShowContent(show_dir_path))

    thumbnails = _listThumbnails(f"{show_dir_path}\\Thumbnails")
    
    content = _sortStyle(content, sorting)
    dir_name = show_dir_path.replace("\\Movie Content", "").split("\\")[-1]

    returnableContent = {}
    tempThumbnails = []
    for show in content:
        if " - " in show[0]:
            title = show[0].split(" - ")
            name = " - ".join(title[1:])
            title = title[0]
            thumbnail = _getThumbnail(thumbnails, title)

            if thumbnail:
                tempThumbnails.append((f"{show[0]}.jpg", thumbnail))

        else:
            title = ""
            name = show[0]
            thumbnail = None

        returnableContent[show[0]] = {'name': name, 'title': title, 'loc': show[1], 'dirName': dir_name, 'thumbnail': thumbnail,
                                      'tempDir': f"{_tempDirectory(True)}"}

    _copyFilesToTemp(tempThumbnails)

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