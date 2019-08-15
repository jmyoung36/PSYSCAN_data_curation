#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 12:11:23 2019

@author: jonyoung
"""

# (hopefully) one-off script to fill gaps (empty folders) in curated_data
# due to not copying files when cp has too many arguments

from os import system, listdir, remove, walk
from os.path import isdir
from convert_dir_to_NIfTI import convert_dir_to_NIfTI


top_dir = '/data/project/PSYSCAN/curated_data/'

# settings:
# do we want to convert to NIfTI?
convert_to_NIfTI = True
# do we want to tar original files?
archive_original_files = False

print 'looking for directories'

# list all directories inside the images_dir
dirs = [dirpath for dirpath, dirs, files in walk(top_dir)]

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
    
    # get a list of files
    existing_files = listdir(image_dir)
    
    # remove any files ending in .txt
    existing_data_files = filter(lambda x: not x[-4:] == '.txt', existing_files)
    
    # if there are no data files, re-copy them
    if len(existing_data_files) == 0 :
        
        print 'Copying image files to ' + image_dir + ' as they are currently missing'
        
        # first get the original directory to copy files from
        fp = open(image_dir + '/original_directory.txt')
        for i, line in enumerate(fp) :
        
            if i == 1 :
            
                raw_data_dir = line
                
        # get list of original files
        original_files = listdir(raw_data_dir)
        
        # copy files from file_path to output_dir
        # use find to chop list of files into manageable chunks to avoid 
        # giving cp too many arguments
        # adapted from https://askubuntu.com/questions/217764/argument-list-too-long-when-copying-files
        #cmd = 'cp ' + raw_data_dir + file_path + '/* ' + output_dir + '/'
        cmd = "find " + raw_data_dir + " -maxdepth 1 -name '*' -exec cp -t " + image_dir + '/' + " {} +"
        system(cmd)
        
        # add a note saying where the files came from
        text_file = open(image_dir + '/original_directory.txt', "w")
        text_file.write('Files were copied from the following directory:\n')
        text_file.write(raw_data_dir)
        text_file.close()
        
        # convert to NIfTI?
        if convert_to_NIfTI :
            
            convert_dir_to_NIfTI(image_dir, True)
            
    else :
        
        print 'Skipping ' + image_dir + ' as it already contains image files'
       
    