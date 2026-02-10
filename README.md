## querymc
### Compatible with Java Edition (1.7+)
### Only tested for Python 3.14

This is a python package for the minecraft java query protocol, which implements methods for the basic stat and full stat requests as described on [Minecraft Wiki](https://minecraft.wiki/w/Query) and returns the structured reply in a dictionary.
For access to e.g. a server icon you will need to use the [Server List Ping](https://minecraft.wiki/w/Java_Edition_protocol/Server_List_Ping), which is NOT part of this module. 

You may be interested in [mcstatus](https://github.com/py-mine/mcstatus) if you want complete functionality across versions.

## Installation
Querymc is available on [PyPi](https://pypi.org/project/querymc/) and can be installed with:
```bash
python3 -m pip install mcstatus
```