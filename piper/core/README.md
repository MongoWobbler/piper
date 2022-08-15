# piper.core

All files in piper.core are meant to be DCC agnostic. Therefore, scripts in piper.core  must not import any DCC API, and only use python standard library and contents found in piper. 

## Building the Piper Installer

**Requires:**  
* [Python 3.7.7 (Same as Maya 2022, otherwise maya.standalone fails)](https://www.python.org/downloads/release/python-379/)  
* [PyInstaller](https://www.pyinstaller.org/)
* [PySide2](https://pypi.org/project/PySide2/)

**Build Command(s):**
```  
cd piper  
pyinstaller --clean --distpath "./" build_piper_installer.spec
```
Alternatively, run [build_piper_installer.bat](https://github.com/MongoWobbler/piper/blob/master/build_piper_installer.bat) that comes in the piper directory to generate piper_installer.exe :)
