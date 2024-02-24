import time

from flask import Flask
from flask_failsafe import failsafe
from flask_app.utils.PropertiesReader import PropertiesReader
from flask_app.utils.globalUtils import _deleteUserDataBatches, _deleteAllTempDirectores, _addComicsToDatabase, _addShowsToDatabase, _addPremadeMemes, _addFinalizedMemes, _addShortformContent


#--------------------------------------------------
# Create a Failsafe Web Application
#--------------------------------------------------
@failsafe
def create_app():
	app = Flask(__name__)
	_deleteAllTempDirectores()
	_deleteUserDataBatches()

	from flask_app.utils.database import database
	db = database()
	db.createTables(purge=True)

	_addComicsToDatabase()
	_addShowsToDatabase()
	_addShortformContent()
	_addFinalizedMemes()
	_addPremadeMemes()

	# Create admin user
	prop_reader = PropertiesReader()
	admin_user = prop_reader.getAdminUser('ADMIN_USERNAME')
	admin_pass = prop_reader.getAdminUser('ADMIN_PASSWORD')

	db.createUser(user=admin_user, password=admin_pass, role='admin')

	app.secret_key = 'AKWNF1231082fksejfOSEHFOISEHF24142124124124124iesfhsoijsopdjf'

	with app.app_context():
		from . import routes
		return app