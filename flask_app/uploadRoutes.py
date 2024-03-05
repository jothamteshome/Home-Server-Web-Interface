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
    options = db.getAllUploadDirectories()
    return cond_render_template('UploadContent/upload.html',
                                options=options,
                                cond_statement=session['user_info']['role'] == "admin")


@app.route('/processUploadContent', methods=['POST'])
@login_required
def processUpload():
    search_dir = request.form['search_dir'].strip()
    source_dir = request.form['source'].strip()
    captions = request.form.getlist('captions')
    images = list(request.files.listvalues())[0]

    upload_count, returnedContent = uploadImages(search_dir, source_dir, captions, images)

    success_data = {'uploaded': upload_count, 'source_name': source_dir, 'duplicates': len(images) - upload_count}

    display_data = {'success': success_data, 'content': returnedContent}

    return json.dumps(display_data)

    
