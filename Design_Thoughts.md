# Sharding:
- Use the [API](https://discordpy.readthedocs.io/en/latest/api.html#discord.AutoShardedClient) To spawn across hosts.
- Have a total limit, as assigned by Discord.
- Have to manually allocate shard ranges across this limit.
- Shared file/splitting probably best; JSON file at start?
- Be wary of guild timeouts.

# Databases
- Meant as self-host
- Switch to MongoDB for easier python integration
- No real need for the relational behavior.
- Adds dependnecies to the python driver [PyMong](https://pymongo.readthedocs.io/en/stable/index.html)
- Relational table structure jstu unnecessary and burdensome
- Easier to make mongo users for self-hosting.

# Invites
- Could theoretically track user who invited bot, but requries guild management permissions (should be denied by a reasonable user).
- Instead can check user permissions from context in [discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=message%20context#discord.ext.commands.Context.permissions)
- Need to verify [MANAGE_CHANNELS](https://discord.com/developers/docs/topics/permissions) at a minimum to create new bot account.
- Have init just take a channel name from anywhere, verify user's permissions.
- Optional argument to designate (even an existing) channel, default = default channel name.
