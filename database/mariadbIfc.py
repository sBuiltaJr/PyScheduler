#This file manages itnerfacing to a maraidb server of at least version 10.
#It may work with older mariadb versions, though they are untested.

import json
import logging as log
import mariadb
import os
import sys

#####  Package Variables  #####
#Temporary until this is purely instantiated by a parent.
db = ''

#####  Manager Class  #####
class mariadbIfc:
	"""Acts as the dabase interface for MariaDB SQL servers.  Also creates
		tables, users, and fields as needed.
	"""

	def __init__(self):
		"""Reads the included json config for db parameters, like username and
			login information.  Verification is handled in a different function.
			Also instantiates a logger specifically for this class.
			
			Input: self - Pointer to the current object instance.
			
			Output: None - Throws exceptions on error.
		"""
		
		self.args = {}
		
		#The config file lcoation is nonconfigurable, for now.
		try:
			json_file = open('mariadb_cfg.json')
			self.args = json.load(json_file)
		#Sure, it's more pythonic to use with and only catch limited exceptions, 
		#but making a case here for every possible exception type is dum.
		except Exception as e:
			print(f"Error opening the mariadb config file: {e=}")
			exit(1)
		
		os.makedirs(self.args['log_dir'], \
						mode=int(self.args['log_file_mode'], 8),\
						exist_ok=True)
						
		self.db_log = log.getLogger('maria_db_log')
		self.db_log.setLevel(getattr(log, self.args['log_level'].upper()))
		self.db_log.addHandler(log.FileHandler( \
									self.args['log_dir'] + os.sep + 'db_ifc_log.log'))
		self.db_log.propagate = False
		self.db_log.info(f"Mariadb Logger logging to {self.args['log_dir']}")


	def validateInstall(self, create : bool):
		"""Validates all the database components are accessable and usable by the
			script.  It optionally attempts to create any missing tables/databases
			if directed with the 'create' option.
			
			Input: self - Pointer to the current object instance.
					 create - Whether to attempt making a DB if it doesn't exist.
			
			Output: bool - True if install is valid and usable.
		"""
		all_ok = False
		
		return all_ok

if __name__ == '__main__':
	#Temporary until the log is actually made in the main python class.
	log.basicConfig(filename=('log.log'), \
						encoding='utf-8', \
						filemode='a', \
						level=log.INFO)
	db = mariadbIfc()
	if not db.validateInstall(True):
		#This is intentionally to the terminal so a new user gets an overt and
		#obviosu prompt to check the logs.
		print(f"Error validating install, see log for details.")
	
