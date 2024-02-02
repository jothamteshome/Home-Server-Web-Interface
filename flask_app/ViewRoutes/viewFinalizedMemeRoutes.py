import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.createdMemeHandling import _retreiveMemeCaptions
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectFinalizedMemes, retreiveFinalizedMemes, _hideFilename

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