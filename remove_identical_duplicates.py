#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:16:45 2019

@author: jonyoung
"""

import os
import natsort
from shutil import rmtree

# set directory to run in and write log file to
#top_dir = '/data/project/PSYSCAN/curated_data/'
#top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/identical_duplicate_removal_test/'
top_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/identical_duplicate_removal_test/'

# directory to find duplicate listing in
#listings_dir = '/home/k1511004/Data/PSYSCAN/WP5_data'
listings_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/'

# set timepoint of directories being processed
timepoint = 'Baseline'

# read in listings file line by line
listings_file = listings_dir + 'identical_duplicates.csv'
with open(listings_file) as f:
    identical_duplicate_dirs = f.readlines()
f.close()
    
# roll through the indentical duplicate dirs
for idd in identical_duplicate_dirs :
    
    # get subject and modality from idd
    subject, modality = idd.split(' ')[0:2]
    modality = modality.strip('\n')
    
    # construct the parent directory from the top_dir, subject, timepoint and modality
    modality_dir = 'sMRI' if modality == 'Structural' else 'fMRI'
    grandparent_directory = top_dir + subject + '/' + timepoint + '/' + modality_dir + '/'
    #print grandparent_directory
    
    # directories within grandparent directories vary in name, so look inside grandparent directory
    if os.path.isdir(grandparent_directory) :
    
        #parent_dirs = os.listdir(grandparent_directory)
	parent_dirs = filter(lambda x: os.path.isdir(grandparent_directory + x), os.listdir(grandparent_directory))
        
        # should be only one parent directory - flag up and skip if more than one is present
        if len(parent_dirs) > 1 :
            
            print ('WARNING: ' + grandparent_directory + ' contains more than one child directory. Skipping to the next one.')
        
        # if only one, check for identical_duplicates_removed.txt
        elif os.path.isfile(grandparent_directory + 'identical_duplicates_removed.txt') :

	    print ('WARNING: ' + grandparent_directory + ' has already had identical duplicates removed. Skipping to the next one.')

	else :
            
            # list image directories
            parent_dir = parent_dirs[0]
            image_dirs = os.listdir(grandparent_directory + parent_dir)
            
            # sort naturally to get lowest numbered directory
            image_dirs = natsort.natsorted(image_dirs)
            
            # want to keep 1st directory, remove the others
            image_dirs = image_dirs[1:]
            
            # list of directories we remove, and their original contents
            removed_directories = []
            
            # open a file to list what directories have been removed and where the original contents came from
            text_file = open(grandparent_directory + 'identical_duplicates_removed.txt', "w")
            
            # roll through the image directories we want to remove
            for image_dir in image_dirs :
                
                # read the original_directory.txt
                with open(grandparent_directory + parent_dir + '/' + image_dir + '/original_directory.txt') as f:
                    
                    original_dir = f.readlines()
                f.close()
                
                # store the information about the directory to be deleted
                removed_directories.append((image_dir, original_dir[1]))
                
                # remove the image directory
                rmtree(grandparent_directory + parent_dir + '/' + image_dir)
                
                # write to the file saying what directory was removed and where the contents came from
                text_file.write(grandparent_directory + parent_dir + '/' + image_dir + '/ was removed as it contained an identical duplicate.\n')
                text_file.write('files were originally from ' + original_dir[1] + '\n')
                
            # close the output file
            text_file.close()
            
                
                
            
