# piper.core

All files in piper.core are meant to be DCC agnostic. Therefore, scripts in piper.core  must not import any DCC API, and only use python standard library and contents found in piper. 

## Building the Piper Installer

**Requires:**  
* [Python 3.7](https://www.python.org/downloads/release/python-379/)  
* [pyinstaller](https://www.pyinstaller.org/)  

**Build Command(s):**
```  
cd piper  
pyinstaller "build_piper_installer.py" --clean --distpath "./" --console --onefile --name piper_installer
```
Alternatively, run build_piper_installer.bat that comes in the piper directory :)
