import json
import os

from flask import current_app as app
from flask import request
from flask_app.routeTools import clear_temp, login_required, render_template
from flask_app.utils.globalUtils import _tempDirectory
from flask_app.utils.displayContent import  collectComics, collectComicSeries, _copyFilesToTemp, _listComicNames, _handleDisplayingComic
from flask_app.utils.database import database
db = database()


@app.route('/viewComics')
@login_required
@clear_temp
def viewComics():
    return render_template('viewContent/viewComics.html', contentList=_listComicNames())


@app.route('/comicData/<franchise_name>/<sorting>', methods=['POST'])
@login_required
def getComicData(franchise_name, sorting):
    return json.dumps(collectComics(" ".join(franchise_name.split("__")), sorting.strip().lower()))

@app.route('/comicData/<series_id>', methods=['POST'])
def getSeriesData(series_id):
    comicData = db.getComic(series_id)
    seriesData = db.getDecodedData('SELECT * FROM comicData WHERE comic_series=%s', [comicData['comic_name']])

    return json.dumps(collectComicSeries(seriesData))


@app.route('/viewComics/Standalone/<comic_id>')
@login_required
def displayComic(comic_id):
    comicData = _handleDisplayingComic(comic_id)
    img_data = []

    for file in os.listdir(f"{_tempDirectory()}\\{comic_id}"):
        img_data.append({'name': file, 'data': {'file': f"{_tempDirectory(True)}/{comic_id}/{file}", 'type': 'image'}})

    comicName = comicData['comic_name'].replace(comicData['comic_author'], "").strip()

    success_data = {'message': f"Currently viewing: {comicName}", 
                    'alt': f"{comicName} comic page",
                    'href': "/viewComics", 'button-text': "View More Comics"}
    
    return render_template('displayReturnedContent.html', img_data=img_data, success=success_data)


@app.route('/viewComics/Series/<series_id>')
@login_required
def displaySeries(series_id):
    return render_template('viewContent/viewComicOptions.html')


@app.route('/viewComics/Options/<franchise_name>/<sorting>')
@login_required
def displayFranchiseOptions(franchise_name, sorting):
    return render_template('viewContent/viewComicOptions.html')