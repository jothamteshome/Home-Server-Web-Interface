import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import collectShortformFolders, pullShortformContent, _copyFilesToTemp
from flask_app.utils.database import database

db = database()

# Displays the template for viewing shortform content
@app.route('/viewShortformContent')
@login_required
@clear_temp
def viewShortformContent():
    return render_template('viewContent/viewShortformContent.html', contentList=collectShortformFolders())


# Handles displaying of single shortform content
@app.route('/viewShortformContent/<name>/<content_id>')
@login_required
def singleShortformContent(name, content_id):
    split_name = " ".join(name.split("__"))
    contentData = db.getShortContent(content_id)

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
                    'alt': f"Image from {split_name}",
                    'href': "/viewShortformContent", 'button-text': "View More Images", 'loop': True, 'link_href': f"/viewShortformContent/{name}"}
    
    return render_template('displayReturnedContent.html', img_data=[img_data], success=success_data)


@app.route('/shortformData/<name>/<content_type_first>/<sorting>', methods=['POST'])
@login_required
def getShortformData(name, content_type_first, sorting):
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    displayed = int(form_fields['displayed'])
    sorting = sorting.lower()
    resetFile = form_fields['resetFile'] == "true"
    videosFirst = content_type_first == "video"

    content = pullShortformContent(name, displayed, resetFile, sorting, videosFirst)
    route = {'link_href': f"/viewShortformContent/{name}", 'repeat': "/viewShortformContent", 'repeatMessage': 'View More Content'}

    return json.dumps({'data': content, 'route': route})


@app.route('/viewShortformContent/Gallery/<name>/<sorting>/<content_type_first>')
@login_required
def viewShortformGallery(name, content_type_first, sorting):
    return render_template('viewContent/viewContentGallery.html')

@app.route('/viewShortformContent/Gallery/<name>/<sorting>')
@login_required
def viewShortformGalleryDefaultSort(name, sorting):
    return render_template('viewContent/viewContentGallery.html')

@app.route('/viewShortformContent/Gallery/<name>')
@login_required
def viewShortformGalleryDefault(name):
    return render_template('viewContent/viewContentGallery.html')
