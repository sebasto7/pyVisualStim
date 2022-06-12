Installation and Setup
======================

The recomended way to run an python application aided by `PsychoPy <http://www.psychopy.org/>`_
is, to install the standalone PsychoPy2 package. Additionally to the specific PsychoPy modules 
, you get an editor in which you can also execute the scripts. Then, copy the ``pyVisualStim``
modules to any location of your computer.

After the installation, it's necessary to set the PATH variable of **PsychoPy** and ``pyVisualStim`` in the system settings.
Add the path of your **PsychoPy** directory and also the path to the *python.exe*
executable to be able to run the ``python`` command in your shell.

Make sure you install *pip* to easily install additional python packages. Also 
add this to your PATH.

pip install PyDAQmx
Make sure PyDAQmx is in your PATH (check sys.path in the PsychoPy shell).

Alternatively you can install PyDAQmx manually by downloading the package, extract it, put it in the PsychoPy2 -> Lib -> site-packages
and then run ``python setup.py install`` from the command line in the PyDAQmx directory. Thus PyDAQmx resides in your site-packages folder
it's already in the PATH.

You will also need the NIDAQ (NI-MAX) software from National Instruments on your system and probably a simulated device (USB-6211).

Then, you need to change the output directory in the ``config.py`` of ``pyVisualStim``.

In the PsychoPy IDE you need to set your Monitor. Open the Monitor center, select ``testMonitor`` and configure your devices width, resolution and do a gamma callibration (more info soon).
At one point in the code a second monitor 'dlp' is used. Just create one dummy 'dlp' monitor in the PsychoPy monitor center, it's currently not needed to be correct.

Building an .exe from an PsychoPy script is possible, but not adviseable ( http://www.psychopy.org/recipes/appFromScript.html ), as for ex. the monitor center
won't be available.

The documentation is created by typing ``make html`` in the docs folder. Edit it via editing the .rst files.