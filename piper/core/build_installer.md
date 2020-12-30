**Requires:**  
* Python 3.7  
* pyinstaller  

**Build Command(s):**  
cd piper  
pyinstaller "build_installer.py" --console --onefile --name installer

**NOTE:**  
Make sure to move installer.exe out of the "dist" directory it builds in, and into the parent directory, piper.