#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 12:03:48 2019

@author: jonyoung
"""

import os

# set directory to run in and write log file to
top_dir = '/data/project/PSYSCAN/Raw_data_from_IXICO/PSYSCAN/'
output_dir = '/data/project/PSYSCAN/Jonathan/'


print 'looking for directories'

# list all directories inside the images_dir
dirs = [dirpath for dirpath, dirs, files in os.walk(top_dir)]

print 'found all directories'

# get list of the dirs at the most deeply nested level, as these are the ones
# containing image files
dir_depth = map(lambda dirpath: len(dirpath.split('/')), dirs)
max_depth = max(dir_depth)
image_dirs = []
for i in range(len(dirs)) :
    
    if dir_depth[i] == max_depth : 
  
        image_dirs.append(dirs[i])

text_file = open(output_dir + '/mismatched_timepoint_dirs.txt', "w")

print ('found ' + str(len(image_dirs)) + ' image directories')
        
# loop through the directories
for image_dir in image_dirs :
    
    # list the files
    all_files = os.listdir(image_dir)
    
    # allow for empty directories
    if len(all_files) > 0 :
    
        # get components of first file
        file_1 = all_files[0]
        
        # find filenames containing a timepoint
        # first split by underscore
        file_1_components = file_1.split('_')
        
        filename_has_tp = False
        filename_tp_ind = 0
        
        # go through components of file name, looking for anything  == 'Baseline' or 'Month'
        for i, component in enumerate(file_1_components) :
    
            if component == 'Baseline' or component == 'Month' :
                
                filename_has_tp = True
                filename_tp_ind = i
                break
            
        # if filename_has_tp, we can investigate
        if filename_has_tp :
            
            # get the tp
            filename_tp = file_1_components[filename_tp_ind]
            
            # if tp is a month, get the next component to know which one
            if filename_tp == 'Month' :
                
                filename_tp = filename_tp + '_' + file_1_components[filename_tp_ind + 1]
                
            # get the image directory timepoint
            image_dir_tp = image_dir.split('/')[-5]
            
            # compare the filename and image dir tps and if they are not the same
            # print out the directory and write it to file
            if not image_dir_tp == filename_tp :
                
                out_str = 'Image directory ' + image_dir + ' contains a timepoint mismatch'
                print (out_str)
                text_file.write(out_str + '\n')

text_file.close()
#            