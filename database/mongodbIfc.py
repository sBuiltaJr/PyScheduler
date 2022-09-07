#This file manages interfacing to a mongoDB server of at least version 6.
#It may work with older mongoDB versions, though they are untested.

import json
import logging as log
import os
import pymongo
import sys

#####  Package Variables  #####
#Temporary until this is purely instantiated by a parent.
db = ''



#####  Manager Class  #####
class mongodbIfc:
    """Acts as the dabase interface for MongoDB SQL servers.  Also creates
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
            json_file = open('mongodb_cfg.json')
            self.args = json.load(json_file)
        #Sure, it's more pythonic to use with and only catch limited exceptions,
        #but making a case here for every possible exception type is dumb.
        except Exception as e:
            print(f"Error opening the mongodb config files: {e=}")
            sys.exit(1)

        os.makedirs(self.args['log_dir'], \
                        mode=int(self.args['log_file_mode'], 8),\
                        exist_ok=True)

        self.db_log = log.getLogger('mongo_db_log')
        self.db_log.setLevel(getattr(log, self.args['log_level'].upper()))
        self.db_log.addHandler(log.FileHandler( \
                               self.args['log_dir'] + os.sep + 'db_ifc_log.log'))
        self.db_log.propagate = False
        self.db_log.info(f"MongoDB Logger logging to {self.args['log_dir']}")

        #We can now at least use the logger for errors.
        try:
            json_file = open('mongodb_commands.json')
            self.cmds = json.load(json_file)
        #Sure, it's more pythonic to use with and only catch limited exceptions,
        #but making a case here for every possible exception type is dumb.
        except Exception as e:
            self.db_log.error(f"Unable to get MongoDB commands: {e=}")
            sys.exit(1)


    def validateInstall(self):
        """Validates all the database components are accessable and usable by the
            script.

            Input: self - Pointer to the current object instance.

            Output: bool - True if install is valid and usable.
        """
        all_ok = False

        #These are separarte try statements for better error debugging.
        try:
            self.con = pymongo.MongoClient(self.args['host'], \
                                            int(self.args['port']))

        except pymongo.errors as err:
            self.db_log.error(f"Error connecting to mongodb: {err}")
            return all_ok

        try:
            #The python interface will make the db upon writing to a table, and
            #automatically includes an 'IF EXIST' condition.
            self.db = self.con[self.args['database']]

            for table in self.args['tables'].values():
                #Like mentione above, we have to actually write to a collection 
                #(table) to verify the transaction works.
                coll   = self.db.table
                result = coll.insert_one({'test_val': '65536'})

                if not result.acknowledged:
                    raise pymongo.errors.InvalidOperation("Write test failed!")
                else:
                    result = coll.delete_one({'_id' : result.inserted_id})

                    if not result.acknowledged:
                        raise pymongo.errors.InvalidOperation("Read test failed!")

        except pymongo.error.InvalidOperation as err:
            self.db_log.error(f"Error accessing collections! {err}")

        except pymongo.errors as err:
            self.db_log.error(f"Unable to access database: {err=}")
            return all_ok

        all_ok = True;

        return all_ok


if __name__ == '__main__':
    #Temporary until the log is actually made in the main python class.
    log.basicConfig(filename=('log.log'), \
                        encoding='utf-8', \
                        filemode='a', \
                        level=log.INFO)

    db = mongodbIfc()

    if not db.validateInstall():
        #This is intentionally written to the terminal (instead of a logger) so
        #a new user gets an overt and obvious prompt to check the logs.
        print(f"Error validating install, see log for details.")


#Python is sure nice sometiems:  have argparser return user input parsed, just give string args.
