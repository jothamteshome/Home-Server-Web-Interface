import json

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.globalUtils import _openJSONDirectoriesFile, _tempDirectory
from flask_app.utils.displayContent import collectFinalizedMemes, retreiveFinalizedMemes, _copyFilesToTemp
from flask_app.utils.database import database

db = database()

# Displays route to show finalized memes template
@app.route('/viewFinalizedMemes')
@login_required
@clear_temp
def viewFinalizedMemes():
    return cond_render_template('viewContent/viewFinalizedMemes.html', contentList=retreiveFinalizedMemes(), 
                                cond_statement="finalized-memes-dir" in _openJSONDirectoriesFile()['conditionally-included-routes'])


# Returns data from temp directory for singular finalized meme
@app.route('/viewFinalizedMemes/<content_id>')
@login_required
def singleFinalizedMeme(content_id):
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


    content_hash = contentData['content_name'].split('.')[0]

    success_data = {'message': f"Currently viewing captions for {content_hash}", 
                    'alt': f"Meme with finalized caption",
                    'href': "/viewFinalizedMemes", 'button-text': "View More Memes", 'loop': True, 'link_href': "/viewFinalizedMemes"}
    
    return render_template('displayReturnedContent.html', img_data=[img_data], success=success_data)


@app.route('/finalizedMemeData/<name>/<content_type_first>/<sorting>', methods=['POST'])
@login_required
def getFinalizedMemeData(name, content_type_first, sorting):
    form_fields = form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    displayed = int(form_fields['displayed'])
    resetFile = form_fields['resetFile'] == "true"

    content = collectFinalizedMemes(displayed, resetFile, 'shuffle')
    route = {'link_href': "/viewFinalizedMemes", 'repeat': "/viewFinalizedMemes", 'repeatMessage': 'View More Memes'}

    return json.dumps({'data': content, 'route': route})

@app.route('/viewFinalizedMemes/Gallery/Finalized__Memes')
@login_required
def viewFinalizedMemeGallery():
    return render_template('viewContent/viewContentGallery.html')