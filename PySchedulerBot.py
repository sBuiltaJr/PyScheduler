#Manages user requests through Discord to generate images with a Stable
#Diffusion model filepath supplied in the config.json file.  Cannot prevent
#Specific types of images, like NSFW, from being generated.


#####  Imports  #####

import asyncio as asy
import base64 as b64
import datetime as dt
import discord as dis
from discord import app_commands as dac
import io
import logging as log
import logging.handlers as lh
import json
import multiprocessing as mp
import os
import pathlib as pl
import re
import src.managers.QueueMgr as qm
import threading as th
import time
from typing import Literal, Optional, Union

#####  Hacks  #####
#https://github.com/python/cpython/issues/90015
#from typing import TypeAlias
#StrIntAlias: TypeAlias = 'str | int'

#####  Package Variables  #####

#The great thing about package-level dictionaries is their global (public-like)
#capability, avoiding constant passing down to 'lower' defs. 
#Static data only, no file objects or similar (or else!).
creds = {}
#These can be specified as POSIX style since the using call will normalize them.
default_params = {'cfg'       : 'config/config.json',
                  'cred'      : 'config/credentials.json',
                  'bot_token' : ''}
params = {}
PSB_version = '0.0.1'    
#This will be modified in the future to accept user-supplied paths.
#This file must be loaded prior to the logger to allow for user-provided
#options to be passed to the Logger.  Thus it must have special error
#handling outside of the logger class.
cfg_path = pl.Path(default_params['cfg'])

try:
    #The .absoltue call normalizes the path in case the user had slashing
    #issues.  Obviously can't solve all potential problems.
    with open(cfg_path.absolute()) as json_file:
        params = json.load(json_file)

except OSError as err:
    print(f"Can't load the config file from path: {cred_path.absolute()}!")
    exit(-1)
        
job_queue = None
worker    = None

class PSBClient(dis.Client):
    def __init__(self, *, intents: dis.Intents):
        """This command copies the global command set to a given Guild instance.

            Input  : self - a reference to the current object.
                     intents - what Discord intents are required to run the bot.

            Output : None
        """
        self.disLog = log.getLogger('discord')
        self.disLog.debug(f"Intents are: {intents}")
        
        super().__init__(intents=intents)
        self.tree = dac.CommandTree(self)

    async def setup_hook(self):
        """Copies the global command set to a given Guild instance.

            Input  : self - a reference to the current object.

            Output : None
        """
        
        #Replies should be managed in a separate task to allow the main UI to
        #always be responsive, and allow the backend to process work independent
        #of message posting.  It's more efficent and better separated.
        self.loop = asy.get_running_loop()
        
        self.disLog.debug(f"Syncing Guild Tree to Global.")
        
        await self.tree.sync()
        
    def GetLoop(self):
        """Returns a reference to this client's asyncio event loop.

            Input  : self - a reference to the current object.

            Output : loop - the client's event loop.
        """
        return self.loop;

intents = dis.Intents.default()
PSB_client = PSBClient(intents=intents)

#####  Package Functions  #####

@PSB_client.event
async def on_ready():
    global job_queue
    global worker
    
        
    queLog = log.getLogger('queue')
    queLog.setLevel(params['log_lvl'])
    log_path = pl.Path(params['log_name_queue'])

    logHandler = lh.RotatingFileHandler(
        filename=log_path.absolute(),
        encoding=params['log_encoding'],
        maxBytes=int(params['max_bytes']),
        backupCount=int(params['log_file_cnt']),
    )
    
    formatter = log.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', 
        params['date_fmt'],
        style='{'
    )
    logHandler.setFormatter(formatter)
    queLog.addHandler(logHandler)
    queLog.info(f'Logged in as {PSB_client.user} (ID: {PSB_client.user.id})')
    
    queLog.debug(f"Creating Queue Manager.")
    job_queue = qm.Manager(loop=PSB_client.GetLoop(),
                           manager_id=1,
                           opts=params['queue_opts'])
    worker    = th.Thread(target=job_queue.PutRequest,
                          name="Queue mgr",
                          daemon=True)
    worker.start()
    
    print('------')

#####  Helper Classes  #####

class TimeTransformer(dac.Transformer):
    async def transform(self, interaction: dis.Interaction, input: str) -> dt.time:
        common_time  = re.compile(" *[0-9]{1,2} *: *[0-9]{1,2} *[ap]m")
        common_match = common_time.fullmatch(input)
        disLog       = log.getLogger('discord')
        mil_time     = re.compile(" *[0-9]{1,2} *: *[0-9]{1,2} *")
        mil_match    = mil_time.fullmatch(input)
        time         = None
        
        disLog.debug(f"Time transform parameters are: {input} {common_match} {mil_match}.")
        
        try:
            #These are split into full subsections in case it becomes necessary
            #to parse common and mil time differently.
            if common_match != None :
            
                parts = input.replace(" ","").split(":")
                parts[0] = int(parts[0]) + 12 if parts[1][-2:] == "pm" else parts[0]

                if int(parts[0])      < 25 and int(parts[0])      >= 0 and \
                   int(parts[1][:-2]) < 61 and int(parts[1][:-2]) >= 0 :
                   
                    time  = dt.time(hour=int(parts[0]), minute=int(parts[1][:-2]))
                
            elif  mil_match != None :
            
                parts = input.replace(" ","").split(":")
                disLog.debug(f"Mil time parts are: {parts}")

                if int(parts[0]) < 25 and int(parts[0]) >= 0 and \
                   int(parts[1]) < 61 and int(parts[1]) >= 0 :
                   
                    time  = dt.time(hour=int(parts[0]), minute=int(parts[1]))
        except Exception as err:
            disLog.warn(f"Exception processing invalid time string {input}, {err}.")
        
        disLog.debug(f"Time returned was {time}.")
        return time


#####  Commands #####

@PSB_client.tree.command(name="hello",
                         description=f"A basic test ping message.")
async def hello(interaction: dis.Interaction):
    """A test echo command to verify basic discord functionality.

       Input  : None.

       Output : None.
    """
    await interaction.response.send_message(f'Hi, {interaction.user.mention}', ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="init",
                         description=f"Creates a Schedule.")
@dac.describe(schedule=f"An optional name for a schedule or an existing channel to use for the schedule.  Defaults to 'new_schedule' in the current channel.")
async def init(interaction: dis.Interaction,
               schedule : Optional[dac.Range[str, 0, 100]] = "new_schedule"): #Discord channel names are limited to 100 characters.
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    
    if (schedule == str):
        message = f"Using current channel to create the schedule {schedule}"
    else:
        message = f"Using the channel {schedule} to create a schedule named 'new_schedule'"
    
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)
    
@PSB_client.tree.command(name="edit",
                         description="Update an event's contents.")
@dac.describe()
async def edit(interaction: dis.Interaction,
               start        : Optional[dac.Transform[str, TimeTransformer]] = None,
               end          : Optional[dac.Transform[str, TimeTransformer]] = None,
               title        : Optional[dac.Range[str, 0, 100]] = "new_schedule",
               comment      : Optional[str] = None, #Comment Transformer
               date         : Optional[str] = "new_schedule", #Date Transformer
               start_date   : Optional[str] = "new_schedule", #Date Transformer
               end_date     : Optional[str] = "new_schedule", #Date Transformer
               repeat       : Optional[str] = "new_schedule", #Weekday Transformer (list of days)
               url          : Optional[dac.Range[str, 0, 1024]] = None,
               quiet_start  : Optional[bool] = None,
               quiet_end    : Optional[bool] = None,
               quiet_remind : Optional[bool] = None,
               expire       : Optional[str] = "new_schedule", #Date Transformer
               deadline     : Optional[str] = "new_schedule", #Date Transformer
               count        : Optional[dac.Range[int, -(pow(2,53) - 1), (pow(2,53) - 1)]] = "new_schedule",
               limit        : Optional[str] = None): #Limit Transformer
    """
       Input  : None.

       Output : None.
    """
    #Transformer for dates for input validation and conversion into ISODate for GC
    #https://discordpy.readthedocs.io/en/stable/interactions/api.html?highlight=app_command%20range#discord.app_commands.Transformer
    #TODO: Complete command processing.
    message= "tbd to make discord happy {start}"
    await interaction.response.send_message(message, ephemeral=bool(params['delete_cmds']), delete_after=9.0)
    
@PSB_client.tree.command(name="tbd1",description="TBD")
@dac.describe()
async def delete(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd2",description="TBD")
@dac.describe()
async def guild(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd3",description="TBD")
@dac.describe()
async def create(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd4",description="TBD")
@dac.describe()
async def config(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd5",description="TBD")
@dac.describe()
async def purge(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd6",description="TBD")
@dac.describe()
async def list(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd7",description="TBD")
@dac.describe()
async def help(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd8",description="TBD")
@dac.describe()
async def schedules(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd9",description="TBD")
@dac.describe()
async def events(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd10",description="TBD")
@dac.describe()
async def sync(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd11",description="TBD")
@dac.describe()
async def oauth(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd12",description="TBD")
@dac.describe()
async def test(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd13",description="TBD")
@dac.describe()
async def skip(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd14",description="TBD")
@dac.describe()
async def sort(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd15",description="TBD")
@dac.describe()
async def zones(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd16",description="TBD")
@dac.describe()
async def manage(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd17",description="TBD")
@dac.describe()
async def diagnose(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)

@PSB_client.tree.command(name="tbd18",description="TBD")
@dac.describe()
async def announcements(interaction: dis.Interaction):
    """

       Input  : None.

       Output : None.
    """
    #TODO: Complete command processing.
    message= ""
    await interaction.response.send_message(message, ephemeral=params['delete_cmds'], delete_after=9.0)


#####  main  #####

def Startup():
    """Updates the global dictionary with the supplied configuration, if it
       exists, and starts the program.

       Input : None (yet).

       Output : None.
    """
    global params
    global creds
    global job_queue
        
    disLog = log.getLogger('discord')
    disLog.setLevel(params['log_lvl'])
    log_path = pl.Path(params['log_name'])

    logHandler = lh.RotatingFileHandler(
        filename=log_path.absolute(),
        encoding=params['log_encoding'],
        maxBytes=int(params['max_bytes']),
        backupCount=int(params['log_file_cnt']),
    )
    
    formatter = log.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', 
        params['date_fmt'],
        style='{'
    )
    logHandler.setFormatter(formatter)
    disLog.addHandler(logHandler)
    
    #This will be modified in the future to accept user-supplied paths.
    try:
        cred_path = pl.Path(default_params['cred'])
        
        with open(cred_path.absolute()) as json_file:
            creds = json.load(json_file)

    except OSError as err:
        disLog.critical(f"Can't load file from path {cred_path.absolute()}")
        exit(-2)
    
    #Start manager tasks
    disLog.debug(f"Starting Bot client")
    
    try:
        PSB_client.run(creds['bot_token'])
    except Exception as err:
        disLog.error(f"Caught exception {err} when trying to run the PSB client!")


if __name__ == '__main__':
    Startup()