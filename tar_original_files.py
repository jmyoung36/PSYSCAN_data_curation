#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:25:49 2019

@author: jonyoung
"""

import os
import tarfile

# (hopefully) one-off script to tar original files in existing curated_data directories

top_dir = '/data/project/PSYSCAN/curated_data/'
original_data_top_dir = '/data/project/PSYSCAN/Raw_data_from_IXICO/PSYSCAN/'

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
        
# loop through the directories
for image_dir in image_dirs :
    
    # skip directory if tarring has already been done
    if os.path.isfile(image_dir + '/original_files.tar.gz') : 
        
        print ('Skipping ' + image_dir + ' as files have already been tared')
        
    else :
    
        print ('tarring original files in '  + image_dir )
        
    #    # split the directory path into components
    #    image_dir_bits = image_dir.split('/')
    #    
    #    # reconstruct PARENT directory of the orginal data directory
    #    subject = image_dir_bits[-5]
    #    timepoint = image_dir_bits[-4]
    #    subcategoryid = image_dir_bits[-2]
    #    version = image_dir_bits[-1]
    #    original_data_parent_dir = original_data_top_dir + subject + '/' + timepoint + '/MRI/' + subcategoryid + '/' + version + '/'
    #    
    #    # search in the parent dir for the original data dir
    #    original_scandate_dir = filter(lambda x: os.path.isdir(original_data_parent_dir + x), os.listdir(original_data_parent_dir))[0]
    #    original_data_dir = original_data_parent_dir + '/' + original_scandate_dir + '/'
    #    print image_dir
    #    print original_data_dir
        # get original data dir from orginal_directory.txt
        fp = open(image_dir + '/original_directory.txt')
        for i, line in enumerate(fp) :
            
            if i == 1 :
                
                original_data_dir = line
                
        # get all the original files
        original_files =  os.listdir(original_data_dir)
        
        # tar all the original files in the image dir
        tar = tarfile.open(image_dir + '/' + 'original_files.tar.gz', "w:gz")
        for name in original_files :
                        
            tar.add(image_dir + '/' + name, name)
                    
        tar.close()
                    
        # remove all archived files that are not NIfTIs
        for original_file in original_files :
                        
            if not '.nii' in original_file : 
                            
                os.remove(image_dir + '/' + original_file)
    
            
    
    
    
    
   