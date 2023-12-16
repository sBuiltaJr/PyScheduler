#This file manages interfacing to a maraidb server of at least version 10.
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



	def validateInstall(self):
		"""Validates all the database components are accessable and usable by the
			script.
			
			Input: self - Pointer to the current object instance.
			
			Output: bool - True if install is valid and usable.
		"""
		all_ok = False
		
		#These are separarte try statements for better error debugging.  The idea
		#of creating missing DBs was scrapped due to implementation complexity.
		#(The script would need to invoke mariadb as sudo with root).
		try:
			self.con = mariadb.connect(host=self.args['host'], \
												port=int(self.args['port']), \
												user=self.args['user_name'], \
												password=self.args['password'])
			
		except mariadb.Error as err:
			self.db_log.error(f"Error connecting to mariadb: {err}")
			return all_ok
			
		try:
			#The interface requries the cursor.
			cursor = self.con.cursor()
			self.con.database = self.args['database']

			for db in self.args['tables'].values():
				#The script actually interacts with the Tables to truly confirm the
				#permissions, instead of just relying on the GRANT table, to avoid
				#having to parse the output and guess some of the parameters.
				cursor.execute(f"{self.cmds['create_bogus']}")
				cursor.execute(f"{self.cmds['insert_bogus']}")
				cursor.execute(f"{self.cmds['update_bogus']}")
				cursor.execute(f"{self.cmds['delete_bogus']}")
				#Delete also intentionally omits the 'IF EXIST' component for the
				#same reason.
				cursor.execute(f"{self.cmds['drop_bogus']}")
		
		except mariadb.OperationalError as err:
			self.db_log.error(f"Unable to access database: {err}")
			return all_ok
			
		except mariadb.ProgrammingError as err:
			self.db_log.error(f"Unable to access tables in database: {err}")
			return all_ok
			
		except mariadb.Error as err:
			self.db_log.error(f"Error running mariadb commands: {err=}")
			return all_ok

		all_ok = True;
		
		return all_ok



if __name__ == '__main__':
	#Temporary until the log is actually made in the main python class.
	log.basicConfig(filename=('log.log'), \
						encoding='utf-8', \
						filemode='a', \
						level=log.INFO)
						
	db = mariadbIfc()
	
	if not db.validateInstall():
		#This is intentionally written to the terminal (instead of a logger) so
		#a new user gets an overt and obvious prompt to check the logs.
		print(f"Error validating install, see log for details.")
	
