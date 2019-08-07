#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 11:15:58 2019

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
top_dir = '/data/project/PSYSCAN/curated_data_new/'
#top_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/PSYU01025/'

# do we want to delete DICOMs if conversion to NIfTI is successful?
delete_dicoms = False

# do we want to rename file according to PSYSCAN naming convention
PSYSCAN_file_naming = True

# initialise dcm2niix 
converter = Dcm2niix()

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
    
    print image_dir
    
    # list the files, look for existing NIfTIs
    all_files = os.listdir(image_dir)
    if len(glob(image_dir + '/*nii*'))  > 0 :
        
        print ('Skipping ' + image_dir + ' as images are already in NIfTI format.')
        
    # check for failed previous attempts at conversion to NIfTI    
    elif os.path.exists(image_dir + '/conversion_error.txt') :
        
        print ('Skipping ' + image_dir + ' as it contains a conversion_error.txt file meaning a previous attempt to convert to NIfTI failed.')
        
    # if the directory has no NIfTIs, try to convert the contents
    # write back into image dir
    else :
        
        print ('Attempting to convert files in ' + image_dir + ' to NIfTI...')
        
        try:
            
            # get list of files so we know what to delete
            # remove any txt files from the list so they will not be deleted
            files_to_convert = all_files
            files_to_convert = filter(lambda x: not x[-4:] == '.txt', files_to_convert)
            
            # attempt to convert the contents of the directory
            print image_dir
            converter.inputs.source_dir = image_dir
            converter.inputs.output_dir = image_dir

            # if PSYSCAN_file_naming is true, get subject, timepoint, modality & version # from directory
            # now include subcategoryid too
            if PSYSCAN_file_naming :
                
                image_dir_bits = image_dir.split('/')
                subject = image_dir_bits[3]
                timepoint = image_dir_bits[4]
                modality = image_dir_bits[5]
                subcategoryid = image_dir_bits[6]
                version = image_dir_bits[7]
                
                # build filename
                s = '_'
                converter.inputs.out_filename = s.join(image_dir_bits[-5:])
            
            
            Dcm2niix_output = converter.run()
            runtime_message = Dcm2niix_output.runtime.stdout
            
            # delete DICOMS if set to do so
            if delete_dicoms :  
                text_file = open(image_dir + '/removed_files.txt', "w")
                text_file.write('Removed the following ' + str(len(files_to_convert)) + ' files:\n')
                for file_to_remove in files_to_convert :
                    
                    os.remove(image_dir + '/' + file_to_remove)
                    text_file.write(file_to_remove + '\n')
                    
                text_file.close()
                
            # save runtime message
            text_file = open(image_dir + '/conversion_stdout.txt', "w")
            text_file.write(runtime_message)
            text_file.close()
            
            print ('Succesfully converted files in ' + image_dir + ' to NIfTI...')
            
        except RuntimeError as e :
            
            # save error message to file
            print ('Failed to convert files in ' + image_dir + ' to NIfTI...')
            print ('See conversion_error.txt for details')
            text_file = open(image_dir + '/conversion_error.txt', "w")
            text_file.write(e.message)
            text_file.close()
            