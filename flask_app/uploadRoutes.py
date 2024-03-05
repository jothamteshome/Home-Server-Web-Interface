import json

from flask import current_app as app
from flask import request, session, redirect
from flask_app.routeTools import clear_temp, login_required, render_template, cond_render_template
from flask_app.utils.createdMemeHandling import _uploadMeme
from flask_app.utils.imageUploading import uploadImageSet
from flask_app.utils.globalUtils import _openJSONDirectoriesFile
from flask_app.utils.displayContent import _hideFilename
from flask_app.utils.database import database

db = database()

####################################################################
#              FINALIZED MEME UPLOAD HANDLING                      #
####################################################################

# Displays the template for uploading a finalized meme
@app.route('/uploadFinalizedMeme')
@login_required
@clear_temp
def uploadFinalizedMeme():
    return cond_render_template('UploadContent/uploadFinalizedMeme.html', cond_statement=session['user_info']['role'] == 'admin')

@app.route('/processUploadFinalizedMeme', methods=['POST'])
@login_required
def processUploadFinalizedMeme():
    # Capture inputted data and extract extension
    caption = request.form['caption'].strip()
    img = request.files['image']

    ext = img.content_type.split('/')[-1]
    
    filename, duplicate, img_data = _uploadMeme(img, caption)

    if duplicate:
        message = f"Caption Already Exists For {filename}"
    elif not duplicate and len(img_data[f"{filename}.{ext}"]['captions']) > 1:
        message = f"Successfully Added Caption To {filename}"
    else:
        message = f"Successfully Created {filename}"

    img_name = list(img_data.keys())[0]

    temp_display = {"name": img_name, "data": img_data[img_name], 'routingName': _hideFilename(img_name)}

    display_data = {'success': message, "content": temp_display}

    return json.dumps(display_data)


####################################################################
#                   SHORTFORM UPLOAD HANDLING                      #
####################################################################

# Route handling the displaying the template to upload shortform content
@app.route('/uploadShortformContent')
@login_required
@clear_temp
def uploadShortformContent():
    options = db.getAllUploadDirectories()
    return cond_render_template('UploadContent/upload.html', 
                                       options=options, 
                                       cond_statement=session['user_info']['role'] == 'admin')


# Route handling the processing of uploaded shortform data
@app.route('/processUploadShortform', methods=['POST'])
@login_required
def processUploadShortform():
    folder_name = request.form['name']
    genre = request.form['genre']
    images = list(request.files.listvalues())[0]

    upload_count, content = uploadImageSet(images, folder_name, genre)

    success_data = {'uploaded': upload_count, 'folderName': folder_name, 'duplicates': len(images) - upload_count}

    if 'view-route' in _openJSONDirectoriesFile()['upload-short-form-genres'][genre]:
        success_data['route'] = _openJSONDirectoriesFile()['upload-short-form-genres'][genre]['view-route']

    display_data = {'success': success_data, 'content': content}
    
    return json.dumps(display_data)