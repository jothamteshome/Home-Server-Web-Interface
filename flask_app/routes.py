import json

from flask import current_app as app
from flask import redirect, request, session
from flask_app import uploadRoutes
from flask_app.ViewRoutes import viewComicsRoutes, viewFinalizedMemeRoutes, viewPremadeMemeRoutes, viewShortformRoutes, viewShowsRoutes
from flask_app.utils.globalUtils import _tryRemoveFile, _dataBatchesFile, _addComicsToDatabase, _addShowsToDatabase, _addAllShortContentToDatabase
from flask_app.routeTools import clear_temp, render_template
from flask_app.utils.database  import database
db = database()

#####################################
# Authentication
#####################################
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
@clear_temp
def logout():
	_tryRemoveFile(_dataBatchesFile())
	session.pop('user_info', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    status = db.authenticate(form_fields['username'], form_fields['password'])
    
    if status['success'] == 0:
        return json.dumps(status)
    else:
        session['user_info'] = {'username': form_fields['username'], 'role': status['role']}
        _tryRemoveFile(_dataBatchesFile())
        status.pop('role') 
        return json.dumps(status)
    
    
@app.route('/processsignup', methods = ["POST","GET"])
def processsignup():
	form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	status = db.createUser(form_fields['username'], form_fields['password'])

	if status['success'] == 0:
		return json.dumps(status)
	else:
		session['user_info'] = {'username': form_fields['username'], 'role': status['role']}
		_tryRemoveFile(_dataBatchesFile())
		status.pop('role') 
		return json.dumps(status)


@app.route('/')
@clear_temp
def root():
    return render_template('home.html')

@app.route('/home')
@clear_temp
def home():
    return redirect('/')

@app.route('/populateComicsDatabase', methods=['POST'])
def populateComicsDatabase():
    _addComicsToDatabase()
    app.freshApp = False
    return json.dumps({})

@app.route('/populateShowsDatabase', methods=['POST'])
def populateShowsDatabase():
    _addShowsToDatabase()
    app.freshApp = False
    return json.dumps({})

@app.route('/populateShortContentDatabase', methods=['POST'])
def populateShortContentDatabase():
    _addAllShortContentToDatabase()
    app.freshApp = False
    return json.dumps({})