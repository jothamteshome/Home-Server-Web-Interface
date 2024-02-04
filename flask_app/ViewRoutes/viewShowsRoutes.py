import json
import base64

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import retreiveShowContent, _copyFilesToTemp, _listShows


# Displays template for viewing longform movie/show content
@app.route('/viewShows')
@login_required
@clear_temp
def viewShows():
    return render_template('viewContent/viewShows.html', contentList=_listShows())


# Processes the passing of data for the listing of show names
@app.route('/processShows', methods=['POST'])
@login_required
def processShows():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    show_dir_path = form_fields['show-dir-path']
    sorting = form_fields['sorting'].strip().lower()

    content = retreiveShowContent(name, show_dir_path, sorting)
    return json.dumps(content)


# Handles the downloading of content to temp directory after show selection is made
@app.route('/downloadTempShowContent', methods=['POST'])
@login_required
@clear_temp
def downloadTempShowContent():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name, source, thumb = form_fields['name'], form_fields['loc'], form_fields['thumb']

    filesToDownload = [(f"{name}.mp4", source)]

    if thumb:
        filesToDownload.append((f"{name}.jpg", thumb))

    _copyFilesToTemp(filesToDownload)
    

    return json.dumps({})


# Processes the displaying of singular show video from temp directory
@app.route('/viewShows/<showName>/<contentName>')
@login_required
def streamShows(showName, contentName):
    contentName = base64.urlsafe_b64decode(contentName).decode('utf-8')
    img_data = [{'name': contentName, 'data': {'file': f"{_tempDirectory(True)}/{contentName}.mp4", 
                                               'thumb': f"{_tempDirectory(True)}/{contentName}.jpg", 'type': 'video'}}]

    success_data = {'message': f"Currently viewing {showName} content", 
                    'alt': f"Image from {showName}",
                    'href': "/viewShows", 'button-text': "View More Shows"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)


# @app.route('/showData/<show_name>/<sorting>', methods=['POST'])
# @login_required
# def getShowData(show_name, sorting):
#     return json.dumps(retreiveShowContent(" ".join(show_name.split("__")), sorting.strip().lower()))

# @app.route('/viewShows/Options/<showName>/<sorting>')
# @login_required
# def displayShowOptions(showName, sorting):
#     return render_template('viewContent/viewShowOptions.html')