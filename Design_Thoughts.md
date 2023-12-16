# Sharding:
- Use the [API](https://discordpy.readthedocs.io/en/latest/api.html#discord.AutoShardedClient) To spawn across hosts.
- Have a total limit, as assigned by Discord.
- Have to manually allocate shard ranges across this limit.
- Shared file/splitting probably best; JSON file at start?
- All events posted to a queue for processing
    - rely on DB's handling to manage races (multiedit) if multiple queues are allowed.
	- Single handler queue per bot; slower but no race conditions.
	    - Will need to see how fine this is at scale.  Jobs should be quick?
		- Borrow IGSD's async setup sicne front-end is similar.
	- force sync command for using calendar so it doesn't get confused trying to autosync

# Databases
- Meant as self-host
- Switch to MongoDB for easier python integration
- No real need for the relational behavior.
- Adds dependnecies to the python driver [PyMong](https://pymongo.readthedocs.io/en/stable/index.html)
- Relational table structure just unnecessary and burdensome
- Easier to make mongo users for self-hosting.
- DBs are the source of truth for calendar events (sicne calendars are optional).


# Invites
- Could theoretically track user who invited bot, but requries guild management permissions (should be denied by a reasonable user).
- Instead can check user permissions from context in [discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=message%20context#discord.ext.commands.Context.permissions)
- Need to verify [MANAGE_CHANNELS](https://discord.com/developers/docs/topics/permissions) at a minimum to create new bot account.
- Have init just take a channel name from anywhere, verify user's permissions.
- Optional argument to designate (even an existing) channel, default = default channel name.

# Commands
- ephemeral note on posting.
- response on success?
    -  have to track origin; maybe just ping user like IGSD?
	- Maybe just post "command succ/fail <command>?
- One bot many channels: channels let users have different calendars with the same bot.


# Migration
- Need a tool/command to query existing Saber DB and extract info.
    - Can obviously just read calendar for Google Cal sync.
	