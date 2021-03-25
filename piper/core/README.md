##Building the Piper Installer

**Requires:**  
* [Python 3.7](https://www.python.org/downloads/release/python-379/)  
* [pyinstaller](https://www.pyinstaller.org/)  

**Build Command(s):**
```  
cd piper  
pyinstaller "build_piper_installer.py" --console --onefile --name piper_installer
```

**NOTE:**  
Make sure to move piper_installer.exe out of the "dist" directory it builds in, and into the parent directory, piper.
