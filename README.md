# piper
A rig, a pipe, and a scripter walk into a bar...

This repo is **currently under development**, feel free to peruse for updates or cool functions/ideas.
Tools are biased towards Maya and Unreal Engine.

[Follow production status by clicking this link](https://github.com/users/MongoWobbler/projects/1)

## Installing  

Run **piper_installer.exe** to add files that allow the user's currently installed Digital Content Creation (DCC) packages to know about piper.
See, **Building the Piper Installer** below if piper_installer.exe is missing.

The **piper_installer.exe** will create the following files for all versions of the following DCCs installed.  

Maya:
 - USER/Documents/maya/VERSION/modules/piper.mod

Houdini:
 - USER/Documents/houdiniVERSION/packages/piper.json

Unreal:
 - PROJECT/Plugins/Piper (Symlink)
  
## Building the Piper Installer

**Requires:**  
* [Python 3.10.8 (Same as latest Maya version (2024), otherwise maya.standalone fails)](https://www.python.org/downloads/release/python-3108/)  
* [PyInstaller](https://www.pyinstaller.org/)
* [PySide2](https://pypi.org/project/PySide2/)

Run [build_piper_installer.bat](https://github.com/MongoWobbler/piper/blob/master/build_piper_installer.bat) to generate piper_installer.exe

## Cloning Repository

If cloning repo, make sure to initiate and update submodules found in piper/vendor after cloning. Example below

```
cd piper/vendor/pyx
git submodule init
git submodule update
```  
Alternatively, clone, initiate, and update the repo and its submodules all in one line by running:
```
git clone --recurse-submodules -j8 https://github.com/MongoWobbler/piper.git
```

## Supported

- Windows
- Maya 2022 to 2024
- Houdini 18.5 to 19.5
- Unreal Engine 5
