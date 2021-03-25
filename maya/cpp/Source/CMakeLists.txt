# REQUIRES:
#       CMAKE
#       Visual Studio 2017 or Visual Studio 2019 depending on version
#
# To build visual studio project:
#       cd piper/maya/cpp
#       cmake -G "Visual Studio 15 2017 Win64" -DMAYA_VERSION=2020 ./Source
#       cmake -G "Visual Studio 16 2019" -A x64 -DMAYA_VERSION=2022 ./Source
#
# Once that is done, you can build the .mll by running the following:
#       cd piper/maya/cpp
#       cmake --build . --config Release

cmake_minimum_required(VERSION 3.1)
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
        "util.h"
        "TensionNode.cpp"
        "TensionNode.h"
        )

find_package(Maya REQUIRED)

add_library(Piper SHARED ${SOURCE_FILES})
target_link_libraries(Piper PRIVATE Maya::Maya)
target_include_directories(Piper PRIVATE Maya::Maya)

MAYA_PLUGIN(Piper)
