import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import collectShortformFolders, pullShortformContent, _decodeDBData
from flask_app.utils.database import database

db = database()

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
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"
    sorting = form_fields['sorting'].strip().lower()
    videosFirst = form_fields['videosFirst'] == "true"

    content = pullShortformContent(name, displayed, resetFile, sorting, videosFirst)

    return json.dumps(content)


# Handles displaying of single shortform content
@app.route('/viewShortformContent/<name>/<content_id>')
@login_required
def singleShortformContent(name, content_id):
    name = " ".join(name.split("__"))
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

    success_data = {'message': f"Currently viewing {name} content", 
                    'alt': f"Image from {name}",
                    'href': "/viewShortformContent", 'button-text': "View More Images", 'loop': True}
    
    return render_template('displayReturnedContent.html', img_data=[img_data], success=success_data)