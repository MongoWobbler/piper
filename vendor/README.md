# Vendor

First of all, [what is vendoring???](https://stackoverflow.com/questions/26217488/what-is-vendoring)  
So with that out of the way, piper uses vendoring since it is meant to be a "batteries included" type of package instead of relying on external dependency managers.

***

Vendor files are split by supported python versions. py2 for Python 2.7, py3 for python 3.7 (mostly), and pyx for vendors that support all versions.

**NOTE**: Each vendor directory must be registered in [piper_config.py](https://github.com/MongoWobbler/piper/blob/master/piper_config.py) in order for them to be added to the sys.path!

Vendor path is added to sys.path inside the DCC's setup.py script, below are a couple of examples.

[Maya](https://github.com/MongoWobbler/piper/blob/master/maya/scripts/setup.py)  
[Houdini](https://github.com/MongoWobbler/piper/blob/master/houdini/python2.7libs/setup.py)

***

If some vendors are missing, make sure submodules have been initiated correctly.

```
cd piper/vendor/pyx
git submodule init
git submodule update
```
