# PyScheduler
A Discord scheduling bot with reminders and Google Calendar integration.  In the spirit of Saber.

PySceduler manages events, createed from either a dedicated Discord channel in the server or a specified
Google Calendar, and posts them to Discord.  The bot can send reminders, manage sign-ups, and automatically
post, cancel, and remind events.  It has permission control and configurable udpate and posting ranges.
By default, PyScheduler will display events up to a week in advance of their scheduled date, and update the
coutndowns hourly.

PyScheduler 

# Dependencies
- Python 3.10 or newer (for encoding handling)


PyScheduler is a cross-platform python 3.x project, currently tested on python 3.10.4.
While intended to be portable, older versions will not be expressly supported.

## Self-Hosting
PyScheduler can be self-hosted with the following dependencies:
- Python 3.10 or newer (for encoding handling)
- mariadb 15.1 (older versions/other DBs may work)

The following OS's have been tested for self hosting:
- Windows 10 21H2
- Ubuntu 20.04
- Ubuntu 22.04
- MacOS Monterey 12.5.1

Other OS's are not expressly supported and no effort will be made into porting to them.

## License
PyScheduler (and all flies in the PyScheduler repo) fall under the [GPLv3](LICENSE.md)

# Usage
PyScheduler is invoked directly via command-line:
```
python3 PyScheduler.py
```

## Limitations/Known Issues
Also see the [changelog](CHANGELOG.md).
- Discord only allows a maximum number of emotes to be attached to a single post;
  limiting signup types for a single event.
- The bot command format will not work with versiosn of Discord older than the 9/1/2022 update.
- Discord's IRC format prevents displaying timezones matching your local computer's time,
  the bot must be set to a given timezone.
