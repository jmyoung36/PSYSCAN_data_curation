#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:00:52 2019

@author: jonyoung
"""

# import what we need
import pandas as pd
from os import walk, listdir, rename

# set directories
curated_data_dir = '/data/project/PSYSCAN/curated_data/'
metadata_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/'

# read in the list of unusable directories
unusable_file_directories = pd.read_csv(metadata_dir + 'mark_as_unusable.csv')

# roll through subjects/timepoints to mark up
subjectids = unusable_file_directories['subjectid'].tolist()
timepoints = unusable_file_directories['timepoint'].tolist()
n_dirs = len(subjectids)
for i in range(n_dirs) :
    
    # list all directories for this subject + timepoint
    dirs = [dirpath for dirpath, dirs, files in walk(curated_data_dir + subjectids[i] + '/' + timepoints[i] + '/')]
    
    # if subjectid/timepoint exists
    if len(dirs) > 0 :
    
        # find directories containing images - these have the maximum depth
        dir_depth = map(lambda dirpath: len(dirpath.split('/')), dirs)
        max_depth = max(dir_depth)
        image_dirs = []
        for j in range(len(dirs)) :
        
            if dir_depth[j] == max_depth : 
            
                image_dirs.append(dirs[j])
                
        # loop through image dirs
        for image_dir in image_dirs :
            
            # list the filesg
            files  = listdir(image_dir)
            # filter out those txt files to leave only images
            image_files = filter(lambda x: not x[-3:] == 'txt', files)
            
            # check if there is any file already commencing 'EXCLUDE_' already
            do_exclude =  not any(map(lambda x: x[:8] == 'EXCLUDE_', image_files))
            
            if do_exclude :
            
                # loop through the image files, renaming them by prefixing with 'EXCLUDE_'
                for image_file in image_files :
                    
                    src = image_dir + '/' + image_file 
                    dst = image_dir + '/EXCLUDE_' + image_file
                    rename(src, dst) 
                    
                # leave a note explaining the 'EXCLUDE'
                text_file = open(image_dir + '/EXCLUDE.txt', "w")  
                text_file.write('Image files in this directory have been marked as EXCLUDE.\n')
                text_file.write('This means that although they have passed QC images may not be usable for cross-sectional or longitudinal analysis.\n')
                text_file.write('e.g. because they were scanned using a different coil than others from the same study site.\n')
                text_file.close()
    

