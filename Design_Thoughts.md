# Sharding:
- Use the [API](https://discordpy.readthedocs.io/en/latest/api.html#discord.AutoShardedClient) To spawn across hosts.
- Have a total limit, as assigned by Discord.
- Have to manually allocate shard ranges across this limit.
- Shared file/splitting probably best; JSON file at start?
- Be wary of guild timeouts.

# Databases
- Meant as self-host
- Don't see need for mongoDB's noSQL capabilities.
- Won't be merging databases or failing shards over, probably.
- Can worry about that if I ever get there.
- Stick MariaDB for now to focus on self-hosts.
- Maria does need sudo login/setup and table create, comprimising with ssetup scripts for now.
- Also [maria can store JSON data](https://mariadb.com/resources/blog/using-json-in-mariadb/), so the calendar/event tables are easy enough to generate.

# Invites
- Could theoretically track user who invited bot, but requries guild management permissions (should be denied by a reasonable user).
- Instead can check user permissions from context in [discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=message%20context#discord.ext.commands.Context.permissions)
- Need to verify [MANAGE_CHANNELS](https://discord.com/developers/docs/topics/permissions) at a minimum to create new bot account.
- Have init just take a channel name from anywhere, verify user's permissions.
- Optional argument to designate (even an existing) channel, default = default channel name.
