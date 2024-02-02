import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import collectShortformFolders, pullShortformContent,_hideFilename

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
                    'href': "/viewShortformContent", 'button-text': "View More Images", 'loop': True}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)