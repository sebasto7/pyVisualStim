# tests for helper functions



from logging import raiseExceptions
from typing import final
import psychopy
from psychopy import visual,core,logging,event, gui, monitors
from psychopy.visual.windowwarp import Warper # perspective correction
from matplotlib import pyplot as plt # For some checks
import PyDAQmx as daq
# The PyDAQmx module is a full interface to the NIDAQmx ANSI C driver.
# It imports all the functions from the driver and imports all the predefined
# constants.
# This provides an almost one-to-one match between C and Python code
import pyglet.window.key as key
import numpy as np
import h5py
import datetime
import time
import sys
import copy

#from modules.helper import *
#from modules.exceptions import *
#from modules import config
#from  modules import stimuli

#%%
def random_persistent_behavior_vector(seeds,frames,choices_dur):
    
    """ this function uses a random seed to create a list of random numbers from a choice list 
        the choice list represents the range of durations possible from where values are drawn based on an
        uniform distribution
        
        output is a list of numbers which sum is equal or higher than the number of frames"""

    if frames>20000:
        raise Exception ('seems like this is too many frames. consider if this is necessary ')

    final_vectors = []
    
    for local_seed in seeds:
        local_vector = []
        np.random.seed(local_seed)
        while np.sum(local_vector)<frames:
            local_vector.append(np.random.choice(choices_dur))

        final_vectors.append(local_vector)
    return final_vectors
    
def random_persistent_values(persistent_behavior_vectors,seeds,frames,possible_values,size):

    """ using the output of random_persistent_behavior_vector(seeds,frames,choices_dur) this function 
    draws possible values from an uniform distribution to populate or modify a noise stimulus
    
    seeds: random seeds to draw values (as many as persistent behavior vectors are required
    frames: lenght of stimulus in frames
    possible values: the set of values from which is possible to choose
    size: the size of a frame of output, if youre building a video, then size is (x,y) dimensions
          if you are for example modifying a frames by shifting one dimension, then size is (1)... 
          
    output: chosen random values based on persistent behavior vector and a uniform distribution"""

    output_values=[]
    
    for vector,local_seed in zip(persistent_behavior_vectors,seeds):
        if len(size)==2:
            local_outputvals = np.zeros((np.sum(vector),size[0],size[1]))
        else:
            local_outputvals = np.zeros((np.sum(vector)))
        np.random.seed(local_seed)
        count=0
        for ix,repeats in enumerate(vector):
            if len(size)==2:
                value_movement = np.random.choice(possible_values,size=(size[0],size[1]))
                local_outputvals[count:count+repeats,:,:] = value_movement[np.newaxis,:,:]
            else:     
                value_movement = np.random.choice(possible_values,size=(1))
                local_outputvals[count:count+repeats] = value_movement
            count=count+repeats

        if len(size)==2:
            output_values.append(local_outputvals[:frames,:,:])
        else:
            output_values.append(local_outputvals[:frames])
    return output_values

def max_angle_from_center(screen_width, distance):

    """ Returns the angular extent of the screen from the center to the edge
    in degrees with respect to the fly

    Assumes that the subject lies on an axis which passes through the screen
    and that it is centered relative to the screen.
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

    max_ang = np.arctan((screen_width/2) / distance)
    max_ang = abs(np.degrees(max_ang))


    return max_ang

#%%

persistant = True

grayvalues = np.array([0,2.0]).astype('float64')
grayvalues = np.where(grayvalues>-1,(grayvalues*63.0/255.0)-1,-1)
#print(grayvalues)
number_of_frames=15000
stim_texture_ls = list()
noise_array_ls = list()
moves = np.zeros((2, number_of_frames)) # 2 directions: x and y. 15000 random choices of shift that should be divisible by the shift resolution

# set the resolution of the stimulus which is defined by the minimal movement posible, which is the lenght of movement given the speed and the framerate
# ideally this should be an integer that should be able to divide without residue the final matrix size

step = 0.05*20 # maybe this should be hardcoded
minimum_step = step*np.cos(np.deg2rad(45))


#if 80%step != 0:
#    raise Exception('in the current implementation, the code only accepts divisors of 80 as step')

# set posible steps in units of stimulus pixels (the real step choice is -1*step,0,1*step)
step_choices = [-1,0,1]
                

# set stimuli dimensions

box_size_x = 5 # first guess: this number should be around 20 
box_size_y = 5

frames=number_of_frames

# if 80%box_size_x == 0 and 80%box_size_y ==0:                
#             x_dim = int(80/box_size_x) #80 is the size of the screen in degrees, for now this is hardcoded
#             y_dim = int(80/box_size_y)

# else:
#     raise Exception ('in the current implementation, the code only accepts divisors of 80 as box_size')

x_dim = int((max_angle_from_center(9,5.3)*2)//box_size_x)
y_dim = int((max_angle_from_center(9,5.3)*2)//box_size_y)

minimum_size_step_based = int((max_angle_from_center(9,5.3)*2)//step)
minimum_size_diag_step = int((max_angle_from_center(9,5.3)*2)//minimum_step)



diagonal_upscale_factor = 1/(minimum_step)

#np.random.seed(3)

#test = stimdict["Test"]

#final_size=int(80/step)


if persistant: # if we want the field to move consistently for a number of frames
    # it takes tha same as the dimension number in steps to reach the original position
    
    choices_of_duration = np.array(range(1,30))# the maximum duration of a moving bout is determined by the size of the screen
    
    
    persistant_val1,persistant_val2 = random_persistent_behavior_vector([4,5],number_of_frames,choices_of_duration) # function in helpers
    moves1,moves2  =  random_persistent_values([persistant_val1,persistant_val2],[0,10],number_of_frames,step_choices,[1]) # function in helpers

    
    moves[0,:] = moves1
    moves[1,:] = moves2
    moves=np.cumsum((moves),axis=1)

    # choose persistent luminances to enhance the motion signal relative to the luminance one

    persistant_lum = random_persistent_behavior_vector([5],number_of_frames,choices_of_duration)
    noise_texture = random_persistent_values(persistant_lum,[3],number_of_frames,grayvalues,size=[x_dim,y_dim])
    noise_texture = noise_texture[0]
    moves=np.cumsum((moves),axis=1)
else:

    for i in range(0,2): # x,y shift arrays
            np.random.seed(i)
            moves[i,:]= np.random.choice(step_choices, number_of_frames, replace=True)#range(int(np.floor(-38/stimdict["Shift_resolution"])),int(np.floor(40/stimdict["Shift_resolution"]))), number_of_frames, replace=True) #this range determines the x multiples of shifts 
    
    moves=np.cumsum((moves),axis=1)
    # if test:
    # noise_texture = np.random.choice(grayvalues, size=(1,y_dim,x_dim))
    # noise_texture = np.repeat(noise_texture,repeats=15000,axis=0)
    # else:


    np.random.seed(3)
    print(3)
    noise_texture = np.random.choice(grayvalues, size=(number_of_frames,y_dim,x_dim))

#upscale the stim array to be able to shift with a step resolution

minimum_size_based_on_step = final_size
minimum_size_based_on_boxsizex = x_dim
minimum_size_based_on_boxsizey = y_dim

minimum_sizex = np.lcm(minimum_size_based_on_step,minimum_size_based_on_boxsizex)
minimum_sizey = np.lcm(minimum_size_based_on_step,minimum_size_based_on_boxsizey)

upscale_factor_x = minimum_sizex/x_dim
upscale_factor_y = minimum_sizey/y_dim

resolutionx = 80/minimum_sizex
resolutiony = 80/minimum_sizey
step_multiplierx = step/resolutionx
step_multipliery = step/resolutiony

noise_texture = np.repeat(noise_texture,int(upscale_factor_x),axis=1) # this brings the size of the matrix to the 80*80 size, then the shifts will be in the right scale
noise_texture = np.repeat(noise_texture,int(upscale_factor_y),axis=2)

moves[0,:] = moves[0,:]* step_multiplierx
moves[1,:] = moves[1,:]* step_multipliery

#copy_texture = copy.deepcopy(noise_texture)
#print(np.unique(noise_texture))
for frame in range(int(number_of_frames)):
    
    noise_texture[frame,:,:]=np.roll(noise_texture[frame,:,:], int(moves[0,frame]),axis=0)
    noise_texture[frame,:,:]=np.roll(noise_texture[frame,:,:], int(moves[1,frame]),axis=1)
    #test
    #noise_texture[frame,:,:]=np.roll(noise_texture[frame,:,:], frame*1,axis=0)
    #noise_texture[frame,:,:]=np.roll(noise_texture[frame,:,:], frame*0,axis=1)
    ##end of test
    

#plot distributions 







# if stimdict["print"] == 'True':
#     for frame in range(int(number_of_frames/100)):
#         plt.figure()
#         plt.imshow(noise_texture[frame,:,:],cmap='gray')
#         plt.savefig("C:\\#Coding\\pyVisualStim\\stimuli_collection\\7.High_resolution_WN\\pics_movingnoise\\_" + str(frame) + ".jpg")
#         plt.close()
# #     sys.exit()
# stim_texture_ls.append(noise_texture)

# if stimdict["print"] == 'True':

#     plt.figure()
#     plt.hist(moves[0,:],bins=np.arange(-20,22,1))
#     plt.savefig("C:\\#Coding\\pyVisualStim\\stimuli_collection\\7.High_resolution_WN\\pics_movingnoise\\stimulus_hist%s_%sdegbox_%sdeg_shift.jpg"%(0,stimdict["Box_sizeX"],stimdict["Shift_resolution"]))
#     plt.close('all')
#     plt.figure()
#     plt.hist(moves[1,:],bins=np.arange(-20,22,1))
#     plt.savefig("C:\\#Coding\\pyVisualStim\\stimuli_collection\\7.High_resolution_WN\\pics_movingnoise\\stimulus_hist%s_%sdegbox_%sdeg_shift.jpg"%(1,stimdict["Box_sizeX"],stimdict["Shift_resolution"]))
#     plt.close('all')

#     print(np.unique(stim_texture_ls))
#     print(np.max(np.array(stim_texture_ls)))
#     copy_texture = np.squeeze(np.array(stim_texture_ls)) # normalize the stimulus before saving)
#     print(copy_texture.shape)
#     print(np.unique(copy_texture))
#     np.save("C:\\#Coding\\pyVisualStim\\stimuli_collection\\7.High_resolution_WN\\pics\\stimulus_%sdegbox_%sdeg_shift.npy"%(stimdict["Box_sizeX"],stimdict["Shift_resolution"]),copy_texture)
    

#     sys.exit()
