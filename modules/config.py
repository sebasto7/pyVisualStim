#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module contains global variables.

.. data:: MY_ID
    User identification
.. data:: OUT_DIR
    Directory for the stimulus output files
    
.. data:: MAINFILE_NAME
    Name for the metadata outputfile
.. data:: OUTFILE_NAME
    Name fo the data outputfile

.. data:: FRAMERATE
    The refresh rate of your monitor. Check PC monitor settings
.. data:: DISTANCE
    Distance from the viewer to the screen
.. data:: SCREEN_WIDTH
    Width of the projection are of the screen
.. data:: VIEWPOS_FILE
    Txt file if the size (x and y) and the position of the screen

    
.. data:: MAXRUNTIME
    By defaul 3600 seconds (60 mnin). Global time. Total duration of a recording.
    If this is exceded, stimulus presentation stops.
.. data:: SEED
    Seed number to be used in some pseudorandomization process in the main code
    
.. data:: COUNTER_CHANEL
    Where to read the counter of scanned frames from the microscope to the NI-DAQ
.. data:: PULSE_CHANNEL
    Where to send the trigger from the NI-DAQ to the microscope for start scanning


"""
# For user configuration
MY_ID = 'seb'
EXP_NAME = 'Input the experiment name'
OUT_DIR = r'U:\Dokumente\GitHub\pyVisualStim' 

# For output file configutation
MAINFILE_NAME = "_meta_data"
OUTFILE_NAME = "_stimulus_output"

# For screen configuration
FRAMERATE = 60# Check refresh rate of your screen (here, PC monitor or projector)
DISTANCE = 6# Distance of the fly to the screen, For dlp 90deg: 5 cm, For ASUS monitor: 10, For dlp 45deg: ? (5.36?)
SCREEN_WIDTH = 20 # Width of the window's projection area, For dlp 90deg: 12, For ASUS monitor: 30,  For dlp 45deg: ? (9?)
VIEWPOS_FILE = r'U:\Dokumente\GitHub\pyVisualStim\viewpositions.txt' # Contains window' size and position on the screen


# Other configurations
MAXRUNTIME = 3600
SEED = 54378  # To keep reproducibility among experiments >> DO NOT CHANGE this SEED number: (54378, original from 2020)

# For NIDAQ configuration
COUNTER_CHANNEL = "Dev1/ctr1" # or "Dev2/ctr1"
PULSE_CHANNEL = "Dev1/ctr0"  #or "Dev2/ctr0". Consider using not a counter but digital mode 'port1/line0' (digital channel)
MAXRATE = 10000.0 # Seb, currently unused



