#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 16:57:04 2019

@author: jonyoung
"""

# import file opeeration and NIfTI utilities
import os
from glob import glob
from nipype.interfaces.dcm2nii import Dcm2niix

def convert_dir_to_NIfTI(image_dir, retry_conversion) :

    # do we want to delete DICOMs if conversion to NIfTI is successful?
    delete_dicoms = False
    
    # do we want to rename file according to PSYSCAN naming convention
    PSYSCAN_file_naming = True
    
    # initialise dcm2niix 
    converter = Dcm2niix()
    
    print image_dir
    
       
    # list the files, look for existing NIfTIs
    all_files = os.listdir(image_dir)
    if len(glob(image_dir + '/*nii*'))  > 0 :
        
        print ('Skipping NIfTI conversion in ' + image_dir + ' as images are already in NIfTI format.')
        
    # check for failed previous attempts at conversion to NIfTI    
    elif os.path.exists(image_dir + '/conversion_error.txt') and not retry_conversion :
        
        print ('Skipping NIfTI conversion in ' + image_dir + ' as it contains a conversion_error.txt file meaning a previous attempt to convert to NIfTI failed.')
        
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
            
            # if there was previously a conversion_error.txt file, remove it
            if os.path.isfile(image_dir + '/conversion_error.txt') :
                
                os.remove(image_dir + '/conversion_error.txt')
            
            print ('Succesfully converted files in ' + image_dir + ' to NIfTI...')
            
        except RuntimeError as e :
            
            # save error message to file
            print ('Failed to convert files in ' + image_dir + ' to NIfTI...')
            print ('See conversion_error.txt for details')
            text_file = open(image_dir + '/conversion_error.txt', "w")
            text_file.write(e.message)
            text_file.close()