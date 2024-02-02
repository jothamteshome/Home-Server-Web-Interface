import json

from flask import current_app as app
from flask import request
from flask_app.ViewRoutes import viewComicsRoutes, viewFinalizedMemeRoutes, viewPremadeMemeRoutes, viewShortformRoutes, viewShowsRoutes
from flask_app.utils.database  import database
db = database()

@app.route('/storeReturnData', methods=['POST'])
def storeReturnData():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    search_name = form_fields['search_name'][:64].encode('utf-8')
    item_name = form_fields['item_name'].encode('utf-8')
    item_loc = form_fields['item_loc'].encode('utf-8')
    item_route = form_fields['processURL'].encode('utf-8')
    item_dir = form_fields['item_dir'].encode('utf-8')
    item_thumb = form_fields['item_thumb'].encode('utf-8')

    db.storeReturnData(search_name, item_name, item_loc, item_route, item_dir, item_thumb)

    return json.dumps({'success': 1})


@app.route('/getReturnData', methods=['POST'])
def getReturnData():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    search_name = form_fields['search_name'][:64]

    returned = db.getReturnData(search_name)[0]
    for row in returned:
        returned[row] = returned[row].decode('utf-8')

    return json.dumps(returned)