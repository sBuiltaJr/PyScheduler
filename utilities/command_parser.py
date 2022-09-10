#This file parses (and validates) commands sent to the bot for use in the DB
#interfaces.  It returns the command as an argument list that can be directly
#fed to the respective database interface.

import argparse as ap
import json
import logging as log
import os
import sys

##### Command Parser Class #####
class CommandParser:

    def __init__(self):
        
        #This is an incredibly handy way to execute based on a valid function
        #name, automatically excluding invalid names, all in O(1) time!
        self.funcs = {'announcements': self.ParseAnnouncements,
                      'config'       : self.ParseConfig,
                      'create'       : self.ParseCreate,
                      'delete'       : self.ParseDelete,
                      'diagnose'     : self.ParseDiagnose,
                      'edit'         : self.ParseEdit,
                      'events'       : self.ParseEvents,
                      'guild'        : self.ParseGuild,
                      'init'         : self.ParseInit,
                      'list'         : self.ParseList,
                      'manage'       : self.ParseManage,
                      'oauth'        : self.ParseOauth,
                      'schedules'    : self.ParseSchedules,
                      'skip'         : self.ParseSkip,
                      'sort'         : self.ParseSort,
                      'sync'         : self.ParseSync,
                      'test'         : self.ParseTest,
                      'zones'        : self.ParseZones
                      }

        self.cmd_log = log.getLogger('command_log')
        self.cmd_log.setLevel(log.INFO)
        self.cmd_log.addHandler(log.FileHandler('command.log'))
        self.cmd_log.propagate = False
        self.cmd_log.info(f"Command logger initialized.")

        #We can now at least use the logger for errors.
        try:
            json_file = open('parse_strings.json')
            self.txt  = json.load(json_file)

        except Exception as err:
            self.cmd_log.error(f"Unable to get parser strings: {err}")

        #It's presumably faster to make all the parser instances once instead
        #of every invocation of a parse function.
        self.annAp = ap.ArgumentParser(prog=self.txt['ann_prog'], \
                                       description=self.txt['ann_desc'],
                                       allow_abbrev=False)
        #todo:  There's probably a clever way to loop this.
        self.annAp.add_argument("ID", type=str)
        self.annSub = self.annAp.add_subparsers()
        self.annSubAdd = self.annSub.add_parser('add', \
                                                help=self.txt['ann_add_help'])
        self.annSubAdd.add_argument('channel', type=int)
        self.annSubAdd.add_argument('rem_time', type=str)
        self.annSubAdd.add_argument('message', type=str)
        self.annSubRem = self.annSub.add_parser('remove',\
                                                help=self.txt['ann_rem_help'])
        self.annSubRem.add_argument('msg_id', type=int)

        #Config
        self.cfgAp = ap.ArgumentParser(prog=self.txt['cfg_prog'], \
                                       description=self.txt['cfg_desc'],
                                       allow_abbrev=False)
        self.cfgAp.add_argument("chan", type=int)
        self.cfgSub = self.cfgAp.add_subparsers()
        self.cfgSubMsg = self.cfgSub.add_parser('msg', \
                                                help=self.txt['cfg_msg_help'])
#        self.cfgSubMsg.add_argument('msg_txt', type=str, \
#                                     help=self.txt['cfg_msg_help'])
        self.cfgSubRmd = self.cfgSub.add_parser('remind',\
                                                help=self.txt['cfg_rmd_help'])
        self.cfgSubRmd.add_argument('-remove', type=str)
        self.cfgSubChn = self.cfgSub.add_parser('chan', \
                                                help=self.txt['cfg_chn_help'])
        self.cfgSubRms = self.cfgSub.add_parser('remind-msg', \
                                                help=self.txt['cfg_rms_help'])
        self.cfgSubRvp = self.cfgSub.add_parser('rsvp',
                                                 help=self.txt['cfg_rvp_help'])
        self.cfgSubRvp.add_argument('-on',\
                                    help=self.txt['cfg_rvp_on_help'])
        self.cfgSubRvp.add_argument('-off',\
                                    help=self.txt['cfg_rvp_off_help'])
        self.cfgSubRvp.add_argument('-add', nargs=2, \
                                    help=self.txt['cfg_rvp_add_help'])
        self.cfgSubRvp.add_argument('-remove', nargs=1, \
                                    help=self.txt['cfg_rvp_rmv_help'])
        self.cfgSubClr = self.cfgSub.add_parser('clear', \
                                                help=self.txt['cfg_clr_help'])
        self.cfgSubExc = self.cfgSub.add_parser('exclusivity',
                                                help=self.txt['cfg_exc_help'])

        #Create



    def SortCommand(self, cmd : str) -> list:
        """Parses the first component of a command string to determine the type
           of command supplied.  Each command has a different structure and
           thus a different argparser, requiring initial identification.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string.
           
           Output: list - A list of the arguments (null if invalid).
        """
        cmd_str    = ''
        ret        = []
        usr_string = []
        
        try:
            usr_string = str(cmd).split(sep=' ',maxsplit=1)
            #The slash has not yet been stripped.
            function   = self.funcs[(usr_string[0])[1:].lower()]

        except KeyError as err:
            self.cmd_log.error(f"Invalid command prefix in string: {cmd}")
            return ret

        #This is necessary to avoid split issues with commands as the original
        #bot allowed for unrestricted message format when quoted.  This makes
        #a split on the other, space-separated, command elements hard.
        #Fortuantely the quotes are requored to by the last element, allowing
        #us to scan for them and manually insert the string as an argument at
        #the end of an arg list.
        if args.endswith('"'):
                #User formmated commands can be of any length or pattern,
                #but shouldn't contain quotes, so we just need to parse
                #backwards to where another quote can be found to complete the
                #pair.
                cmd_index = args.rfind('"', 0,-1)

                #Technically the else is also an error but the parser can
                #handle it.
                if cmd_index > 0:
                    cmd_str = cmd[cmd_index:]
                    args    = cmd[:cmd_index]
                    print(f"split: {cmd_str}, {cmd_index}, {args}")
        usr_args = args.split(' ')
        usr_args.append(cmd_str)

        ret = function(usr_args)

        return ret


    def ParseAnnouncements(self, args : list) -> list:
        """Parses the announcements command.  Announcements requires at least
           1 argument with 2 optional; one for the channel to list 
           announcements, and 2 optional to either add a announcement string
           (instead of list) or which announcement to remove.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        try:
            self.cmd_log.debug(f"Annc args are: {args.split(' ')}")
            ret = self.annAp.parse_args(args);
        except Exception as err:
            self.cmd_log.error(f"Error in AnnParse: {err=}")

        return ret

    def ParseConfig(self, args : str) -> list:
        """Parses the config command.  Config modifies schedules and requires
           at least 2 arguments; one for the channel and one for the config.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []
        try:
            if args.endswith('"'):
                #User formmated commands can be of any length or pattern,
                #but shouldn't contain quotes, so we just need to parse
                #backwards to where another quote can be found to complete the
                #pair.
                cmd_index = args.rfind('"', 0,-1)

                #Technically the else is also an error but the parser can
                #handle it.
                if cmd_index > 0:
                    cmd_str = args[cmd_index:]
                    args = args[:cmd_index]
                    print(f"split: {cmd_str}, {cmd_index}, {args}")

            self.cmd_log.debug(f"cfg args are: {args.split(' ')}")
            ret = self.cfgAp.parse_args(args.split(' '));
            print(f"ret: {ret}")
        except Exception as err:
            self.cmd_log.error(f"Error in CfgParse: {err=}")


        return ret

    def ParseCreate(self, args : str) -> list:
        """Parses the create command.  Create requires at least 3 arguments and
           can have many for specifying comments, roles, and more.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseDelete(self, args : str) -> list:
        """Parses the delete command.  Delete may specify an optional command
           for deleteing events, channels, or all schedules in the guild.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseDiagnose(self, args : str) -> list:
        """Parses the diagnose command.  This is a argument-less command that
           performs basic setup checks for the bot (such as guild/channel
           access or definition).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseEdit(self, args : str) -> list:
        """Parses the edit command.  Edit may specify a series of arguments,
           up to the total elements in an event.  At least 2 are required.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseEvents(self, args : str) -> list:
        """Parses the events command.  Events has one optional argument, used
           to filter events for a specific channel instead of 'all'.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseGuild(self, args : str) -> list:
        """Parses the guild command.  Guild requires at least 2 arguments, one
           for the type of information modified, and one for its config.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseInit(self, args : str) -> list:
        """Parses the init command.  Init may specify an optional command
           channel, provided as a channel ID.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        print(f"init! Args: {args}")
        ret = []

        return ret

    def ParseList(self, args : str) -> list:
        """Parses the list command.  List requires one argument and up to 3,
           1 is the event ID to lsit and the other 2 are dispaly and filters.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseManage(self, args : str) -> list:
        """Parses the manage command.  Oauth has 4 required arguments: 1 for
           the event ID, 1 for the command type (add/remove), 1 for the event
           group, and 1 for the user ID.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseOauth(self, args : str) -> list:
        """Parses the oauth command.  Oauth has 1 required argument, the oauth
           token necessary to access the schedule's associated Google Calendar.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParsePurge(self, args : str) -> list:
        """Parses the purge command.  Purge requries one argument, the channel
           from which to delete (up to 100) bot messages from per invocation.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseSchedules(self, args : str) -> list:
        """Parses the schedules command.  This is a argument-less command that
           simply lists all schedules assigned to the guild.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseSkip(self, args : str) -> list:
        """Parses the skip command.  Skip has 1 required argument; which event
           ID to skip (and schedule to the next entry).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseSort(self, args : str) -> list:
        """Parses the sort command.  Sort has 1 required argument and 1
           optional; 1 for which  channel to sorte events in (up to 15), and 
           1 for the order (descending by date is otherwise assumed).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseSync(self, args : str) -> list:
        """Parses the sync command.  Sync has 1 required argument and 2
           optional, 1 for which channel to sync and 2 for how to sync the 
           channel (import/export form Google, and which calendar).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseTest(self, args : str) -> list:
        """Parses the test command.  Test has 1 required argument and 1
           optional, 1 for the test message to send, and 1 for what type of 
           test message (such as start, remind, or end).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret

    def ParseZones(self, args : str) -> list:
        """Parses the zones command.  Zones has 1 required argument, used to
           filter for which calendars fall in the specified zone.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """
        ret = []

        return ret


if __name__ == '__main__':
    #Temporary until the log is actually made in the main python class.
    log.basicConfig(filename=('parse.log'), \
                        encoding='utf-8', \
                        filemode='a', \
                        level=log.INFO)
    cp = CommandParser()
#    ret = cp.SortCommand("/init This is a Test!  This is only a test.")
#    print(f"ret = {ret}")

#    ret = cp.SortCommand("/announcements J09DlA add 4893839 start-1h 'stuff'")
#    ret = cp.SortCommand("/announcements J09DlA remove 1")
#    ret = cp.SortCommand("/announcements J09DlA")

#    ret = cp.SortCommand('/config 474738')
    ret = cp.SortCommand('/config 474738 msg "@here The event %t %a. %f"')
    ret = cp.SortCommand('/config 474738 remind "10, 20, 30 min"')
    ret = cp.SortCommand('/config 474738 remind -remove "20 min"')
#    ret = cp.SortCommand('/config 474738 end-remind "10 min"')
#    ret = cp.SortCommand('/config 474738 chan "general"')
#    ret = cp.SortCommand('/config 474738 remind-msg "reset"')
#    ret = cp.SortCommand('/config 474738 rsvp -on')
#    ret = cp.SortCommand('/config 474738 rsvp -add DPS 478293472')
#    ret = cp.SortCommand('/config 474738 rsvp -remove Undecided')
#    ret = cp.SortCommand('/config 474738 clear 2345273450')
#    ret = cp.SortCommand('/config 474738 exclusivity off')


    print(f"Done!")



#Basic idea: Have a different parser for each command, return list.
#Need the initial handler to peel off any qutoe strings and add as an argument.
