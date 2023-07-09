# Building Maya Plug-in

## REQUIRES:
- CMAKE
- Visual Studio 2017, 2019, or 2022 depending on version

## STEPS:
1. Clean the `piper/maya/cpp` directory to remove all build files from previous builds
```
cd piper/maya/cpp
git clean -d -f -x
```   
2. To build visual studio project, use the command based on the version you want to build:
```
cd piper/maya/cpp
cmake -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=2020 ./Source
cmake -G "Visual Studio 16 2019" -A x64 -DMAYA_VERSION=2022 ./Source
cmake -G "Visual Studio 16 2019" -A x64 -DMAYA_VERSION=2023 ./Source
cmake -G "Visual Studio 17 2022" -A x64 -DMAYA_VERSION=2024 ./Source
```
3. Once that is done, you can build the `.mll` by running the following:
```
cd piper/maya/cpp
cmake --build . --config Release
```
