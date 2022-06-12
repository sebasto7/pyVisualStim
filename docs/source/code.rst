Documentation for the Code
**************************

Run
===

Run the ``run.py`` script in PsychoPy. It is located in the top ``twopstim`` folder.

.. code-block:: python

    import twopstim
    from psychopy import gui

    file_path = gui.fileOpenDlg('./twopstim/stimuli')

    # Execute
    twopstim.main(file_path[0], testmode)
    

Main
====

.. automodule:: twopstim
    :members:
.. autofunction:: main

.. note::
    Run without DLP, if you test the stimulus. In this mode, the stimulus' MAXRUNTIME will be ignored
    and the microscope's frame recording won't be checked.
    
Helper
======

.. automodule:: twopstim.helper
    :members:

Exceptions
==========

.. automodule:: twopstim.exceptions
    :members:

Config
======

.. automodule:: twopstim.config
    :members:
