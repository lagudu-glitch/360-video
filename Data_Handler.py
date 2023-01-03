# Copyright 2022 Vishnu Lagudu - License: MIT License

from __future__ import division, unicode_literals

import os
import sqlite3

class DataHandler:
	def __init__(self, path):
		# Connect to the database
		self.conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + path)
		self.cursor = self.conn.cursor()
	
	# Static method to format the data present into a list of lists with the data in each 
	# row being an individual list
	@staticmethod
	def format_data(data):
		all_data = []
		for row in data:
			row_data = []
			for col in range(0, len(row)):
				row_data.append(str(row[col]))
			all_data.append(row_data)
		return all_data

	def last_insert_rowid(self, table_name):
		self.cursor.execute("select id from {};".format(table_name))
		return (self.cursor.fetchall()[-1][0])


	# Gets the data from the given table
	def get_data(self, table_name):
		data = self.cursor.execute("SELECT * FROM {};".format(table_name))
		return self.format_data(data)
	
	# Gets the column names from the given table
	def get_header(self, table_name):
		headers = self.cursor.execute("PRAGMA table_info({});".format(table_name))
		return [str(header[1]) for header in headers]

	# Gets all the table names from the given database
	def get_table(self):
		tables = self.cursor.execute('SELECT name from sqlite_master where type = "table";')
		return [str(table[0]) for table in tables]

	# Gets all the data from database and stores them in a dictionary with each table name 
	# as the key value being the formated data from the table -> ( format_data() ) 
	def get_all_data(self):
		tables = self.get_table()
		all_data_db = {}
		for table in tables:
			all_data_db[table] = self.get_data(table)
		return all_data_db

	# Gets all the column names from the database and stores them in a dictionary with each
	# table name as the key and the value being the column names of the table
	def get_all_header(self):
		tables = self.get_table()
		all_headers_db = {}
		for table in tables:
			all_headers_db[table] = self.get_header(table)
		return all_headers_db
	
	def create_study_session(self, person_id, video_ids_str):
		self.cursor.execute("INSERT INTO study_session (start_time_utc, person_id, videos) VALUES (datetime('now'), {}, '{}');".format(person_id, video_ids_str))
		self.conn.commit()

	# Function to insert non-default values into person table	
	def add_participant(self, full_name, email_address, video_ids_str):
		self.cursor.execute("SELECT id from person where email_address = '{}';".format(email_address))
		person_id = self.cursor.fetchall()
		if len(person_id) == 1:
			self.create_study_session(person_id[0][0], video_ids_str)
		else:
			self.cursor.execute("INSERT INTO person (full_name, email_address) VALUES ('{}', '{}');".format(full_name, email_address))
			self.conn.commit()
			self.create_study_session(self.last_insert_rowid('person'), video_ids_str)
	
	def ingest_interactions(self, view_segment_id, interactions):
		for values in interactions:
			self.cursor.execute("INSERT INTO interaction_event (view_segment, x_deg, y_deg, z_deg) VALUES ('{}', '{}', '{}', '{}');".format(view_segment_id, values["x_deg"], values["y_deg"], values["z_deg"]))
			self.conn.commit()

	# Function to close the connection with the database
	def close_conn(self):
		self.conn.close()