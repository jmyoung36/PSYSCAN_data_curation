#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 11:15:58 2019

@author: jonyoung
"""

import os
from convert_dir_to_NIfTI import convert_dir_to_NIfTI

# set directory to run in
# NB conversion will be run in all files contained within this directory, i.e.
# to convert all files for a single subject, set this to the subject directory
# to convert all files for multiple subjects, set this a directory containing
# the subject directories
# to convert all files for a single subject and a single timepoint, set this to
# the timepoint directory inisde the subject directory, and so forth
top_dir = '/data/project/PSYSCAN/Jonathan/curated_data_symlink_test/'
#top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/PSYU01025/'

# do we want to delete DICOMs if conversion to NIfTI is successful?
delete_dicoms = False

# do we want to rename file according to PSYSCAN naming convention
PSYSCAN_file_naming = True

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
    
    convert_dir_to_NIfTI(image_dir, True)
            