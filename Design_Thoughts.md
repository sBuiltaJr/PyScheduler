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
