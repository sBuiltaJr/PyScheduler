#Overview
This is a list of possible upgrades/updates that may be added to the project.  They're listed
here so as to not be forgotten.  No list is in priority order.


## Bug-fixes
(These items probably have higher implementation priority but aren't guaranteed to be first).

## Investigations
(Items that may not be bugs but should still be investigated)

## Planned
Fix the timezone display
- Discord supports a UTC convention that should work.
Custom user description for a channel.
- Theoretically easy.
- May need to stash calendar link elsewhere.
- Calendar link as a command?
- Should still default to old behavior.
Emote Limit Checking
- Current bot doesn't check for emote limits and can get banned for it.
- Need to have only 20 roles/19 emotes max (1 emote for cancel)
Import script
- Have to dump from !config.
- May need to be version-specific (or only support from version x).
Stored event configs
- Make a 'config' Collection tied to a calendar.
- Have option sets for different event configs that a user can save (like RSVP list).
- Can recall lists as a special argument into the create.
Sharding
- Project is mostly intended as shelf-host, but it should work.
- MongoDB already effectively supports shards.
- Basically need to specify which shard IDs the system uses as it boots.
- Probably a parameter to the top-level invocation, maybe a script wrapping it.

## Unplanned
Interchangeable Databases
Backup scripts
DB reconciliation
Identify inviter as schedule config
