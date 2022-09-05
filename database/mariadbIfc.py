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
		self.cmds = {}
		
		#The config file lcoation is nonconfigurable, for now.
		try:
			json_file = open('mariadb_cfg.json')
			self.args = json.load(json_file)
		#Sure, it's more pythonic to use with and only catch limited exceptions, 
		#but making a case here for every possible exception type is dumb.
		except Exception as e:
			print(f"Error opening the mariadb config files: {e=}")
			sys.exit(1)
		
		os.makedirs(self.args['log_dir'], \
						mode=int(self.args['log_file_mode'], 8),\
						exist_ok=True)
						
		self.db_log = log.getLogger('maria_db_log')
		self.db_log.setLevel(getattr(log, self.args['log_level'].upper()))
		self.db_log.addHandler(log.FileHandler( \
									self.args['log_dir'] + os.sep + 'db_ifc_log.log'))
		self.db_log.propagate = False
		self.db_log.info(f"Mariadb Logger logging to {self.args['log_dir']}")
		
		#We can now at least use the logger for errors.
		try:
			json_file = open('mariadb_commands.json')
			self.cmds = json.load(json_file)
		#Sure, it's more pythonic to use with and only catch limited exceptions, 
		#but making a case here for every possible exception type is dumb.
		except Exception as e:
			self.db_log.error(f"Unable to get MariaDB commands: {e=}")
			sys.exit(1)

	def validateInstall(self, create : bool):
		"""Validates all the database components are accessable and usable by the
			script.  It optionally attempts to create any missing tables/databases
			if directed with the 'create' option.
			
			Input: self - Pointer to the current object instance.
					 create - Whether to attempt making a DB if it doesn't exist.
			
			Output: bool - True if install is valid and usable.
		"""
		#This start true so the acces attempt can set it false to signal the
		#create option
		all_ok = True
		
		try:
			self.con = mariadb.connect(host=self.args['host'], \
												port=int(self.args['port']), \
												user=self.args['user_name'], \
												password=self.args['password'])
		except mariadb.Error as err:
			self.db_log.error(f"Error connecting to mariadb: {err=}")
			all_ok = False
			
			if not create :
				return all_ok
		
		if not all_ok:
			#At best we can attempt to try the default user/password connection,
			#and exit if it fails.  From tehr eonly the user can fix the problem.
			try:
				self.con = mariadb.connect(host="127.0.0.1", \
													port=3306, \
													user="root", \
													password="")
			except mariadb.Error as err:
				self.db_log.error("Unable to log in with root using the default mariadb settings, you must make an account for me first or allow root access. Or is the service off?")
				self.db_log.error(f"Error: {err=}") 
										
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
	
