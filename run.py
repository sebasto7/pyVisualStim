#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'\\fs02\smolina$\Dokumente\GitHub\2pstim\twopstim') # It must be change for the path where the code is in each PC
# sys.path.insert(0, r'C:\Users\aito\Documents\GitHub\2pstim\twopstim') # Sebastian's laptop
# sys.path.insert(0, r'C:\Users\sebas\OneDrive\Dokumente\GitHub\2pstim\twopstim') 

import pyVisualStim
from psychopy import gui

file_path = gui.fileOpenDlg('./pyVisualStim/stimuli')

# Execute
pyVisualStim.main(file_path[0])


