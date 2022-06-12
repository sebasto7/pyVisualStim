#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This module contains global variables.

.. data:: FRAMERATE
    The refresh rate of your monitor. Check PC monitor settings
.. data:: MAXRUNTIME
    By defaul 3600 seconds (60 mnin). Global time. Total duration of a recording.
    If this is exceded, stimulus presentation stops.
.. data:: COUNTER_CHANEL
    Where to read the counter of scanned frames from the microscope to the NI-DAQ
.. data:: PULSE_CHANNEL
    Where to send the trigger from the NI-DAQ to the microscope for start scanning
.. data:: MAXRATE
.. data:: OUT_DIR
    Directory for the stimulus output files
    
.. data:: OUT_DIR
    Directory for the stimulus output files
    
.. data:: VIEWPOS_FILE
    Txt file if the size (x and y) and the position of the screen
    
.. data:: SEED
    Seed number to be used in some pseudorandomization process in the main code

"""
OUT_DIR = r'C:\Users\smolina\2pstim OutputFiles' 
#OUT_DIR = r'\\fs02\smolina$\Dokumente\2pstim OutputFiles' # Different in each PC
# OUT_DIR = r'C:\Users\aito\Documents\2pstim OutputFiles' # Sebastian's laptop
# OUT_DIR = r'C:\Users\sebas\OneDrive\Dokumente\2pstim OutputFiles' 

MY_ID = 'seb'
MAINFILE_NAME = "_main_booleans"
OUTFILE_NAME = "_stimulus_output"

FRAMERATE = 60 # 100 for office monitor. 60 for laptop
MAXRUNTIME = 3600
DISTANCE = 5.36  # Distance of the fly to the screen
SCREEN_WIDTH = 9
SEED = 54378  # To keep reproducibility among experiments >> DO NOT CHANGE this SEED number: 54378

# For NIDAQ configuration
COUNTER_CHANNEL = "Dev2/ctr1"
PULSE_CHANNEL = "Dev2/ctr0"  # Consider using not a counter but digital mode 'port1/line0' (digital channel)
MAXRATE = 10000.0

# Viewpositions

VIEWPOS_FILE = 'viewpositions.txt'
