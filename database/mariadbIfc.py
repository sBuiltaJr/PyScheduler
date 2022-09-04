#This file manages itnerfacing to a maraidb server of at least version 10.
#It may work with older mariadb versions, though they are untested.

import json
import logging as log
import mariadb
import os
import sys

#####  Manager Class  #####
class mariadbIfc:
	"""Acts as the dabase interface for MariaDB SQL servers.  Also creates
		tables, users, and fields as needed.
	"""

	def __init__(self):
		"""Reads the included json config for db parameters, like username and
			login information.  Verification is handled in a different function.
			Also instantiates a logger specifically for this class.
		"""
		
		self.args = {}
		
		#The config file lcoation is nonconfigurable, for now.
		with open('mariadb_cfg.json') as json_file:
			self.args = json.load(json_file)

		if not self.args:
			raise FileNotFoundError('mariadb_cfg.json file empty or missing!')
		
		os.makedirs(self.args['log_dir'], \
						mode=int(self.args['log_file_mode'], 8),\
						exist_ok=True)
						
		self.db_log = log.getLogger('maria_db_log')
		self.db_log.setLevel(getattr(log, self.args['log_level'].upper()))
		self.db_log.addHandler(log.FileHandler( \
									self.args['log_dir'] + os.sep + 'db_ifc_log.log'))
		self.db_log.propagate = False
		self.db_log.info(f"Mariadb Logger logging to {self.args['log_dir']}")



if __name__ == '__main__':
	#Temporary until the log is actually made in the main python clsass.
	log.basicConfig(filename=('log.log'), \
						encoding='utf-8', \
						filemode='a', \
						level=log.INFO)
	db = mariadbIfc()
