import json
import base64
import os

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.createdMemeHandling import _retreiveMemeCaptions
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectShortformFolders, collectFinalizedMemes, collectPremadeMemeAuthors, retreiveFinalizedMemes
from flask_app.utils.displayContent import pullShortformContent, pullPremadeMemes, retreiveShowContent, collectComics, collectComicSeries
from flask_app.utils.displayContent import _copyFilesToTemp, _listShows, _hideFilename, _listComicNames
from flask_app.utils.database  import database
db = database()

####################################################################
#                   GENERAL USE VIEW ROUTES                        #
####################################################################

@app.route('/storeReturnData', methods=['POST'])
def storeReturnData():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    search_name = form_fields['search_name'].encode('utf-8')
    item_name = form_fields['item_name'].encode('utf-8')
    item_loc = form_fields['item_loc'].encode('utf-8')
    item_route = form_fields['processURL'].encode('utf-8')
    item_dir = form_fields['item_dir'].encode('utf-8')

    db.storeReturnData(search_name, item_name, item_loc, item_route, item_dir)

    return json.dumps({'success': 1})


@app.route('/getReturnData', methods=['POST'])
def getReturnData():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    search_name = form_fields['search_name']

    returned = db.getReturnData(search_name)[0]
    for row in returned:
        returned[row] = returned[row].decode('utf-8')

    return json.dumps(returned)


####################################################################
#                   COMIC BOOK HANDLING                            #
####################################################################


@app.route('/viewComics')
@login_required
@clear_temp
def viewComics():
    return render_template('viewContent/viewComics.html', contentList=_listComicNames())


@app.route('/processComics', methods=['POST'])
@login_required
def processComics():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    optionPath = form_fields['optionPath']
    sorting = form_fields['sorting'].strip().lower()

    content = collectComics(optionPath, sorting)
    return json.dumps(content)


@app.route('/processComicSeries', methods=['POST'])
@login_required
def processComicSeries():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    loc = form_fields['loc']

    content = collectComicSeries(name, loc)
    return json.dumps(content)


@app.route('/downloadComic', methods=['POST'])
@login_required
def downloadComic():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    subdir = form_fields['name']
    loc = form_fields['loc']

    comic = []

    for page in os.listdir(loc):
        comic.append((page, f"{loc}\\{page}"))

    _copyFilesToTemp(comic, subdir)

    return json.dumps({})


@app.route('/viewComics/<comicName>')
@login_required
def displayComics(comicName):
    img_data = []

    for file in os.listdir(f"{_tempDirectory()}\\{comicName}"):
        img_data.append({'name': file, 'data': {'file': f"{_tempDirectory(True)}/{comicName}/{file}", 'type': 'image'}})

    comicName = " ".join(comicName.split("_")).title()

    success_data = {'message': f"Currently viewing: {comicName}", 
                    'alt': f"{comicName} comic page",
                    'href': "/viewComics", 'button-text': "View More Comics"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)




####################################################################
#                   SHOW CONTENT HANDLING                          #
####################################################################


# Displays template for viewing longform movie/show content
@app.route('/viewShows')
@login_required
@clear_temp
def viewShows():
    return render_template('viewContent/viewShows.html', contentList=_listShows())


# Processes the passing of data for the listing of show names
@app.route('/processShows', methods=['POST'])
@login_required
def processShows():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    sorting = form_fields['sorting'].strip().lower()

    content = retreiveShowContent(name, sorting)
    return json.dumps(content)


# Handles the downloading of content to temp directory after show selection is made
@app.route('/downloadTempShowContent', methods=['POST'])
@login_required
@clear_temp
def downloadTempShowContent():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name, source = form_fields['name'], form_fields['loc']

    _copyFilesToTemp([(f"{name}.mp4", source)])

    return json.dumps({})


# Processes the displaying of singular show video from temp directory
@app.route('/viewShows/<showName>/<contentName>')
@login_required
def streamShows(showName, contentName):
    contentName = base64.urlsafe_b64decode(contentName).decode('utf-8')
    img_data = [{'name': contentName, 'data': {'file': f"{_tempDirectory(True)}/{contentName}.mp4", 'type': 'video'}}]

    success_data = {'message': f"Currently viewing {showName} content", 
                    'alt': f"Image from {showName}",
                    'href': "/viewShows", 'button-text': "View More Shows"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)


####################################################################
#                   SHORTFORM CONTENT HANDLING                     #
####################################################################

# Displays the template for viewing shortform content
@app.route('/viewShortformContent')
@login_required
@clear_temp
def viewShortformContent():
    return render_template('viewContent/viewShortformContent.html', contentList=collectShortformFolders())


# Processes selection data and returns images
@app.route('/processViewShortform', methods=['POST'])
@login_required
def processViewShortform():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    directory = form_fields['source_dir']
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"
    sorting = form_fields['sorting'].strip().lower()
    videosFirst = form_fields['videosFirst'] == "true"

    content = pullShortformContent(name, directory, displayed, resetFile, sorting, videosFirst)

    return json.dumps(content)


# Handles displaying of single shortform content
@app.route('/viewShortformContent/<name>/<contentName>')
@login_required
def singleShortformContent(name, contentName):
    contentName = _hideFilename(contentName, decode=True)
    ext = contentName.split(".")[-1].lower()
    IMG_EXT = {'jpg', 'jpeg', 'gif', 'png'}
    img_data = [{'name': contentName, 'data': {'file': f"{_tempDirectory(True)}/{contentName}", 'type': 'image' if ext in IMG_EXT else 'video'}}]

    success_data = {'message': f"Currently viewing {name} content", 
                    'alt': f"Image from {name}",
                    'href': "/viewShortformContent", 'button-text': "View More Images"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)


####################################################################
#                   PREMADE MEME HANDLING                          #
####################################################################

# Displays template for premade memes
@app.route('/viewPremadeMemes')
@login_required
@clear_temp
def viewPremadeMemes():
    return cond_render_template('viewContent/viewPremadeMemes.html', contentList=collectPremadeMemeAuthors(), 
                                cond_statement="premade-memes-dirs" in _openJSONDirectoriesFile()['conditionally-included-routes'])


# Handles processing and returning of premade memes
@app.route('/processPremadeMemes', methods=['POST'])
@login_required
def processPremadeMemes():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    directory = form_fields['source_dir']
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"
    sorting = form_fields['sorting'].strip().lower()

    content = pullPremadeMemes(name, directory, displayed, resetFile, sorting)

    return json.dumps(content)


# Handles processing and displaying of single premade meme
@app.route('/viewPremadeMemes/<name>/<contentName>')
@login_required
def singlePremadeMeme(name, contentName):
    contentName = _hideFilename(contentName, decode=True)
    ext = contentName.split(".")[-1].lower()
    IMG_EXT = {'jpg', 'jpeg', 'gif', 'png'}
    img_data = [{'name': contentName, 'data': {'file': f"{_tempDirectory(True)}/{contentName}", 'type': 'image' if ext in IMG_EXT else 'video'}}]

    success_data = {'message': f"Currently viewing {name} content", 
                    'alt': f"Meme by {name}",
                    'href': "/viewPremadeMemes", 'button-text': "View More Memes"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)


####################################################################
#                   FINALIZED MEME HANDLING                        #
####################################################################

# Displays route to show finalized memes template
@app.route('/viewFinalizedMemes')
@login_required
@clear_temp
def viewFinalizedMemes():
    return cond_render_template('viewContent/viewFinalizedMemes.html', contentList=retreiveFinalizedMemes(), 
                                cond_statement="finalized-memes-dirs" in _openJSONDirectoriesFile()['conditionally-included-routes'])


# Returns finalized meme image data
@app.route('/processFinalizedMemes', methods=["POST"])
@login_required
def processFinalizedMemes():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"

    return json.dumps(collectFinalizedMemes(displayed, resetFile, 'shuffle'))


# Returns data from temp directory for singular finalized meme
@app.route('/viewFinalizedMemes/<accessType>/<contentName>')
@login_required
def singleFinalizedMeme(accessType, contentName):
    contentName = _hideFilename(contentName, decode=True)
    content_hash = contentName.split('.')[0]

    captions = _retreiveMemeCaptions(content_hash, existingOnly=True)

    img_data = [{'name': contentName, 'data': {'file': f"{_tempDirectory(True)}/{contentName}", 'type': 'image', 'captions': captions}}]

    success_data = {'message': f"Currently viewing captions for {content_hash}", 
                    'alt': f"Meme with finalized caption",
                    'href': "/viewFinalizedMemes", 'button-text': "View More Memes"}
    
    if accessType == "Uploaded":
        success_data['href'] = "/uploadFinalizedMeme"
        success_data['button-text'] = "Upload Another Meme"
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)