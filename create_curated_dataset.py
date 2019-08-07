#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:56:46 2019

@author: jonyoung
"""

# import what we need
import pandas as pd
from os import system
from os.path import isdir

# set directories
raw_data_dir = '/data/project/PSYSCAN/Raw_data_from_IXICO/'
curated_data_dir = '/data/project/PSYSCAN/curated_data_new/'
metadata_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/'
#metadata_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/'

# dict to translate qc_serieslabel to desired directory names
# EXPAND THIS!!!
qc_serieslabel_dict = {'RS-fMRI':'fMRI', '3D T1W':'sMRI'}

# read in the extract spreadsheet
extract = pd.read_excel(metadata_dir + 'PSYSCAN_spreadsheet_for_Harddisk-test-2.xlsx', keep_default_na=False)

# apply any required filters
extract = extract[extract['active'] == True]
extract = extract[extract['qc_metadataqcgrade'].isin(['Fail', 'N/A', 'NA', 'Advisory', 'Pass'])]
# ...et cetera

# extract the file paths and qc_serieslabels
file_paths = extract['filepath'].tolist()
qc_serieslabels = extract['qc_serieslabel'].tolist()

# initialise a list for any missing directories we may find
missing_dirs = []

#print file_paths

# loop through the file paths
for i, file_path in enumerate(file_paths) :
    
    # check the file path exists
    if isdir(raw_data_dir + file_path) :
        
        #print raw_data_dir + file_path
        
        # split the file path so we can extract subject id, timepoint etc
        file_path_bits = file_path.split('/')
        subjectid = file_path_bits[1]
        timepoint = file_path_bits[2]
        subcategoryid = file_path_bits[4]
        version = file_path_bits[5]
        
        # look up the qc_serieslabel
        qc_serieslabel = qc_serieslabels[i]
        modality = qc_serieslabel_dict[qc_serieslabel]
        
#        print file_path
#        print 'subjectid: ' + subjectid
#        print 'timepoint: ' + timepoint
#        print 'version: ' + version
#        print 'qc_serieslabel: ' + qc_serieslabel
#        print 'modality: ' + modality     
        
        # build an output directory location 
        output_dir = curated_data_dir + subjectid + '/' + timepoint + '/' + modality + '/' + subcategoryid + '/' + version
        
        # only proceed if output directory does not already exist
        # so creation of the curated dataset is incremental rather than from scratch each time
        if not isdir(output_dir) :
            
            # create output directory
            cmd = 'mkdir -p ' + output_dir
            system(cmd)
            
            # copy files from file_path to output_dir
            cmd = 'cp ' + raw_data_dir + file_path + '/* ' + output_dir + '/'
            system(cmd)
        
            # add a note saying where the files came from
            text_file = open(output_dir + '/original_directory.txt', "w")
            text_file.write('Files were copied from the following directory:\n')
            text_file.write(raw_data_dir + file_path)
            text_file.close()
        
        
    else :
        
        missing_dirs.append(file_path)
        
# print and write to text file the missing directories
# add a note saying where the files came from
if len(missing_dirs) > 0 :
    
    text_file = open(curated_data_dir + '/missing_directories.txt', "w")  
    text_file.write('Missing directories:\n')   
    print 'Missing directories:'
    
    for missing_dir in missing_dirs :
    
        print missing_dir
        text_file.write(raw_data_dir + missing_dir + '\n')
        
    text_file.close()
    
