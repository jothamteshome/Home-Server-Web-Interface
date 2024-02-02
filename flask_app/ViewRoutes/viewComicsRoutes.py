import json
import os

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import  collectComics, collectComicSeries, _copyFilesToTemp, _listComicNames


@app.route('/viewComics')
@login_required
@clear_temp
def viewComics():
    return render_template('viewContent/viewComics.html', contentList=_listComicNames())


@app.route('/processComics', methods=['POST'])
@login_required
def processComics():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    optionPath = form_fields['optionPath']
    sorting = form_fields['sorting'].strip().lower()

    content = collectComics(optionPath, sorting)
    return json.dumps(content)


@app.route('/processComicSeries', methods=['POST'])
@login_required
def processComicSeries():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    name = form_fields['name']
    loc = form_fields['loc']

    content = collectComicSeries(name, loc)
    return json.dumps(content)


@app.route('/downloadComic', methods=['POST'])
@login_required
def downloadComic():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    subdir = form_fields['name']
    loc = form_fields['loc']

    comic = []

    for page in os.listdir(loc):
        comic.append((page, f"{loc}\\{page}"))

    _copyFilesToTemp(comic, subdir)

    return json.dumps({})


@app.route('/viewComics/<comicName>')
@login_required
def displayComics(comicName):
    img_data = []

    for file in os.listdir(f"{_tempDirectory()}\\{comicName}"):
        img_data.append({'name': file, 'data': {'file': f"{_tempDirectory(True)}/{comicName}/{file}", 'type': 'image'}})

    comicName = " ".join(comicName.split("_")).title()

    success_data = {'message': f"Currently viewing: {comicName}", 
                    'alt': f"{comicName} comic page",
                    'href': "/viewComics", 'button-text': "View More Comics"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)