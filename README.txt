FrITA is the Free Interactive Text Aligner.

Copyright Gregory Vigo Torres, 2013
All code included in this software distribution, unless indicated otherwise, is licensed under the GPL v. 3.

This readme is for the FrITA demo release. 

RELEASE NOTES
THIS IS A DEMO RELEASE!
This release is full of bugs and a number of other issues that will be resolved in later releases. 
However, basic features (import a couple of files and generate a .tmx) work in Debian 7, Linux Mint and Windows 7. 
The purpose of this release is simply to show that the application exists and generally present my intentions 
for what I think a free aligner should be like.

ROADMAP
-Short term
Use PySide instead of PyQt.
Major refactoring/restructuring of code.
Remedy some GUI bugs.
Improve performance with large files.

DEPENDENCIES
You MUST have:
    Python 3 or higher
    PyQT 4.8 or higher (This implies Qt.)
And:
    LXML is suggested for improving .docx support but it's not required. 
    See the lxml website (http://lxml.de/) for installation instructions.

    I recommend using your distro's package manager to install the dependencies (apt-get, synaptic etc.).
    Or,
    You can download the latest version of PyQt from: http://www.riverbankcomputing.com/software/pyqt/intro
    You can download the latest version of Python from: http://python.org/

    Make sure you have the dependencies installed for the Python3 installation you'll be using for FrITA. 

INSTALLATION
    There is currently no installer, but being as FrITA is written entirely in Python, there's not much to install.
    There is an icon called app_icon.svg in the icons directory that you can use for launchers and things.

    After you have all the dependencies installed:

    Linux:
        You need to copy the .frita_conf directory and ALL its contents (the segmentation rules) into your home directory.
        You may need to change the permissions of the main.py to executable (755).

    Windows:
        Aside from Linux, FrITA has only been tested in Windows 7. 
        You need to copy the entire .frita_conf folder and its contents to your USER folder, 
        C:\\Users\"YOUR USER FOLDER"\ .frita_conf.

    Mac
        FrITA has not yet been tested on a Mac, but it should work. 
        The only thing that should need to be done is to .frita_conf directory and its contents to your home directory.
        You may have to change the file permissions of main.py to executable.

USAGE
    Linux
        To start FrITA in Linux execute main.py, which can be found in the source directory. 
        The script uses /usr/bin/env python3, if you have issues with Python versions either change the first line
        or execute main.py directly with Python 3: e.g. python3.3 main.py.

    Windows
        To start FrITA in Windows you should just be able to execute main.py (in the FrITA source directory) with Python 3.

    Mac:
        As of this release, FrITA has not been tested on a Mac. However, it should work by just executing main.py with Python 3.
