import json

from flask import current_app as app
from flask import request, session
from flask_app.routeTools import clear_temp, login_required, cond_render_template
from flask_app.utils.imageUploading import uploadImages
from flask_app.utils.database import database
db = database()


@app.route('/uploadContent')
@login_required
@clear_temp
def uploadContent():
    options = db.getAllUploadSearchDirectories()
    return cond_render_template('UploadContent/upload.html',
                                options=options,
                                cond_statement=session['user_info']['role'] == "admin")


@app.route('/processUploadContent', methods=['POST'])
@login_required
def processUpload():
    search_dir = request.form['search_dir'].strip()
    source_dir = request.form['source'].strip()
    new_dir = request.form['new_dir'] == "true"
    captions = request.form.getlist('captions')
    images = list(request.files.listvalues())[0]

    if new_dir:
        db.storeUploadSourceDirectories([(search_dir, source_dir)])

    routes = {"Shortform Content": "/viewShortformContent", "Premade Meme": "/viewPremadeMemes", "Finalized Meme": "/viewFinalizedMemes"}

    contentType = db.getDecodedData('SELECT section_content_style FROM uploadSearchDirectories WHERE section_name = %s', [search_dir])[0]['section_content_style']

    upload_count, returnedContent = uploadImages(search_dir, source_dir, captions, images)

    success_data = {'uploaded': upload_count, 'source_name': source_dir, 'duplicates': len(images) - upload_count, 'route': routes[contentType]}
    display_data = {'success': success_data, 'content': returnedContent}

    return json.dumps(display_data)


@app.route('/uploadContent/Options/<search_dir>')
@login_required
def uploadSearchOptions(search_dir):
    search_dir_info = db.getUploadSearchDirectory(" ".join(search_dir.split("__")))

    if search_dir_info['search_dir_storage']:
        return cond_render_template('UploadContent/uploadData.html',
                                        new_dir=False,
                                        caption_required=search_dir_info['caption_required']==True,
                                        cond_statement=True)
    

    options = db.getUploadSourceDirectories(" ".join(search_dir.split("__")))

    options = {option: "__".join(option.split(" ")) for option in options}
    options["Create Folder"] = "Create__Folder"

    return cond_render_template('UploadContent/uploadOptions.html',
                                search_dir=search_dir,
                                non_url_search_dir=" ".join(search_dir.split("__")),
                                options=options,
                                cond_statement=session['user_info']['role'] == "admin")


@app.route('/uploadContent/Options/<search_dir>/<source_dir>')
@login_required
def processUploading(search_dir, source_dir):
    search_dir = " ".join(search_dir.split("__"))
    caption_required = db.getDecodedData('SELECT caption_required FROM uploadSearchDirectories WHERE section_name = %s', [search_dir])[0]['caption_required']
    return cond_render_template('UploadContent/uploadData.html',
                                source_dir=" ".join(source_dir.split("__")),
                                new_dir=source_dir=="Create__Folder",
                                caption_required=caption_required==True,
                                cond_statement=True)


@app.route('/setUploadSelectorIds', methods=['POST'])
@login_required
def setUploadSelectorIds():
    ids = request.form.getlist('id')

    databaseUpdate = []

    for i in range(len(ids)):
        prev_id, next_id = ids[i-1], ids[(i+1) % len(ids)]
        databaseUpdate.append([prev_id, next_id, ids[i]])

    db.updateShortContent(['prev_content_id', 'next_content_id'], databaseUpdate)

    return json.dumps({})
    
