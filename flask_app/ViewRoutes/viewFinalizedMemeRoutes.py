import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.createdMemeHandling import _retreiveMemeCaptions
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectFinalizedMemes, retreiveFinalizedMemes, _decodeDBData
from flask_app.utils.database import database

db = database()

# Displays route to show finalized memes template
@app.route('/viewFinalizedMemes')
@login_required
@clear_temp
def viewFinalizedMemes():
    return cond_render_template('viewContent/viewFinalizedMemes.html', contentList=retreiveFinalizedMemes(), 
                                cond_statement="finalized-memes-dir" in _openJSONDirectoriesFile()['conditionally-included-routes'])


# Returns finalized meme image data
@app.route('/processFinalizedMemes', methods=["POST"])
@login_required
def processFinalizedMemes():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"

    return json.dumps(collectFinalizedMemes(displayed, resetFile, 'shuffle'))


# Returns data from temp directory for singular finalized meme
@app.route('/viewFinalizedMemes/<accessType>/<content_id>')
@login_required
def singleFinalizedMeme(accessType, content_id):
    contentData = _decodeDBData(db.getShortContent(content_id))

    img_data = {'name': contentData['content_name'], 'data': {'file': f"{_tempDirectory(True)}/{contentData['content_name']}", 'type': contentData['content_type']}}

    if contentData['has_caption']:
        caption_loc = contentData['caption_loc']

        captions = []

        with open(caption_loc, "r") as captionFile:
            for line in captionFile:
                line = line.strip()
                captions.append("\n\n".join(line.split("***")))

        img_data['data']['captions'] = captions


    content_hash = contentData['content_name'].split('.')[0]

    success_data = {'message': f"Currently viewing captions for {content_hash}", 
                    'alt': f"Meme with finalized caption",
                    'href': "/viewFinalizedMemes", 'button-text': "View More Memes"}
    
    if accessType == "Uploaded":
        success_data['href'] = "/uploadFinalizedMeme"
        success_data['button-text'] = "Upload Another Meme"
    
    return render_template('displayReturnedContent.html', img_data=[img_data], success=success_data)