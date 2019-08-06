#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 12:19:46 2019

@author: jonyoung
"""

import os
from glob import glob
from nipype.interfaces.dcm2nii import Dcm2niix

# set directory to run in
# NB conversion will be run in all files contained within this directory, i.e.
# to convert all files for a single subject, set this to the subject directory
# to convert all files for multiple subjects, set this a directory containing
# the subject directories
# to convert all files for a single subject and a single timepoint, set this to
# the timepoint directory inisde the subject directory, and so forth
top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/renaming_test/'
#top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/PSYU01025/'

# do we want to delete DICOMs if conversion to NIfTI is successful?
delete_dicoms = False

# do we want to rename file according to PSYSCAN naming convention
PSYSCAN_file_naming = True

# initialise dcm2niix 
converter = Dcm2niix()

# list all directories inside the images_dir
dirs = [dirpath for dirpath, dirs, files in os.walk(top_dir)]

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
    
    # list the files, look for existing NIfTIs
    all_files = os.listdir(image_dir)
    NIfTI_files = glob(image_dir + '/*nii*')
    if len(NIfTI_files)  > 0 :
        
        print ('Looking at NIfTI images in ' + image_dir + '.')
        NIfTI_filename = NIfTI_files[0].split('/')[-1]
                
        # check if NIfTI is already in the correct format, beginning 'PSY....'
        if NIfTI_filename[:3] == 'PSY' :
            
            print ('Skipping ' + image_dir + ' as NIfTI images are already named in PSYSCAN format.')
        
        # rename file
        else :
            
            image_dir_bits = image_dir.split('/')
            cmd = 'mv ' + image_dir + '/' + NIfTI_filename + ' ' + image_dir + '/' + '_'.join(image_dir_bits[-4:]) + '.nii.gz'
            
            # escape any double quotes
            cmd = cmd.replace('"', '\\"')
            os.system(cmd)
            
            # also rename JSON, if any
            json_files = glob(image_dir + '/*.json')
            cmd = 'mv ' + json_files[0] + ' ' + image_dir + '/' + '_'.join(image_dir_bits[-4:]) + '.json'
            
            # escape any double quotes
            cmd = cmd.replace('"', '\\"')
            
            os.system(cmd)
            
            # save runtime message
            text_file = open(image_dir + '/NIfTI_renaming.txt', "w")
            text_file.write('Renamed NIfTI and JSON from ' + NIfTI_filename.split('.')[0] + ' to ' + '_'.join(image_dir_bits[7:11]) + '\n')
            text_file.close()
            
            print ('Succesfully renamed NIfTI file in ' + image_dir + '...')
            
            
            
    else :
        
        print ('Skipping ' + image_dir + ' as no images found in NIfTI format.')
            
          
            
            
       