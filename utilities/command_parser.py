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


    def SortCommand(self, cmd : str) -> list:
        """Parses the first component of a command string to determine the type
           of command supplied.  Each command has a different structure and
           thus a different argparser, requiring initial identification.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string.
           
           Output: list - A list of the arguments (null if invalid).
        """


    def ParseAnnouncements(self, str) -> List:
        """Parses the announcements command.  Announcements requires at least
           1 argument with 2 optional; one for the channel to list 
           announcements, and 2 optioal to either add a announcement string
           (instead of list) or which announcement to remove.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseConfig(self, str) -> List:
        """Parses the config command.  Config modifies schedules and requires
           at least 2 arguments; one for the channel and one for the config.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseCreate(self, str) -> List:
        """Parses the create command.  Create requires at least 3 arguments and
           can have many for specifying comments, roles, and more.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseDelete(self, str) -> List:
        """Parses the delete command.  Delete may specify an optional command
           for deleteing events, channels, or all schedules in the guild.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseDiagnose(self, str) -> List:
        """Parses the diagnose command.  This is a argument-less command that
           performs basic setup checks for the bot (such as guild/channel
           access or definition).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseEdit(self, str) -> List:
        """Parses the edit command.  Edit may specify a series of arguments,
           up to the total elements in an event.  At least 2 are required.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseEvents(self, str) -> List:
        """Parses the events command.  Events has one optional argument, used
           to filter events for a specific channel instead of 'all'.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseGuild(self, str) -> List:
        """Parses the guild command.  Guild requires at least 2 arguments, one
           for the type of information modified, and one for its config.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseInit(self, str) -> List:
        """Parses the init command.  Init may specify an optional command
           channel, provided as a channel ID.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseList(self, str) -> List:
        """Parses the list command.  List requires one argument and up to 3,
           1 is the event ID to lsit and the other 2 are dispaly and filters.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseManage(self, str) -> List:
        """Parses the manage command.  Oauth has 4 required arguments: 1 for
           the event ID, 1 for the command type (add/remove), 1 for the event
           group, and 1 for the user ID.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseOauth(self, str) -> List:
        """Parses the oauth command.  Oauth has 1 required argument, the oauth
           token necessary to access the schedule's associated Google Calendar.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParsePurge(self, str) -> List:
        """Parses the purge command.  Purge requries one argument, the channel
           from which to delete (up to 100) bot messages from per invocation.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseSchedules(self, str) -> List:
        """Parses the schedules command.  This is a argument-less command that
           simply lists all schedules assigned to the guild.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseSkip(self, str) -> List:
        """Parses the skip command.  Skip has 1 required argument; which event
           ID to skip (and schedule to the next entry).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseSort(self, str) -> List:
        """Parses the sort command.  Sort has 1 required argument and 1
           optional; 1 for which  channel to sorte events in (up to 15), and 
           1 for the order (descending by date is otherwise assumed).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseSync(self, str) -> List:
        """Parses the sync command.  Sync has 1 required argument and 2
           optional, 1 for which channel to sync and 2 for how to sync the 
           channel (import/export form Google, and which calendar).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseTest(self, str) -> List:
        """Parses the test command.  Test has 1 required argument and 1
           optional, 1 for the test message to send, and 1 for what type of 
           test message (such as start, remind, or end).

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """

    def ParseZones(self, str) -> List:
        """Parses the zones command.  Zones has 1 required argument, used to
           filter for which calendars fall in the specified zone.

           Input: self - Pointer to the current object instance.
                  cmd - Pointer to the user-supplied string (sans command).

           Output: list - A list of the arguments (null if invalid).
        """


if __name__ == '__main__':
    #Temporary until the log is actually made in the main python class.
    log.basicConfig(filename=('parse.log'), \
                        encoding='utf-8', \
                        filemode='a', \
                        level=log.INFO)



#Basic idea: Have a different parser for each command, return list.
