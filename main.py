# Copyright 2022 Vishnu Lagudu - License: MIT License

from __future__ import division as _, unicode_literals as _; del _

# Importing all required libraries
import flask, flask.ext.cas, werkzeug
import Data_Handler
import datetime
import simplejson as json
import flask_hci_server, flask_helpers

# Configuring the app object
app = flask.Flask(__name__, static_url_path = '/static')
app.secret_key = "hello"
app.jinja_env.filters['zip'] = zip
flask_hci_server.adapt_for_crowd_server(app)

# Enable Purdue Authentication (CAS)
ALLOWED_USERS = ('vlagudu', 'mmetwaly', 'aq')
app.config.update(flask_hci_server.PURDUE_CAS_CONFIG)
app.config['CAS_AFTER_LOGIN'] = 'admin'
cas = flask.ext.cas.CAS(app, '/cas')

path = "/data/_fake_data.db"  # ---> if the data is stored in a diffrent db change the route here

# Site URL : https://crowd.ecn.purdue.edu/43/

# Route for Home Page
@app.route('/')
@app.route('/home', methods = ["POST", "GET"])
def home():
	return flask.render_template("home.html")

# Route for the DataTable Page
@app.route('/Data_Tables')
def Data_Tables():

	# Fetch records from the database
	db = Data_Handler.DataHandler(path) # Creates a db object of class DataHandler
	tables = db.get_table()
	all_headings = db.get_all_header()
	all_data = db.get_all_data()
	db.close_conn()

	return flask.render_template("Data_Tables.html", title='DATA TABLES', tables = tables, all_headings = all_headings, all_data = all_data)

# Route for page that allows admin to enter data into database. (admin access required)
@app.route("/admin", methods=['POST', 'GET'])
@flask_hci_server.login_required
def admin():
	user_name = cas.attributes["cas:login"]
	if user_name not in ALLOWED_USERS:
		raise werkzeug.exceptions.Forbidden
	if flask.request.method == "POST":
		db = Data_Handler.DataHandler(path) # Creates a db object of class DataHandler
		full_name = flask.request.form['full_name']
		email_address = flask.request.form['email_address']
		video_ids_str = flask.request.form["video_ids_str"]

		# video_ids_str = "".join(video_ids_str.split())
		# ptn_video_ids = r'^\d+(?:,\d+)*$' # ex:  "3"  "3,1,2"
	 	# if re.match(ptn_video_ids, video_ids_str) is None:
 		# 	abort(400, description="video_ids should be a comma-separated list of integers")
	
		db.add_participant(full_name, email_address,video_ids_str)
		db.close_conn()
	return flask.render_template("admin.html")

# Route for Preliminary Analysis Page
@app.route('/Preliminary_Analysis')
def Preliminary_Analysis():
	return flask.render_template("Preliminary_Analysis.html", title='PRELIMINARY ANALYSIS')

# Runs the app as well as specifies the port
if __name__ == '__main__':
	flask_helpers.main(app, port = 8043, host = '127.0.0.1', debug = False, use_evalex = False)
