#Manages user requests through Discord to generate images with a Stable
#Diffusion model filepath supplied in the config.json file.  Cannot prevent
#Specific types of images, like NSFW, from being generated.


#####  Imports  #####

import asyncio as asy
import base64 as b64
import discord as dis
from discord import app_commands as dac
import io
import logging as log
import logging.handlers as lh
import json
import multiprocessing as mp
import os
import pathlib as pl
import src.managers.QueueMgr as qm
import threading as th
import time
from typing import Literal, Optional

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
    
@PSB_client.tree.command()
async def hello(interaction: dis.Interaction):
    """A test echo command to verify basic discord functionality.

       Input  : None.

       Output : None.
    """
    await interaction.response.send_message(f'Hi, {interaction.user.mention}', ephemeral=True, delete_after=9.0)



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
        print(f"creds: {creds['bot_token']}")
        PSB_client.run(creds['bot_token'])
    except Exception as err:
        disLog.error(f"Caught exception {err} when trying to run the PSB client!")


if __name__ == '__main__':
    Startup()