# REQUIRES:
#       CMAKE
#       Visual Studio 2017, 2019, or 2022 depending on version
#
# STEPS:
# 1. Clean the piper/maya/cpp directory to remove all build files from previous builds
#       cd piper/maya/cpp
#       git clean -d -f -x
#
# 2. To build visual studio project:
#       cd piper/maya/cpp
#       cmake -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=2020 ./Source
#       cmake -G "Visual Studio 16 2019" -A x64 -DMAYA_VERSION=2022 ./Source
#       cmake -G "Visual Studio 16 2019" -A x64 -DMAYA_VERSION=2023 ./Source
#       cmake -G "Visual Studio 17 2022" -A x64 -DMAYA_VERSION=2024 ./Source
#
# 3. Once that is done, you can build the .mll by running the following:
#       cd piper/maya/cpp
#       cmake --build . --config Release

cmake_minimum_required(VERSION 3.21)
project(Piper)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/Modules)

# the line below might need to be removed for a cmake only build. Was added to make CLION happy.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake/Modules")

set(SOURCE_FILES
        "MainPlugin.cpp"
        "PiperTransforms.cpp"
        "PiperTransforms.h"
        "PiperIK.cpp"
        "PiperIK.h"
        "PiperFK.cpp"
        "PiperFK.h"
        "util.h"
        "TensionNode.cpp"
        "TensionNode.h"
        "PiperFK.cpp"
        "PiperFK.h"
        "PiperMath.cpp"
        "PiperMath.h"
        "SwingTwistNode.cpp"
        "SwingTwistNode.h")

# uncomment with correct maya version when developing in CLion to have cmake find correct maya version
# set(MAYA_VERSION 2023)

find_package(Maya REQUIRED)

add_library(Piper SHARED ${SOURCE_FILES})
target_link_libraries(Piper PRIVATE Maya::Maya)
target_include_directories(Piper PRIVATE Maya::Maya)

MAYA_PLUGIN(Piper)
