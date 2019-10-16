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
top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/identical_duplicate_removal_test/'
#top_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/identical_duplicate_removal_test/'

# directory to find duplicate listing in
listings_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/'
#listings_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/'

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

        # check for identical_duplicates_removed.txt
        if os.path.isfile(grandparent_directory + 'identical_duplicates_removed.txt') :

            print ('WARNING: ' + grandparent_directory + ' has already had identical duplicates removed. Skipping to the next one.')

    	else :

    	    # get parent directories
    	    parent_dirs = filter(lambda x: os.path.isdir(grandparent_directory + x), os.listdir(grandparent_directory))
    
    	    # natural sort to keep only an image from the first directory if there is more than one
    	    parent_dirs = natsort.natsorted(parent_dirs)
    
    	    # open a file to list what directories have been removed and where the original contents came from
            text_file = open(grandparent_directory + 'identical_duplicates_removed.txt', "w")
    
            # for the first parent directory, only list 2nd directory onward for removal so we keep 1st
            parent_dir = parent_dirs[0]
            image_dirs = os.listdir(grandparent_directory + parent_dir)
            image_dirs = natsort.natsorted(image_dirs)[1:]
    
    	    # delete image dirs and at the same time write to file their original location
            for image_dir in image_dirs :
    
                # read the original_directory.txt
                with open(grandparent_directory + parent_dir + '/' + image_dir + '/original_directory.txt') as f:
                        
                    original_dir = f.readlines()
                    
                f.close()
    
                text_file.write(grandparent_directory + parent_dir + '/' + image_dir + '/ was removed as it contained an identical duplicate.\n')
                text_file.write('files were originally from ' + original_dir[1] + '\n')
    
            		# remove the image directory
                rmtree(grandparent_directory + parent_dir + '/' + image_dir)
    	
            # for any further parent directories, remove ALL image directories
            # go through the image directories to read and rewrite their details
            # then rmtree at the parent directory to remove all image directories at once and avoid leaving an empty parent directory
            for parent_dir in parent_dirs[1:] :
                
                image_dirs = os.listdir(grandparent_directory + parent_dir)
                image_dirs = natsort.natsorted(image_dirs)
                for image_dir in image_dirs :
                    
                    # read the original_directory.txt
                    with open(grandparent_directory + parent_dir + '/' + image_dir + '/original_directory.txt') as f:
    	                    
                        original_dir = f.readlines()
                    
                    f.close()
    
                    text_file.write(grandparent_directory + parent_dir + '/' + image_dir + '/ was removed as it contained an identical duplicate.\n')
                    text_file.write('files were originally from ' + original_dir[1] + '\n')
    
    		# remove the whole parent dir
    		rmtree(grandparent_directory + parent_dir)
    
    	    # close the output file
            text_file.close()