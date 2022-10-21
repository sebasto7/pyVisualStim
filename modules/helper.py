#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from collections import defaultdict

from exceptions import MicroscopeException, StimulusTimeExceededException, GlobalTimeExceededException
#import PyDAQmx as daq temporarily comented
import numpy
import datetime
import config
from psychopy import visual



class Viewpositions(object):
    """ Reads the Viewpositions file and stores its values 
    
        :param filename: The viewpositions.txt file
        :type filename: path
    
    """
    
    __slots__ = ['x','y','width','height','_viewpos']
    
    def __init__(self,filename):
        self._viewpos = []
        
        try:
            self._viewpos = numpy.genfromtxt(filename, dtype=None)
        except ValueError:
            print ('Viewpositions could not be read. Error msg:')
            raise 
            
        self.x = self._viewpos[0]
        self.y = self._viewpos[1]
        self.width = self._viewpos[2]
        self.height = self._viewpos[3]
        


class Output(object):
    
    """ The Output class contains all data which will be written to the output file
    
    """
    __slots__ = ['framenumber','tcurr','boutInd','epochchoose','xPos','yPos','rand_intensity','theta','data']
    def __init__(self):
        self.framenumber = 0
        self.tcurr = 0
        self.boutInd = 0
        self.epochchoose = 0
        self.xPos = 0
        self.yPos = 0
        self.theta = 0
        self.data = 0

    def save_outfile(self,location):
        """
        :param location: Location where files should be stored
        :type location: path
        """
        time = datetime.datetime.now()
        outfile_name = "%s\\%s_%d_%d_%d_%d_%d_%d.txt" %(location,config.OUTFILE_NAME,time.year,time.month,time.day,time.hour,time.minute,time.second)
        
        outfile_temp = "%s\\%s.txt" %(location,config.OUTFILE_NAME)
        with open(outfile_temp) as source:
            with open(outfile_name, 'w') as dest:
                for line in source:
                    dest.write(line)

        
    def create_outfile_temp(self,location,path_stimfile,exp_Info):
    
        """
        :param location: Location where files should be stored
        :type location: path
        :param path_stimfile: Location and name of chosen stimfile
        :type path_stimfile: path
        
        """
    
        outfile_temp_name = "%s\\%s.txt" %(location,config.OUTFILE_NAME)
        outFile_temp = open(outfile_temp_name, 'w')
        expInfo = '%s %s \n' % (exp_Info["ExpName"],exp_Info["User"])#exp_Info["Subject #"]
        stimfile = '%s\n' % (path_stimfile)
        outFile_temp.write(expInfo)
        outFile_temp.write(stimfile)
        outFile_temp.write('frame,tcurr,boutInd,epoch,xpos,ypos,theta,data\n')
        
        return outFile_temp
    

class Stimulus(object):
    """ Takes a stimulus filename as input and creates a dictionary of lists with all stimulus attributes 
        provided by the stimfile. If a list of epochs has only one element, the value will be extracted from the list and 
        thus is directly usable.
        
        :param dict: dictionary containing the Stimulus attributes names as keys and as values lists containing 
                    one element per epoch
        :type dict: defaultdict, default_factory = None
        
        """

    def __init__(self,filename):
        
        self.dict = self._read(filename)

    def _read(self,filename):
    
        """
        :param filename: Stimfile to read from
        :type filename: path
        
        """
        dict = defaultdict()
        
        with open(filename) as file:
            for line in file:
                curr_list = line.split()

                if not curr_list:
                    continue
                    
                key = curr_list.pop(0)
                
                if len(curr_list) == 1 and not "Stimulus." in key:
                    try:
                        dict[key] = int(curr_list[0])
                    except ValueError:
                        dict[key] = curr_list[0]
                    continue 
                    
                if key.startswith("Stimulus."):
                    key = key[9:]
                    
                    if key.startswith("stimtype"):
                        dict[key] = list(map(str, curr_list))
                    else: 
                        dict[key] = list(map(float, curr_list))

        return dict
                

def write_main_setup(location,dlp_ok,MAXRUNTIME):

    """ Writes the meta_data file which logs global settings """

    # A temporary mainfile, containing data of last run
    mainfile_name_temp = "%s\\%s.txt" %(location,config.MAINFILE_NAME)
    mainfile_temp = open(mainfile_name_temp, 'w')

    mainfile_temp.write("useDLP %d\n" % dlp_ok)
    mainfile_temp.write("MAXRUNTIME %f\n" % MAXRUNTIME)
    
def save_main_setup(location):

    """ Copies the current meta_data file to a timestamped meta_data file.
    This is execution specific."""
    
    # A permanently saved mainfile copy with time stemp
    time = datetime.datetime.now()
    mainfile_name = "%s\\_meta_data_%d_%d_%d_%d_%d_%d.txt" %(location,time.year,time.month,time.day,time.hour,time.minute,time.second)
    
    mainfile_temp = "%s\\%s.txt" %(location, config.MAINFILE_NAME)
    with open(mainfile_temp) as source:
        with open(mainfile_name, 'w') as dest:
            for line in source:
                dest.write(line)

    
def write_out(outFile,out):

    """ Checks NIDAQ data and writes all out-data to output file.
    
    :param global_clock: global clock, will be written to output
    :type global_clock: core.Clock
    :param outFile: The output file
    :type outFile: A csv .txt file
    :param out: The output data
    :type out: `helper.Output`
    :param data: counter for microsope frames
    :type data: uInt32()
    :param lastDataFrame: last frame recorded by microsope
    :type lastDataFrame: uInt32()
    :param lastDataFrameStartTime: time the microsope started to record the last frame
    :type lastDataFrameStartTime: time
    
    :returns: The updated NIDAQ data and read in time.
    
    .. note::
        The NIDAQ arguments (data, lastDataFrame, lastDataFrameStartTime) are only needed if DLP is used
    
    .. note::
        The output file contains (framenumber,time, 0,epochchoose,xPos,0,theta = rotation,0)
    
    """
    # write out as a comma seperated file or tab separated
    outFile.write('%8d, %8.3f, %8d, %8d, %8.4f, %8.4f,%8.4f, %8d\n' %(out.framenumber,out.tcurr,out.boutInd,out.epochchoose,out.xPos,out.yPos,out.theta,out.data))
    # outFile.write('%8d %8.3f %8d %8d %8.4f %8.4f %8.4f %8d\n' %(out.framenumber,out.tcurr,out.boutInd,out.epochchoose,out.xPos,out.yPos,out.theta,out.data))

def check_timing_nidaq(dlpOK,stimdictMAXRUNTIME,global_clock,taskHandle = None,data = 0 ,lastDataFrame = 0 ,lastDataFrameStartTime = 0):
    """
    Reads in the microscope's signal, updates framenumber (in data) and checks if microscope still works in time.
    Furthermore it checks if a time constant has been exceeded (MAXRUNTIME's)
    
    :param dlpOK: Is DLP used (so, not in testmode)?
    :type dlpOK: boolean
    :param stimdictMAXRUNTIME: The stimulus' MAXRUNTIME
    :type stimdictMAXRUNTIME: int
    :param global_clock: global clock, will be written to output
    :type global_clock: core.Clock
    :param data: counter for microsope frames
    :type data: uInt32()
    :param lastDataFrame: last frame recorded by microsope
    :type lastDataFrame: uInt32()
    :param lastDataFrameStartTime: time the microsope started to record the last frame
    :type lastDataFrameStartTime: time
    
    :returns: The updated NIDAQ data and read in time.
    
    .. note::
        The NIDAQ arguments (data, lastDataFrame, lastDataFrameStartTime) are only needed if DLP is used
    """
    # check for DAQ Data
    if taskHandle != None:
        daq.DAQmxReadCounterScalarU32(taskHandle,1.0,daq.byref(data), None) 

        if (lastDataFrame != data.value):
            lastDataFrame = data.value
            lastDataFrameStartTime = global_clock.getTime()
    
    # Irregular stop conditions:       
    if dlpOK and (global_clock.getTime() - lastDataFrameStartTime > 1):
       raise MicroscopeException(lastDataFrame,lastDataFrameStartTime,global_clock.getTime())
     
    elif dlpOK and (global_clock.getTime() >= stimdictMAXRUNTIME):
        raise StimulusTimeExceededException(stimdictMAXRUNTIME,global_clock.getTime())
        
    elif global_clock.getTime() >= config.MAXRUNTIME:
        raise GlobalTimeExceededException(config.MAXRUNTIME,global_clock.getTime())
       
    return (data.value,lastDataFrame, lastDataFrameStartTime)
    
def shuffle_epochs(randomize,no_epochs):
    """Shuffles the epoch sequence according to the randomize option.
    
    :param randomize: 0 (don't shuffle), 1 (shuffle randomly, except 1st epoch), 2 (shuffle randomly).
    :type randomize: Integer
    :param no_epochs: Number of epochs in stimfile.
    :type no_epochs: Integer
    :returns: numpy integer array of shuffled epoch indices. 
  
    """
    if randomize == 0.0:
        # dont shuffle epochs
        index = numpy.zeros((no_epochs,1))
        index = index.astype(int)
        for ii in range(0,no_epochs):
            index[ii] = ii

    elif randomize == 1.0:
        # shuffle epochs randomly, except epoch 0
        # every 2nd epochchoose == 0
        index = numpy.zeros((no_epochs-1,1))
        index = index.astype(int)
        
        for ii in range(0,no_epochs-1):
            index[ii] = ii+1
        
        # numpy.random.seed(config.SEED)
        numpy.random.shuffle(index) # Actual shuffling

    elif randomize == 2.0:
        # shuffle epochs randomly
        index = numpy.zeros((no_epochs,1))
        index = index.astype(int)
        
        for ii in range(no_epochs):
            index[ii] = ii
            
        # numpy.random.seed(config.SEED)
        numpy.random.shuffle(index) # Actual shuffling

            
    return index
    
def choose_epoch(index,randomize,no_epochs,current_index):
    """Shuffles the epoch sequence according to the randomize option.
    
    :param index: Array of shuffled epoch indices.
    :type index: Numpy int array
    :param randomize: 0 (choose next), 1 (every 2nd epoch choose epoch 0), 2 (choose next epoch).
    :type randomize: Integer
    :param no_epochs: Number of epochs in stimfile.
    :type no_epochs: Integer
    :param current_index: Current chosen index of index-array.
    :type current_indexs: Integer
    :returns: Integer of chosen epoch index 

    
    """

    if randomize == 0.0 or randomize == 2.0:                
        epochchoose = index.item((current_index,0))
        current_index = (current_index+1) % no_epochs
        print('Presented epoch: {}'.format(epochchoose))
        
    elif randomize == 1.0:
         # every 2nd epochchoose == 0
        if (current_index % 2) == 1:
            epochchoose = index.item(int((current_index-1)/2),0)
            print('Presented epoch: {}'.format(epochchoose))
        else:
            epochchoose = 0
            print('Presented epoch: {}'.format(epochchoose))
        current_index = (current_index+1) % (2*(no_epochs-1))
        
    return (epochchoose, current_index)


def set_bgcol(lum,con):
    
    """ Sets background color according to luminance and contrast in stimfile 
    
    It's calculated this way like::
        
        bgcol = lum*(1-con)
    
    """
    
    bgcol = lum*(1-con)

    background = [0]*3
    background[0] = 0.0 *2-1 # the *2-1 part converts the color space [0,1] -> [-1,1]
    background[1] = get_dlpcol(bgcol,'G')*2-1 
    background[2] = get_dlpcol(bgcol,'B')*2-1
    
    
    return background
    
def set_fgcol(lum,con):
    
    """ Sets background color according to luminance and contrast in stimfile 
    
    :param lum: the luminance defined py this epoch.
    :type lum: double
    :param con: the contrast defined py this epoch.
    :type con: double
    :returns: double
    
    
    It's calculated this way like::
        
        fgcol = lum*(1+con)
    
    """

    fgcol = lum*(1+con)

    foreground = [0]*3
    foreground[0] = 0.0 *2-1 # the *2-1 part converts the color space [0,1] -> [-1,1]
    foreground[1] = get_dlpcol(fgcol,'G')*2-1
    foreground[2] = get_dlpcol(fgcol,'B')*2-1
    
    
    return foreground
    
def set_intensity(epoch,value):

    """ Returns Intensity color 
    It calls the function for gamma correction and 6-bit depth transformation

    :returns: list of 3 floats for RGB color space in range [-1,1]

    """

    intensity = [0] * 3

    intensity[0] = 0.0 * 2 - 1  # the *2-1 part converts the color space [0,1] -> [-1,1]
    intensity[1] = 0.0 * 2 - 1  # the *2-1 part converts the color space [0,1] -> [-1,1] , before get_dlpcol(value, 'G') * 2 - 1
    intensity[2] = get_dlpcol(value, 'B') * 2 - 1

    return intensity

def get_dlpcol(DLPintensity,channel):
    
    """ Gamma correction 
    
    This function uses some measured screen properties to correct light intensity.
    It also converts the values from 8 bit depth (0 to 255) to 6 bit depth (0 to 63)
    
    :param DLPintensity: the fore- or background color value.
    :type DLPintensity: double
    :param channel: the color channel green 'G' or blue 'B'
    :type channel: char
    :returns: double in [0,1].
    
    """
    
    # Some fixed - measured variables
    gamma_gr = 0.9872   # LightCrafter 4500, 6 bit depth, measurements 140508
    scale_gr = 1.0340
    gamma_bl = 1        # blue values are dummy values
    scale_bl = 1
    
    temp = 0
    
    # if channel == 'G':
    #     temp = pow(DLPintensity/scale_gr , 1/gamma_gr) # Seb, commented 2022.06.07
    
    if channel == 'B':
        temp = pow(DLPintensity/scale_bl, 1/gamma_bl)
    
    
    # keep the output in the closed interval [0, 1]
    if temp > 1:
        temp = 1
    
    if temp < 0:
        temp = 0


    # temp = DLPintensity; # debug line to use if we want to turn off gamma correction
    temp *= 63.0/255.0 # convert from 8 bit depth to 6 bit depth. 
    
    return temp


def max_horizontal_angle(screen_width, distance):

    """ Returns the angular extent of the edge of screen along x-axis in degrees
    with respect to the fly 

    Assumes that the subject lies on an axis which passes through the screen
    and that it is horizontally-centered relative to the screen.
    Thus, a perpendicular line from the subject to the screen has a degree
    of zero. Returned value is always positive, therefore the other edge of
    the screen has the opposite sign of the returned value.
    It's calculated this way::

        angle = arctan((screen width/2) /distance of subject to the screen)
        
        which is the same as:
        
        angle = arctan(screen width /(2*distance of subject to the screen))
            

    :param screen_width: width of the screen
    :type screen_width: float
    :param distance: perpendicular distance of the subject to the screen
    :type distance: float
    :returns: float

    """

    maxhorang = numpy.arctan((screen_width/2) / distance)
    maxhorang = abs(numpy.degrees(maxhorang))
    

    return maxhorang

def max_vertical_angle(screen_width, distance):

    """ Returns the angular extent of the edge of screen along y-axis in degrees
    with respect to the fly 

    Assumes that the subject lies at the top of the y-axis which goes down 
    vertically.
    Thus, a perpendicular line from the subject to the screen has a degree
    of zero. Returned value is always positive.
    It's calculated this way::

         angle = (arctan((screen width) /distance of subject to the screen))

    :param screen_width: width of the screen
    :type screen_width: float
    :param distance: perpendicular distance of the subject to the screen
    :type distance: float
    :returns: float

    """

    maxverang = numpy.arctan((screen_width) / distance)
    maxverang = (abs(numpy.degrees(maxverang)))
    

    return maxverang


def position_x(stimdict, epoch, screen_width, distance, seed):

    """ Returns random position values on the x-axis.

    It makes use of a default seed value to make experiment replicable.
    If the maximum position in the stimulus file is higher than the angular
    extent, it makes the value in the stimulus file equal to the angular
    extent, therefore the stimulus is not placed outside of the screen.
    The same applies for the minimum porsition in the stimulus file.

    :param screen_width: width of the screen
    :type screen_width: float
    :param distance: perpendicular distance of the subject to the screen
    :type distance: float
    :param seed: seed to be used in the pseudo-random number generation
    :type seed: int
    :returns: NumPy integer array

    """
    xmax = stimdict["bar.xmax"][epoch]
    xmin = stimdict["bar.xmin"][epoch]
    bar_distance = stimdict["bar.distance"][epoch]

    hor_angle = max_horizontal_angle(screen_width, distance)
    # hor_extent = abs(hor_angle - (stimdict["bar.width"][epoch]))
    hor_extent = abs(hor_angle)

    if xmin < -hor_extent:
        xmin = -hor_extent

    if xmax > hor_extent:
        xmax = hor_extent
        

    xpos = numpy.arange(xmin, xmax, bar_distance)
    seeder = numpy.random.RandomState(seed)
    seeder.shuffle(xpos)

    return xpos

def position_y(stimdict, epoch, screen_width, distance, seed):

    """ Returns random position values on the y-axis.

    It makes use of a default seed value to make experiment replicable.
    If the maximum position in the stimulus file is higher than the angular
    extent, it makes the value in the stimulus file equal to the angular
    extent, therefore the stimulus is not placed outside of the screen.
    The same applies for the minimum porsition in the stimulus file.

    :param screen_width: width of the screen
    :type screen_width: float
    :param distance: perpendicular distance of the subject to the screen
    :type distance: float
    :param seed: seed to be used in the pseudo-random number generation
    :type seed: int
    :returns: NumPy integer array

    """
    
        
    ymax = stimdict["bar.ymax"][epoch]
    ymin = (stimdict["bar.width"][epoch])
    bar_distance = stimdict["bar.distance"][epoch]

    ver_angle = max_vertical_angle(screen_width, distance)
    # ver_extent = abs(ver_angle - (stimdict["bar.width"][epoch]))
    ver_extent = abs(ver_angle)
    
    if stimdict["pers.corr"][epoch] == 1:

        if ymin < -ver_extent:
            ymin = -ver_extent
    
        if ymax > ver_extent:
            ymax = ver_extent

        
    else:
        ver_angle = max_horizontal_angle(screen_width, distance) # Vertical extent will max how we calculate the horizontal extent
        ver_extent = abs(ver_angle)
        ymin = -ver_extent 
        ymax= ver_extent
        
    ypos = numpy.arange(ymin, ymax, bar_distance) 
    ypos = ypos*-1 #-1 to move downswards with the stimulus
    seeder = numpy.random.RandomState(seed)
    seeder.shuffle(ypos)


    return ypos


def subwindow(win,size=1,shape=[(-0.5,-1), (0.5, -1), (0.5, 0), (-0.5, 0)]):

    """ creates a restricted area inside the visual.window instance
        the stimulus is visible only under the inclusion area defined by shape"""

    """ input: 
                win: psychopy.visual.window instance 
                size: size
                shape: corners of a polygon defining the position of the included area"""
    
    aperture = visual.Aperture(win, size=1, shape=shape)  # try shape='square'
    aperture.enabled=True