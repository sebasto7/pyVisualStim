

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psychopy
from psychopy import visual,core,logging,event, gui, monitors
from psychopy.visual.windowwarp import Warper # perspective correction
from matplotlib import pyplot as plt # For some checks
from stimuli import *
from helper import *
from exceptions import *
import PyDAQmx as daq
# The PyDAQmx module is a full interface to the NIDAQmx ANSI C driver. 
# It imports all the functions from the driver and imports all the predefined 
# constants. 
# This provides an almost one-to-one match between C and Python code
import pyglet.window.key as key
import numpy as np
import config
import h5py
import datetime
import time

#%%
def main(path_stimfile):
    """ 
        This function handles the window,logging, nidaq and played stimulus ...
    
        It also contains the monitor information you might want to edit.
        Press **Esc** to end the presentation immediately.
        Press **any key** to end the presentation after this epoch.
        
        :param path_stimfile: the path to the stimulus txt file
        :type path_stimfile: str
        
        .. note::
        The stimulus attributes specified in the txt file will change several 
        options, such as: prespective correction, randomization of epoch order, 
        stimulus type, etc. For more info, check each stimulus txt file and the 
        function that controls it specified under Stimulus.stimtype
            
    
    """
    
##############################################################################    
################################### GUI INPUTS ###############################
##############################################################################
    # Question: Put it on DLP ?
    dlp = gui.Dlg(title=u'Light Crafter', pos=None, size=None, style=None,
                  labelButtonOK=u' Yes ', labelButtonCancel=u' No ', screen=-1)
    dlp.addText('Want to use the DLP?')
    dlp_ok = dlp.show()
    
    #Messages
    mssg = gui.Dlg(title="Messages")
    mssg.addText('In the next box, you will define the basic experimental parameter')    
    mssg.addText('\nVIEWPOINTS have a range from 1 to -1. Eg., x = 0.5, y =0.5 refers to the screen center')
    mssg.addText("WARP options for prespective correction: ‘spherical’, ‘cylindrical, ‘warpfile’ or None")
    mssg.addText('\nPress OK to continue')
    mssg.show()
    if mssg.OK == False:
        core.quit()  # user pressed cancel
    
    # Store info about the experiment session
    exp_Info = {'ExpName': config.EXP_NAME,'User': config.MY_ID, 'Subject #': '001', 'ViewPoint_x': 0.5, 'ViewPoint_y':0.5, 'Warp': 'spherical'}
    dlg = gui.DlgFromDict(dictionary=exp_Info, sortKeys=False, title="Experimental parameters")

    if dlg.OK == False:
        core.quit()  # user pressed cancel
        
    _time = datetime.datetime.now()
    exp_Info['date'] = "%d_%d_%d_%d_%d_%d.txt" %(_time.year,_time.month,
                                                _time.day,_time.hour,
                                                _time.minute,_time.second) 
    exp_Info['psychopyVersion'] = psychopy.__version__
    exp_Info['frameRate'] = config.FRAMERATE
    exp_Info['distanceScreen'] = config.DISTANCE
    exp_Info['screenWidth'] = config.SCREEN_WIDTH
    
         
 ##############################################################################   

    
    # Create output file
    out = Output()
    outFile = out.create_outfile_temp(config.OUT_DIR,path_stimfile,exp_Info)
    
    # Read coonfig settings
    MAXRUNTIME = config.MAXRUNTIME
    framerate = config.FRAMERATE;
    fname = path_stimfile
    current_index = 0
    epoch = 0 #First epoch of the stimulus file
    stop = False
    
    # Read stimulus file 
    stimulus = Stimulus(fname)
    stimdict = stimulus.dict
            
    # Read Viewpositions
    viewpos = Viewpositions(config.VIEWPOS_FILE)
    _width = viewpos.width[0]
    _height = viewpos.height[0]
    _xpos = viewpos.x[0]
    _ypos = viewpos.y[0]
    
##############################################################################
############### Creating the window where to draw your screen ################
##############################################################################    
    
    # IMPORTANT: in order to use warper for perspective correction, 
    # useFBO = True is important for our window
    # What the useFBO does is render your window to an 'offscreen' window first 
    # before drawing that to the 'back buffer'and that process allows us to do 
    # some fancy transforms on the whole window when we then flip()

    

    #Initializing the window as a dark screen (color=[-1,-1,-1])
    if dlp.OK:
        #Using the projector
        #mon = monitors.Monitor('dlp', width=config.SCREEN_WIDTH, distance=config.DISTANCE)
        win = visual.Window(fullscr = False, monitor='dlp',
                            size = [_width,_height], viewScale = [1,1],
                            pos = [_xpos,_ypos], screen = 1, 
                            color=[-1,-1,-1],useFBO = True,allowGUI=False, 
                            viewOri = 0.0) 
        # viewScale = [1,1/2] because dlp in patternMode has rectangular pixels
        # viewOri to compensate for the tilt of the projector. 
        # If screen is already being tilted by Windows settings, set to 0.0 (deg)

    else:
        #In test mode on the PC screen
        _width = 325 # should genertae a window be of size = config.SCREEN_WIDTH on your PC monitor
        _height = 325 # should genertae a window be of size = config.SCREEN_WIDTH on your PC monitor
        
        _width = 1920
        _height = 1080
        
        #_width = 1080
        #_height = 1080
        
        #mon = monitors.Monitor('testMonitor', width=config.SCREEN_WIDTH, distance=config.DISTANCE)
        win = visual.Window(monitor='testMonitor',size = [_width,_height], screen = 0,
                            allowGUI=False, color=[-1,-1,-1],useFBO = True, viewOri = 0.0) 
    
    # Other screen parameters (In the App, they are set in the "Monitor Center")
    #win.scrWidthCM = config.SCREEN_WIDTH # Width of the projection area of the screen
    #win.scrDistCM = config.DISTANCE # Distancefrom the viewer to the screen 
        
    
    # #Detecting dropped frames if any
    # win.setRecordFrameIntervals(True)
    # # warn if frame is late more than 4 ms
    # win._refreshTreshold = 1/config.FRAMERATE+0.004 
    # logging.console.setLevel(logging.WARNING)
    
############################################################################## 
    
    # store frame rate of monitor if we can measure it
    exp_Info['frameRate'] = win.getActualFrameRate()
    if exp_Info['frameRate'] != None:
        frameDur = 1.0 / round(exp_Info['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess



    # Forcing the MAXRUNTIME to be 0 in test mode 
    if not dlp.OK:
        stimdict["MAXRUNTIME"] = 0
    

    # Write main setup to file
    write_main_setup(config.OUT_DIR,dlp.OK,config.MAXRUNTIME)
    
    # shuffle epochs newly, if start or every epoch has been displayed
    if current_index == 0:
        try:
            shuffle_index = shuffle_epochs(stimdict["RANDOMIZE"],stimdict["EPOCHS"])
        except:
            shuffle_index = shuffle_epochs(stimdict["randomize"][0],stimdict["EPOCHS"]) # Seb, temp line for old stimuli design
                


##############################################################################       
######### Creating some attributes per epoch (Stimulus object, bg, fg)########
##############################################################################
    # Generating or loading any stimulus data if STIMULUSDATA is not NULL
    if stimdict["STIMULUSDATA"] != "NULL":
            if stimdict["STIMULUSDATA"][0:10] == "SINUSOIDAL":
                _useTex = True
                _useNoise = False
                # Creting texture for the sinusoidal grating
                dimension = 128 # It needs to be square power-of-two (e.g. 64 x 64) for PsychoPy
                if stimdict['stimtype'][-1] == 'noisy_circle':
                        dimension = config.FRAMERATE  # It needs to be the lentgh of the screen refresh (frame) rate for a proper frequency sampling

                stim_texture_ls = list()
                for e in range(stimdict["EPOCHS"]):
                    con= stimdict['michealson.contrast'][e]
                    lum = stimdict['lum'][e]
                    #Important here to recalculate bg and fg from original lum nand con values.
                    # The previous bg and fg were already corrected for dlp bit depth
                    # and [-1,1] color range. We want to avoud this here for BG and FG.
                    # Calculation of BG and FG here depends on the michelson contrast definition
                    FG = (con * lum) + lum #wrong: lum*(1+con)
                    BG = 2*lum - FG # wrong:lum*(1-con)
                    print(f'Sinusoidal wave, FG:{FG} BG:{BG}')
                    f = 1# generate a single cycle
                    # Generate 1D wave and modulate the luminance and contrast
                    x = np.arange(dimension)
                    # Wave needs to be scaled to 0-1 so we can modulate it easier later
                    sine_signal = (np.sin(2 * np.pi * f * x / dimension)/2 +0.5)

                    # Scaling the signal
                    #It stills need to me done differently. the MContrast scaling is not properly working and the scaling is not symmetric. 
                    stim_texture  = (sine_signal  * 2*(FG - BG)* (63.0/255.0))-1 + (BG*(63.0/255.0)*2)# Scaling the signal to [-1,1] range, from 8bit to 6bit range and  to chosen MContrast
                    stim_texture_min = np.min(stim_texture)

                    # Making either 1D or 2D sine wave
                    stim_texture = np.tile(stim_texture, [dimension,1]) # Saving 2D wave in the list
                    stim_texture_ls.append(stim_texture)

                        

                if stimdict["STIMULUSDATA"][11:16] == "NOISY":
                    _useNoise = True
                    # Adding noise using target SNR
                    # Set a target SNR
                    # Creating noise array per epoch

                    # Max value of noise to avoid clipping of the sinusoidal wave
                    tolerated_noise_max_value_1 = 2*(abs(-1 - stim_texture_min)) # based on the lowest value for PSYCHOPY, -1
                    tolerated_noise_max_value_2 = np.min(stim_texture)-np.max(stim_texture) # based on the sinusoidal values. THIS CALCULATION ONLY MAKES SENSE FOR 50% MC

                    print('Noise levels (STD):')
                    noise_array_ls = list()
                    for i,SNR in enumerate(stimdict['SNR']):
                        target_snr = SNR
                        print(f'SNR {i}: {target_snr}')
                        # SNR as mean of standard deviation of signal/standard deviation of noise
                        # Wikipedia coeficient of variation definition
                        
                        signal = stim_texture_ls[i][1]
                        signal_mean = np.mean(signal)
                        signal_std = np.std(signal)
                        signal_std = np.std(stim_texture_ls[i])
                        print(f'STD signal {i}: {signal_std}')
                        signal_rms = np.sqrt(np.mean(signal**2))
                        noise_mean = 0
                        noise_std = (signal_std/target_snr) # Before was: (signal_mean/target_snr)
                        print(f'STD {i}: {noise_std}')
                        noise_arr = np.random.normal(noise_mean, noise_std, [1000,dimension,dimension])
                        print(f'MAX VALUE {i}: {np.max(noise_arr)}')
                        if np.max(noise_arr) > tolerated_noise_max_value_1:
                            print(f'WARNING!!! NOISE CLIPPING FOR EPOCH: {i}')
                        noise_rms = np.sqrt(np.mean(noise_arr[0,:,:]**2))
                        noise_array_ls.append(noise_arr)
                        
                        # Plotting what it will be presented
                        max_value = (2*(63.0/255.0))-1 # Max value in stim_texture after scaling
                        min_value = -1 # Min value in stim_texture after scaling
                        noisy_sinosoidal_wave = signal + noise_arr [1,1,:]
                        noisy_sinosoidal_wave[np.where(noisy_sinosoidal_wave> max_value)] = max_value
                        noisy_sinosoidal_wave[np.where(noisy_sinosoidal_wave<min_value)] = min_value
                        # plt.plot(noisy_sinosoidal_wave)
                        # plt.show()
                        
                        # Calculating std for noise based on SNR definition in dB
                        
                        # target_snr_db = 10* (np.log10(mean_signal/np.sqrt(noise_std)))
                        # target_snr_db = 10* (np.log10(signal_std/noise_std))
                        target_snr_db = 20* np.log10(signal_rms/noise_rms) # Wikipedia decibels definition
                        # print(f'SNR_dB {i}: {target_snr_db}')
                    
                else:
                    noise_array_ls = list()
                    for e in range(stimdict["EPOCHS"]):
                        noise_array_ls.append(None)
                        
            elif  stimdict["STIMULUSDATA"] == "TERNARY_TEXTURE":
                stim_texture_ls = list()
                noise_array_ls = list()
                choiseArr = [0,0.5,1]
                z= 10000 # z- dimension (here frames presented over time)
                if int(stimdict["texture.hor_size"][1]) == 1:
                    x= 1 # x-dimension
                    y = int(stimdict["texture.vert_size"][1]) # y-dimension
                    np.random.seed(config.SEED)
                    stim_texture= np.random.choice(choiseArr, size=(z,x,y))
                    stim_texture = np.repeat(stim_texture,int(stimdict["texture.vert_size"][1]),axis=1)
                elif int(stimdict["texture.vert_size"][1]) == 1:
                    x= int(stimdict["texture.hor_size"][1])
                    y = 1
                    np.random.seed(config.SEED)
                    stim_texture= np.random.choice(choiseArr, size=(z,x,y))
                    stim_texture = np.repeat(stim_texture,int(stimdict["texture.hor_size"][1]),axis=2)
                else:
                    x=int(stimdict["texture.hor_size"][1])
                    y=int(stimdict["texture.vert_size"][1])
                    np.random.seed(config.SEED)
                    stim_texture= np.random.choice(choiseArr, size=(z,x,y))
                
                stim_texture_ls.append(stim_texture) 
                noise_array_ls.append(None)
                
            elif  stimdict["STIMULUSDATA"] == "POLIGON":
                stim_texture_ls = list()
                noise_array_ls = list()
                x=int(stimdict["texture.hor_size"][1])
                y=int(stimdict["texture.vert_size"][1])
                z= 10000 # z- dimension (here frames presented over time)
                curr_arr = np.zeros(size=(z,x,y))
                
                
                
            else: # Specific case for older files (used in 2pstim-C- in which ["STIMULUSDATA"] was not specified
                 stim_texture = h5py.File(stimdict["STIMULUSDATA"])
                 stim_texture= stim_texture['stimulus'][()]
                 stim_texture= stim_texture[0:10000,:,:] # 10000 is a fix value
    
    else: # When ["STIMULUSDATA"]is == "NULL"
        stim_texture_ls = list()
        noise_array_ls = list()
        for e in range(stimdict["EPOCHS"]):
            stim_texture_ls.append(None)
            noise_array_ls.append(None)
        _useTex = False
        _useNoise = False
        
    # Creating the stimulus object per epoch
    stim_object_ls = list() 
    for i,stimtype in enumerate(stimdict["stimtype"]):
        if stimdict["pers.corr"][i] == 1:
            _units = 'deg' # Keep in "deg" when using the warper.

        else:
            #'degFlatPos' is the correct unit for having a correct screen size 
            # in degrees when the perspective is not corrected by the warper.
            _units = 'degFlatPos' 
            
        if stimtype[-6:] == "circle":
            circle = visual.Circle(win, units=_units, edges = 128)
            stim_object = circle
            
        elif stimtype ==  "stripe(s)":
            bar = visual.Rect(win, lineWidth=0, units=_units)
            stim_object = bar
            
        elif stimtype ==  "driftingstripe":
            bar = visual.Rect(win, lineWidth=0, units=_units)
            stim_object = bar
            
        elif stimtype == "noise":
            noise = visual.GratingStim(win,units=_units, name='noise',tex='sqr')
            stim_object = noise
            
        elif stimtype[-7:] == "grating":
            grating = visual.GratingStim(win,units=_units, name='grating', 
                                         tex='sqr',colorSpace='rgb',
                                         blendmode='avg',texRes=128, 
                                         interpolate=True, depth=-1.0, 
                                         phase = (0,0))
            # noise = visual.NoiseStim(win,units=_units, name='noise', 
            #                          colorSpace='rgb',noiseType='Binary',
            #                          noiseElementSize=0.0625,noiseBaseSf=8.0, 
            #                          noiseBW=1,noiseBWO=30, noiseOri=0.0,
            #                          noiseFractalPower=0.0,noiseFilterLower=1.0,
            #                          noiseFilterUpper=8.0, noiseFilterOrder=0.0,
            #                          noiseClip=3.0, interpolate=False, depth=0.0)
            # noise.buildNoise()
            stim_object =grating
            
        elif stimtype ==  "dottygrating":
            grating = visual.GratingStim(win,units=_units, name='grating', 
                                         tex='sqr',colorSpace='rgb',blendmode='avg',
                                         texRes=128, interpolate=True, depth=-1.0, 
                                         phase = (0,0))
            dots = visual.DotStim( win=win, name='dots', units=_units,
                                  nDots=int(stimdict["nDots"][i]), dotSize=5,
                                  speed=0.1, dir=0.0, coherence=1.0,
                                  fieldPos=(0.0, 0.0), fieldSize=2.0,
                                  fieldShape='square',signalDots='same', 
                                  noiseDots='position',dotLife=3,
                                  color=[-1.0,-0.7366,-0.7529], colorSpace='rgb', 
                                  opacity=1, depth=-1.0)
            stim_object =[grating,dots]
            
        stim_object_ls.append(stim_object)
        
        
    # Creating backgroung (bg) and foreground (fg) colors  per epoch
    bg_ls = list()
    fg_ls = list() 
    for e in range(stimdict["EPOCHS"]):
    
        # Setting stimulus backgroung (bg) and foreground (fg) colors 
        try: 
            if stimdict["lum"][e] == 111:
                # Gamma correction and 6-bit depth transformation
                bg = set_intensity(e,stimdict["bg"][e])
                fg = set_intensity(e,stimdict["fg"][e])
                bg_ls.append(bg)
                fg_ls.append(fg)
                
            elif stimdict["lum"][e] or stimdict["contrast"][e]:
                # Gamma correction and 6-bit depth transformation
                bg = set_bgcol(stimdict["lum"][e],stimdict["contrast"][e]) 
                fg = set_fgcol(stimdict["lum"][e],stimdict["contrast"][e])
                bg_ls.append(bg)
                fg_ls.append(fg)
            
            else:
                # Gamma correction and 6-bit depth transformation
                bg = set_intensity(e,stimdict["bg"][e])
                fg = set_intensity(e,stimdict["fg"][e])
                bg_ls.append(bg)
                fg_ls.append(fg)
                
        except:
            # Gamma correction and 6-bit depth transformation
            bg = set_intensity(e,stimdict["bg"][e])
            fg = set_intensity(e,stimdict["fg"][e])
            bg_ls.append(bg)
            fg_ls.append(fg)
            
##############################################################################
############################ NIDAQ CONFIGURATION #############################
##############################################################################

    # Initialize Time
    global_clock = core.Clock() 
    
    # Timer initiation
    duration_clock = global_clock.getTime() # it will be reset at every epoch    
    

    if dlp.OK:
        print('DLP used')

        counterTaskHandle = daq.TaskHandle(0) 
        pulseTaskHandle = daq.TaskHandle(0)   
        counterChannel = config.COUNTER_CHANNEL
        pulseChannel = config.PULSE_CHANNEL
        maxRate = config.MAXRATE

        # data from NIDAQ counter
        data = daq.uInt32(1)
        lastDataFrame = -1
        lastDataFrameStartTime = 0

        #DAQ SETUP FOR IMAGING SYNCHRONIZATION
        try:    
            # DAQmx Configure Code
            daq.DAQmxCreateTask("2",daq.byref(counterTaskHandle))
            daq.DAQmxCreateCICountEdgesChan(counterTaskHandle,counterChannel,
                                            "",daq.DAQmx_Val_Rising,0,
                                            daq.DAQmx_Val_CountUp)
            daq.DAQmxCreateTask("1",daq.byref(pulseTaskHandle))
            daq.DAQmxCreateCOPulseChanTime(pulseTaskHandle,pulseChannel,
                                           "",daq.DAQmx_Val_Seconds,
                                           daq.DAQmx_Val_Low,0,0.05,0.05)
            
            # DAQmx Start Code
            daq.DAQmxStartTask(counterTaskHandle) # Reading any coming frame.
            daq.DAQmxStartTask(pulseTaskHandle)   # Sending trigger to mic.

            # Reads incoming signal from microscope computer and stores it to 
            # 'data'. A rising edge is send every new frame the microscope 
            # starts to record, thus the 'data' variable is incremented
            daq.DAQmxReadCounterScalarU32(counterTaskHandle,1.0,
                                          daq.byref(data), None)
            
            # Do we need that here? Check it with hardware. 
            # Checks if new frame is being imaged.            
            if (lastDataFrame != data.value):
                lastDataFrame = data.value
                lastDataFrameStartTime = global_clock.getTime()

        except daq.DAQError as err:
            print ("DAQmx Error: %s"%err)
                
    else: 
        # When not using dlp (Checking the stimulus in th PCs monitor), 
        # some varibales need to be defined anyways, although they are 
        # not being change every frame.        
        counterTaskHandle = None
        data = daq.uInt32(1)
        lastDataFrame = 0
        lastDataFrameStartTime = 0
        print('No DLP used')
            
##############################################################################
######### MAIN Loop which calls the functions to draw stim on screen #########
##############################################################################        
    
    # Pause between sending the trigger to microscope and displaying stimuli
    # For not presenting the simuli during aninitial increase in fluorescence
    # that happens sometimes when the microscope starts scanning
    print('Microscope scanning started')
    print('5s pause...')
    time.sleep(5) 
    print('Stimulus started')
    
    # Main Loop: dit diplays the stimulus unless:
        # keyboard key is pressed (manual stop)
        # stop condition becomse "True" 
    while not (len(event.getKeys()) > 0 or stop):
        
        # choose next epoch
        try: 
            (epoch,current_index) = choose_epoch(shuffle_index,stimdict["RANDOMIZE"],
                                             stimdict["EPOCHS"],current_index)
        except:
            (epoch,current_index) = choose_epoch(shuffle_index,stimdict['randomize'][0],
                                             stimdict["EPOCHS"],current_index) # Seb, temp for old stimulus design
        
        # Data for Output file
        out.boutInd = out.boutInd + 1
        out.epochchoose = epoch
 
        # Subjects view perspective
        
        x_eyepoint = exp_Info['ViewPoint_x']
        y_eyepoint = exp_Info['ViewPoint_y']
        
        # warp for perspective correction
        if stimdict["pers.corr"][epoch] == 1:
            warper = Warper(win, warp=exp_Info['Warp'],warpfile = "",
                                warpGridsize= 300, eyepoint = [x_eyepoint,y_eyepoint], 
                                flipHorizontal = False, flipVertical = False)
            #warper.dist_cm = config.DISTANCE# debug_chris
            warper.changeProjection(warp='spherical', eyepoint=(exp_Info['ViewPoint_x'], exp_Info['ViewPoint_y']))# debug_chris
            #print(f'Warper eyepoints: {warper.eyepoint}')
        else:
            warper = Warper(win, warp= None, eyepoint = [x_eyepoint,y_eyepoint])
        # Reset epoch timer
        duration_clock = global_clock.getTime()  
        try:
                    
            # Functions that draw the different stimuli
            if stimdict["stimtype"][epoch] == "stripe(s)":
                
                (out, lastDataFrame, lastDataFrameStartTime) = flashing_stripes(bg_ls,fg_ls,stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch],dlp.OK,counterTaskHandle,data, lastDataFrame, lastDataFrameStartTime)
                                                                
            elif stimdict["stimtype"][epoch][-6:]== "circle":

                (out, lastDataFrame, lastDataFrameStartTime) = field_flash(bg_ls,fg_ls,stim_texture_ls[epoch],noise_array_ls[epoch],stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch],dlp.OK, viewpos, data, counterTaskHandle, lastDataFrame, lastDataFrameStartTime)
            
            elif stimdict["stimtype"][epoch] == "driftingstripe":

                (out, lastDataFrame, lastDataFrameStartTime) = drifting_stripe(bg_ls,fg_ls,stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch],dlp.OK, viewpos, data, counterTaskHandle, lastDataFrame, lastDataFrameStartTime)
                    
            
            elif stimdict["stimtype"][epoch] == "noise":
                    
                (out, lastDataFrame, lastDataFrameStartTime) = stim_noise(bg_ls,stim_texture,stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch],dlp.OK,counterTaskHandle,data, lastDataFrame, lastDataFrameStartTime)
                
            elif stimdict["stimtype"][epoch][-7:] == "grating":
                    
                (out, lastDataFrame, lastDataFrameStartTime)= noisy_grating(_useNoise,_useTex,viewpos,bg_ls,stim_texture_ls[epoch],noise_array_ls[epoch],stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch],dlp.OK,counterTaskHandle,data, lastDataFrame, lastDataFrameStartTime)
                
            elif stimdict["stimtype"][epoch] == "dottygrating":
                    
                (out, lastDataFrame, lastDataFrameStartTime)= dotty_grating(_useNoise,_useTex,viewpos,bg_ls,stim_texture_ls[epoch],stimdict,epoch, win, global_clock,duration_clock,outFile,
                                                                out,stim_object_ls[epoch][0],stim_object_ls[epoch][1],dlp.OK,counterTaskHandle,data, lastDataFrame, lastDataFrameStartTime)
            
            
            else: raise StimulusError(stimdict["stimtype"][epoch],epoch)
            
            # Irregular stop conditions:
            # "and not stimdict["MAXRUNTIME"]==0" is an quick fix to test stim 
            # on dlp without mic. Important for SEARCH Stimulus
            if (dlp.OK and (global_clock.getTime() - lastDataFrameStartTime > 1) 
                and not stimdict["MAXRUNTIME"]==0):
                raise MicroscopeException(lastDataFrame,lastDataFrameStartTime,global_clock.getTime())
            elif (dlp.OK and (global_clock.getTime() >= stimdict["MAXRUNTIME"]) 
                  and not stimdict["MAXRUNTIME"]==0):
                raise StimulusTimeExceededException(stimdict["MAXRUNTIME"],global_clock.getTime())
            elif (global_clock.getTime() >= MAXRUNTIME) and not stimdict["MAXRUNTIME"]==0:
                raise GlobalTimeExceededException(MAXRUNTIME,global_clock.getTime())
                
        # Real Errors      
        except StimulusError as e:
            print ('Stimulus function could not be executed. Stimtype:', e.type)
            print ('At epoch:', e.epoch)
            raise
        except daq.DAQError as err:
            print ("DAQmx Error: %s"%err)
        # Irregular stop conditions:   
        except MicroscopeException or StimulusTimeExceededException or GlobalTimeExceededException as e:
            pass 
            print ("A stop condition became true: " )
            print ("Time of %s was exceeded by current time %s at microscope frame %s. Maybe better use testmode (no DLP)?" %(e.spec_time,e.time,e.frame))
            print (e)
            stop = True
        # Manual stop from stimulus:
        except StopExperiment:
            print ("Stopped experiment manually")
             # fake key-press to stop experiments through event listener
            event._onPygletKey(key.END,key.MOD_CTRL)
            
    
    # ## 
    # #Uncomment the following if you would like to save the stimulation as a movie in your PC.
    # #Not recomended for usual recordings but just for examples of short duration
    ##Saving movie frames
    #win.saveMovieFrames('G:\\SebastianFilesExternalDrive\\Science\\PhDAGSilies\\2pData Python_data\\0. Stim gif files\\Record_Gratings_sine_5MC_white_noise_30sw_30deg_sec_1hz_3sec_DARK_3sec_moving_8_to_0.0625_48sec.gif')   
    
##############################################################################    
    # Save data
    outFile.close()
    save_main_setup(config.OUT_DIR)
    out.save_outfile(config.OUT_DIR)
    
    # DAQmx Stop Code
    if counterTaskHandle:
        clearTask(counterTaskHandle)
    if counterTaskHandle:
        clearTask(pulseTaskHandle)
        
    # Stop 
    print ("Write out ... close ...")
    win.close()
    core.quit()

     
    
def clearTask(taskHandle):
    """
    Clears a task from the card.
    """
    daq.DAQmxStopTask(taskHandle)
    daq.DAQmxClearTask(taskHandle)
 
if __name__ == "__main__":
    main()

# %%
