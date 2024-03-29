#Manages the job queue for processing PSB commands. Also handles rate limits
#and other checks, including tracking guilds.
#
#A seaprate manager is reqruied by Discord because all slash commands have a
#hard 3-second timeout.  Even modern HW is not yet able to meet this demand.


#####  Imports  #####

import logging as log
import multiprocessing as mp
import queue
import requests as req
import time

jobs = {}


#####  Package Functions  #####

#####  Manager Class  #####

class Manager:

    def __init__(self, loop, manager_id: int, opts: dict):
        """Manages job request queueing and tracks relevant discord context,
           such as poster, Guild, channel, etc.  The Manager gets this from the
           caller so different Managers could have different settings.

           Input: self - Pointer to the current object instance.
                  loop - The asyncio event loop this manager posts to.
                  manager_id - The current Manager's ID, assigned by the caller.
                  opts - A dictionary of configurable options.
              
           Output: None - Throws exceptions on error.
        """
        self.flush      = False
        self.id         = manager_id
        self.keep_going = True
        self.flush      = False
        self.post_loop  = loop
        self.queLog     = log.getLogger('queue')
        #It's possible all opts are provided directly from config.json,
        #requiring them to be cast appropriately for the manager.  This also
        #allows the caller to never have to worry about casting the types
        #correctly for a config file and definition it doesn't own.
        self.depth          = int(opts['depth'])
        self.max_guilds     = int(opts['max_guilds'])
        self.max_guild_reqs = int(opts['max_guild_reqs'])
        
        #This may eventually be implemented as a concurrent futures ProcessPool
        #to allow future versions to invoke workers across computers (e.g.
        #subprocess_exec with TCP/UDP data to/from a set of remote terminals).
        self.queue = mp.Queue(self.depth)

    def Flush(self):
        """Sets the 'flush' flag true to enable the job queue to flush jobs
           when able.  

           Input: self - Pointer to the current object instance.
              
           Output: none.
        """
        self.flush = True
        
    def Add(self, request : dict) -> str:
        """Passes queued jobs to the worker tasks.  Is effectively the 'main'
           of the class.  Workers return the image prompt and queue object id
           when complete.  The Manager should post the result to the main thread
           via a pipe to allow simultaneous handling of commands and responses.

           Input: self - Pointer to the current object instance.
                  request - Sanitized data to potentially add to the queue.
              
           Output: str - Result of the job scheduling attempt.
        """
        global jobs
        
        if request['data']['guild'] not in jobs:
        
            if len(jobs) >= self.max_guilds :
            
                self.queLog.warning(f"Trying to add guild {request['data']['guild']} goes over Guild limit {self.max_guilds}!")
                return "Bot is currently servicing the maximum number of allowed Guilds."
                
            else:
                #Asyncio and Threading are suppose to be GIL safe, making this
                #safe.  Change this if that changes.
                jobs[request['data']['guild']] = {}
        
        #This is a form of rate-limiting; limiting a guild to X posts instead
        #of attempting to track timing.
        if len(jobs[request['data']['guild']]) >= self.max_guild_reqs:
        
            self.queLog.warning(f"User {request['data']['id']}'s request excedded the Guild request limit {self.max_guild_reqs}!")
            
            if len(jobs[request['data']['guild']]) == 0:
            
                del jobs[request['data']['guild']]
            
            return "Unable to add your job, too many requests from this Guild are already in the queue."
            
        #This isn't an elif to avoid duplicating the contents. ID is also only
        #deleted after the job is done, so this function always loses the race.
        if request['data']['id'] not in jobs[request['data']['guild']]:
        
            (jobs[request['data']['guild']])[request['data']['id']] = request['metadata']
            self.queLog.debug(f"Added new request from Guild {request['data']['guild']} to ID {request['data']['id']}.")
            
        else :
        
            self.queLog.debug(f"Request id {request['data']['id']} alraedy exists!")
            #In the future, this can be modified by converting ID into a
            #snowflake, allowing users to post multiple jobs.
            return "You already have a job on the queue, please wait until it's finished."
        
            #Else rate limit
        try:
            #The Metadata can't be pickeled, meaning we can only send data
            #through the queue.
            self.queue.put(request['data'])
            
        except queue.Full as err:
        
            (jobs[request['data']['guild']]).pop(request['data']['id'])
            self.queLog.warning(f" Encountered a full queue for request with metadata: {request['data']}, {err}!")
            
            return "The work queue is currently full, please wait a bit before making another request."
            
        except Exception as err:
        
            (jobs[request['data']['guild']]).pop(request['data']['id'])
            self.queLog.error(f" Unable to add job to queue for request with metadata: {request['data']}, {err}!")
            
            return "Unable to add your job to the queue.  Are you sending more than text and numbers?"
            
        return "Your job was added to the queue.  Please wait for it to finish before posting another."
    
    def GetDefaultJobData(self) -> dict:
        """Returns the default job settings that can be provided to an empty
           query (or to reinitialize an object).

           Input: None.

           Output: opts - a dictionary of the default queue arguments.
        """
        return {}
        
    def PutRequest(self) :
        """Should be instantiated as an independent proecss for putting and
           getting data from the SD server.  Results are provided back to the
           main IGSD thread via the supplied event loop.  Has no knowledge of
           Guilds or how to post the provided image to the requestor.

            Input: pipe - where to return the job result.
                  
            Output: None - Throws exceptions on error.
        """
        global jobs
        
        while self.keep_going:
        
            if self.flush:
#                self.queue.Flush()
                self.flush = False
                continue
            request            = self.queue.get()
            result             = {}
            jres               = {}
            
            #TODO: Add actual job code, mongodb and reading from Gooogle Calendar.
            
            jres['id']          = request['id'] #TODO this shouldn't be necessary
            #Pop last to ensure a new request from the same ID can be added
            #only after their first request is completed.
            job     = (jobs[request['guild']]).pop(request['id'])
            jres   |= job
            
            if len(jobs[request['guild']]) == 0:
            
                self.queLog.debug(f"Removing empty Guild {request['guild']} from the list.")
                del jobs[request['guild']]
                
            self.queLog.debug(f"Job Id {jres['id']} result was: {jres}")
            job['loop'].create_task(job['poster'](msg=jres), name="reply")
            
        return
        
    def Run(self):
        """Should spawn the process that puts job requests to the SD server.
           Is the freamework for multiple concurrent jobs, but will need to be
           modified to actually support them.

           Input: self - Pointer to the current object instance.
              
           Output: None - Results are posted to a pipe.
        """
        self.queLog.info(f"Queue Manager {self.id} starting workers.")
        #This may, someday, need to be a proper multiprocessing queue.
        #jobs = [QueueObject(x) for x in range(self.depth)], in a loop
