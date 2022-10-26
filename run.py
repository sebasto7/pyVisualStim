#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from modules import main
from psychopy import gui


#Coded being executed from the terminal
file_path = gui.fileOpenDlg('./stimuli_collection')
main(file_path[0])
