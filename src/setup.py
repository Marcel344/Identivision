"""
This is a setup.py script generated by py2applet

Usage:
    python3 setup.py py2app -A
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = ['myModel.py','modelThread.py','loadModelsThread.py','WebCamThread.py','IGWebScraperThread.py','FBWebScraperThread.py','cleanDataThread.py','batteryGraphThread.py','DroneThread.py','identivisionLogo.mp4','main.ui','instagram.ui']
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
