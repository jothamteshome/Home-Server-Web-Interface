import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectPremadeMemeAuthors, pullPremadeMemes, _hideFilename

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
                    'href': "/viewPremadeMemes", 'button-text': "View More Memes", 'loop': True}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)