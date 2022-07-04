#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, r'\\fs02\smolina$\Dokumente\GitHub\pyVisualStim\pyVisualStim') # It must be change for the path where the code is in each PC

import pyVisualStim
from psychopy import gui

file_path = gui.fileOpenDlg('./pyVisualStim/stimuli')

# Execute
pyVisualStim.main(file_path[0])


