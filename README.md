# PyScheduler
A Discord scheduling bot with reminders and Google Calendar integration. In the
spirit of Saber.

PyScheduler manages events, created from either a dedicated Discord channel in
the server or a specified Google Calendar, and posts them to Discord.  The bot
can send reminders, manage sign-ups, and automatically post, cancel, and remind
events.  It has permission control and configurable udpate and posting ranges.
By default, PyScheduler will display events up to a week in advance of their
scheduled date, and update the coutndowns hourly.

# Dependencies
- Python 3.10 or newer (for encoding handling)

PyScheduler is a cross-platform python 3.10.x project.
While intended to be portable, older versions will not be expressly supported.

## Self-Hosting
PyScheduler can be self-hosted with the following dependencies:
- Python 3.10 (for encoding handling)
- mongoDB 6.0 (older versions/other DBs may work)
- Pip 22.0.2
- Discord.py 2.0.1
- PyMongo 4.2.0

Newer versions of the above may also work. 

The following OS's have been tested for self hosting:
- Windows 10 21H2
- Debian 12 Bookworm
- Ubuntu 20.04
- MacOS Monterey 12.5.1

Other OS's are not expressly supported and no effort will be made into porting
to them.

## License
PyScheduler (and all flies in the PyScheduler repo) fall under the [GPLv3](LICENSE.md).
Other components, such as the dependency packages, are covered by their respective licenses.

# Usage
PyScheduler is invoked directly via command-line:
```
python3 PyScheduler.py
```

## Limitations/Known Issues
Also see the [changelog](CHANGELOG.md).
- Discord only allows a maximum number of emotes to be attached to a single
  post; limiting signup types for a single event.
