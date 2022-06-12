
Done 
====

Main: Funktionen von 2pstim.cpp main():

	- DAQ Setup (ein Pulse und EdgeCounter)
		- Funktion: Experiment Start signal, sicherstellen dass das Mikroskop regelmäßig aufnimmt
		- Frage: Wann sendet das Mikroskop/ der Computer ein Edge den die NIDAQ Funktion aufnimmt (&data)?
	- Viewpositions einlesen -> Window mit Maßen erstellen
	- output file erstellen
	- Stimulus file einlesen -> in Dict speichern
	- main setup file schreiben
	- set coloring (background, getDLPcolor (gamma correction))
	
	- Loop experiment:
		- set epoch indices according to randomize
		- choose next epoch
		
		- draw chosen stimulus
			- make a shapestim
			- Cylinder Stripe

	- save out & main file
	- end NIDAQ tasks
	- stop
	
Cylinder Stripe:

	- pass window, shapestim, stimulus dictionary, timing, NIDAQ handle
	- change stimulus attributes according to epoch (TIME COSTLY)
	- present stimulus by frame
		- besonderheit: dies wird am Stück präsentiert, also rückkehr in main für output writeout/handling/... nicht möglich
	- draw
	- write output data, check NIDAQ data
 
config:

	- output directory
	- file names
	- maxruntime
	- framerate
	- channels nidaq
	- viewpositions file name

helper: 

	- read in funtions (viewpos file, stimfile)
	- make file funcitons (output, main booleans, )
	- randomize funcitons for epochs
	- color setting
	- gamma correction
	
run: just click "run" & everything will start up

Dokumentation 



ToDo
====

- PYTHON TIMING: There is still a delay when displaying a new epoch !!!
	- one could use 'element array stim' to speed up similar epochs in one stimuli
	- Or Write an easier stimulus function with less features

- FRUSTUM (3D) 
    - The problem is that we need a perspective correction for '3D effects'
    - here is the problem discussed: https://groups.google.com/forum/#!topic/psychopy-users/JrQy68EQyFU
    - one solution could be the Warper https://groups.google.com/forum/#!topic/psychopy-dev/cu9OAA1iWII but it's kinda slow and I guess we would need 
     to define an own warpfile. But maybe it will also work without a warpfile. Then we need to check if the perspective correction is correct.
    - antoher solution is to code an perspective correction unit function like degFlat and use it with addUnitTypeConversion(). Problem here:
        this is very weird, the new function is not recognized somehow and sometimes it creates more vertices than by the stimulus given (6 instead of 4??)
        another problem is that this transformation is applied before applying a rotation --> perspective correction wrong if stimulus rotated


- Do (gamma-) callibration on monitors. Is the COLOR correct ?

