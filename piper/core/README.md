##Building the Piper Installer

**Requires:**  
* [Python 3.7](https://www.python.org/downloads/release/python-379/)  
* [pyinstaller](https://www.pyinstaller.org/)  

**Build Command(s):**
```  
cd piper  
pyinstaller "build_piper_installer.py" --clean --distpath "./" --console --onefile --name piper_installer
```
Alternatively, run build_piper_installer.bat that comes in the piper directory :)
