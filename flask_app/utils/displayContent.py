import shutil
import base64
import random
import json
import os
import re
import time

from functools import cmp_to_key
from flask_app.utils.database import database
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, current_app as app
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


# Hides a filename behind base64 encoding scheme
def _hideFilename(filename, decode=False):
    if decode:
        return base64.urlsafe_b64decode(filename).decode()

    return base64.urlsafe_b64encode(filename.encode()).decode()


def _distributeBatches(filenames):
    data_batches = {}

    batch_num = -BATCHED_SEND_COUNT

    databaseUpdate = []

    for i, file_data in enumerate(filenames):
        prev_id, next_id = filenames[i-1][2], filenames[(i+1) % len(filenames)][2]
        if i % BATCHED_SEND_COUNT == 0:
            batch_num += BATCHED_SEND_COUNT
            data_batches[batch_num] = []

        data_batches[batch_num].append(file_data)
        databaseUpdate.append([prev_id, next_id, file_data[2]])

    data_batches[batch_num].append(('CONTENT_END', "CONTENT_END", 'CONTENT_END', 'CONTENT_END'))

    with open(_dataBatchesFile(), 'w') as jsonFile:
        json.dump(data_batches, jsonFile)


    db.updateShortContent(['prev_content_id', 'next_content_id'], databaseUpdate)


def _loadBatchFromJSON(displayed):
    with open(_dataBatchesFile(), "r") as jsonFile:
        data = json.load(jsonFile)
        return data[str(displayed)]


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

        filename_dict[file[2]] = {'file': f"{_tempDirectory(True)}/{file[0]}", 'type': file[3], 'alt': altText}

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


def _handleDisplayingComic(comic_id):
    comicData = db.getComic(comic_id)
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

    comicData = db.getDecodedData('comicData', 'comic_franchise=%s AND comic_series=%s', [franchise_name.strip(), ""])

    for row in comicData:
        id = row['comic_id']
        name = row['comic_name']
        author = row['comic_author']
        series = row['has_chapters']
        title = name.replace(f"{author}", "").strip()

        comicContents['data'][title] = {'id': id, 'name': title, 'author': author, 'has_chapters': series}

    comicContents['data'] = _sortComics(comicContents['data'], sorting)

    return comicContents


def collectComicSeries(seriesData):
    comicSeriesContents = {'data': {}}

    for row in seriesData:
        id = row['comic_id']
        name = row['comic_name']
        author = row['comic_author']

    
        comicSeriesContents['data'][name] = {'id': id, 'name': name, 'author': author}

    comicSeriesContents['name'] = row['comic_series'].replace(author, "").strip()
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
    
    showData = db.getDecodedData("showData", "show_name=%s", [name])

    for row in showData:
        id = row['show_id']
        name = row['show_episode']
        title = row['show_ep_num']
        loc = row['show_loc']
        thumb_loc = row['show_thumb']

        content.append((name, loc, id, title, thumb_loc))

    content = _sortStyle(content, sorting)

    returnableContent = {}

    for show in content:
        show_split = show[0].split(" - ")
        name = " - ".join(show_split[1:]) if show[3] else show[0]
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

    SEARCH_DIRS = db.query("SELECT search_dir_name FROM shortContentData WHERE content_style=%s GROUP BY search_dir_name ORDER BY search_dir_name", ['Shortform Content'])
    SEARCH_DIRS = [search_dir['search_dir_name'].decode('utf-8') for search_dir in SEARCH_DIRS]

    validNames = []

    for directory in SEARCH_DIRS:
        validNames.append({'name': f"--- {directory} ---", 'disabled': True})

        names = db.query("SELECT source_dir_name FROM shortContentData WHERE content_style=%s AND search_dir_name=%s GROUP BY source_dir_name", ['Shortform Content', directory])
        names = [name['source_dir_name'].decode('utf-8') for name in names]

        formatted_data = []

        for name in names:
            formatted_data.append({'name': name, 'data': json.dumps({'name': "__".join(name.split(" "))})})

        validNames.extend(sorted(formatted_data, key=lambda x: x['name'].lower()))

    return validNames


# Pull all shortform content from selected folder name
def pullShortformContent(source_name, displayed, resetFile, sorting, videosFirst):
    source_name = " ".join(source_name.split("__"))

    content = {'image': db.getDecodedData("shortContentData", "content_style=%s AND source_dir_name=%s AND content_type='image'", ['Shortform Content', source_name]),
               'video': db.getDecodedData("shortContentData", "content_style=%s AND source_dir_name=%s AND content_type='video'", ['Shortform Content', source_name])}

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    if videosFirst:
        content = dict(sorted(content.items(), reverse=True))

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        filenames = []

        for content_type in content:
            shortformContentData = content[content_type]

            content_type_data = []

            for row in shortformContentData:
                id = row['content_id']
                name = row['content_name']
                type = row['content_type']
                loc = row['content_loc']

                content_type_data.append((name, loc, id, type))
            
            filenames.extend(_sortStyle(content_type_data, sorting))

        
        if sorting == "shuffle":
            filenames = _sortStyle(filenames, sorting)


        _distributeBatches(filenames)

    return _handleBatch(_loadBatchFromJSON(displayed), f'Image/Video from {source_name}')


####################################################################
#                   PREMADE MEME HANDLING                          #
####################################################################


# Collect all valid folders with premade memes
def collectPremadeMemeAuthors():
    validNames = []

    SEARCH_DIRS = db.query("SELECT search_dir_name FROM shortContentData WHERE content_style=%s GROUP BY search_dir_name ORDER BY search_dir_name DESC", ['Premade Meme'])
    SEARCH_DIRS = [search_dir['search_dir_name'].decode('utf-8') for search_dir in SEARCH_DIRS]

    for directory in SEARCH_DIRS:
        validNames.append({'name': f"--- {directory} ---", 'disabled': True})

        names = db.query("SELECT source_dir_name FROM shortContentData WHERE content_style=%s AND search_dir_name=%s GROUP BY source_dir_name", ['Premade Meme', directory])
        names = [name['source_dir_name'].decode('utf-8') for name in names]

        formatted_data = []

        for name in names:
            formatted_data.append({'name': name, 'data': json.dumps({'name': "__".join(name.split(" "))})})

        validNames.extend(sorted(formatted_data, key=lambda x: x['name'].lower()))

    return validNames


# Pull premade meme data from long storage and move to temp directory
def pullPremadeMemes(source_name, displayed, resetFile, sorting):
    source_name = " ".join(source_name.split("__"))

    premadeMemeData = db.getDecodedData("shortContentData", "content_style=%s AND source_dir_name=%s", ['Premade Meme', source_name])

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        content = []

        for row in premadeMemeData:
            id = row['content_id']
            name = row['content_name']
            type = row['content_type']
            loc = row['content_loc']

            content.append((name, loc, id, type))
        
        content = _sortStyle(content, sorting)

        _distributeBatches(content)
    
    return _handleBatch(_loadBatchFromJSON(displayed), f"Image/Video by {source_name}")


####################################################################
#                   FINALIZED MEME HANDLING                        #
####################################################################


# Retrieves data of finalized memes that exist
def retreiveFinalizedMemes():
    return [{'name': "Finalized Memes", 'data': json.dumps({'name': "Finalized Memes"})}]


# Handles collection of finalized memes
def collectFinalizedMemes(displayed, resetFile, sorting):
    finalizedMemeData = db.getDecodedData("shortContentData", "content_style=%s", ['Finalized Meme'])

    if resetFile:
        _tryRemoveFile(_dataBatchesFile())

    if _dataBatchesFile(name_only=True) not in _tryListDir(_dataBatchesFile(dir_only=True)):
        filenames = []

        for row in finalizedMemeData:
            id = row['content_id']
            name = row['content_name']
            type = row['content_type']
            loc = row['content_loc']

            filenames.append((name, loc, id, type))
        
        filenames = _sortStyle(filenames, sorting)


        _distributeBatches(filenames)

    return _handleBatch(_loadBatchFromJSON(displayed), "Finalized meme image")