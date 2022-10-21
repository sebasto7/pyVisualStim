#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'C:\Users\vargasju\PhD\experiments\2p\Juan_stimuli') # It must be change for the path where the code is in each PC
sys.path.insert(0, r'U:\Dokumente\GitHub\pyVisualStim\modules') 


import modules
from psychopy import gui

file_path = gui.fileOpenDlg('./pyVisualStim/stimuli')

# Execute
modules.main(file_path[0],subwindow=True)


