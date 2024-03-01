import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectPremadeMemeAuthors, pullPremadeMemes, _decodeDBData, _copyFilesToTemp
from flask_app.utils.database import database

db = database()

# Displays template for premade memes
@app.route('/viewPremadeMemes')
@login_required
@clear_temp
def viewPremadeMemes():
    return cond_render_template('viewContent/viewPremadeMemes.html', contentList=collectPremadeMemeAuthors(), 
                                cond_statement="premade-memes-dirs" in _openJSONDirectoriesFile()['conditionally-included-routes'])


# Handles processing and displaying of single premade meme
@app.route('/viewPremadeMemes/<name>/<content_id>')
@login_required
def singlePremadeMeme(name, content_id):
    split_name = " ".join(name.split("__"))
    contentData = _decodeDBData(db.getShortContent(content_id))

    _copyFilesToTemp([[contentData['content_name'], contentData['content_loc']]])

    img_data = {'name': contentData['content_name'], 'data': {'file': f"{_tempDirectory(True)}/{contentData['content_name']}", 'type': contentData['content_type'], 'prev_id': contentData['prev_content_id'], 'next_id': contentData['next_content_id']}}

    if contentData['has_caption']:
        caption_loc = contentData['caption_loc']

        captions = []

        with open(caption_loc, "r") as captionFile:
            for line in captionFile:
                line = line.strip()
                captions.append("\n\n".join(line.split("***")))

        img_data['data']['captions'] = captions

    success_data = {'message': f"Currently viewing {split_name} content", 
                    'alt': f"Meme by {split_name}",
                    'href': "/viewPremadeMemes", 'button-text': "View More Memes", 'loop': True, 'link_href': f"/viewPremadeMemes/{name}"}
    
    return render_template('displayReturnedContent.html', img_data=[img_data], success=success_data)


@app.route('/premadeMemeData/<name>/<content_type_first>/<sorting>', methods=['POST'])
@login_required
def getPremadeData(name, content_type_first, sorting):
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    displayed = int(form_fields['displayed'])
    sorting = sorting.lower()
    resetFile = form_fields['resetFile'] == "true"
    
    content = pullPremadeMemes(name, displayed, resetFile, sorting)
    route = {'link_href': f"/viewPremadeMemes/{name}", 'repeat': "/viewPremadeMemes", 'repeatMessage': 'View More Memes'}

    return json.dumps({'data': content, 'route': route})


@app.route('/viewPremadeMemes/Gallery/<name>/<sorting>')
@login_required
def viewPremadeGallery(name, sorting):
    return render_template('viewContent/viewContentGallery.html')

@app.route('/viewPremadeMemes/Gallery/<name>')
@login_required
def viewPremadeGalleryDefault(name):
    return render_template('viewContent/viewContentGallery.html')
