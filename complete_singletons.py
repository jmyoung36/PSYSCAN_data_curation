#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 14:39:15 2019

@author: jonyoung
"""

import pandas as pd
from os import listdir
from os.path import isdir

# top level directory to look for image dirs in
top_dir = '/data/project/PSYSCAN/Raw_data_from_IXICO/PSYSCAN/'

# find file listing dirs here
file_listings_dir = '/home/k1511004/Projects/PSYSCAN_data_curation/'
#file_listings_dir = '/home/jonyoung/IoP_data/Projects/PSYSCAN_data_curation/'

# set modality
modality = 'sMRI'

# read in the listings
file_listing = pd.read_csv(file_listings_dir + modality + '_singleton_files.csv', header=None)
file_listing.columns = ['modality', 'subjectid', 'TT file path']
IoP_file_paths = []
for i in range(len(file_listing)) :
    
    # create parent directory for the image directory
    TT_file_path = file_listing['TT file path'].iloc[i]
    IoP_parent_path = top_dir + TT_file_path
    
    if isdir(IoP_parent_path) : 
        
        IoP_file_path = IoP_parent_path + listdir(IoP_parent_path)[0]
        
    else :
        
        IoP_file_path = None
        
    IoP_file_paths.append(IoP_file_path)
        
# add the new paths as a column
file_listing['IoP file path'] = pd.Series(IoP_file_paths)

# save the results
file_listing.to_csv(file_listings_dir + modality + '_singleton_files_IoP.csv')

