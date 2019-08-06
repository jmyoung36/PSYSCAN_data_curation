#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 13:57:33 2018

@author: jonyoung
"""

import numpy as np
import pandas as pd
import nibabel as nib
from hashlib import md5
import os

# list which keys differ between two dicts, if any
def find_dict_differences(dict_1, dict_2) :
    
    # list of differing keys
    differing_keys = []
    
    # first get sets of keys
    keys_set_1 = set(dict_1.keys())
    keys_set_2 = set(dict_2.keys())
    
    # find set difference of keyes, if any
    key_set_diff = keys_set_1.symmetric_difference(keys_set_2)
    if len (key_set_diff) > 0 :
        
        differing_keys.append(list(differing_keys))
        
    # go through and find mismatched values
    common_key_set = keys_set_1.intersection(keys_set_2)
    for key in common_key_set :
            
        if not dict_1[key] == dict_2[key] :
                
            differing_keys.append(key)
            
    return differing_keys
    
# compare dictionaries
def compare_dicts(filenames, header_dicts) :
    
    # hold lists: different groups of files, and keys which differ
    filename_groups = []
    distinct_header_dicts = []
    differing_keys = []
    
    # get the first dictionary
    header_dict_1 = header_dicts[0]
    
    # 1st group contains (at least) the first file
    filename_groups.append(filenames[0])
    distinct_header_dicts.append(header_dicts[0])
    
    # roll through the remaining files
    for i in range(1, len(filenames)) :
        
        # get the header dict and file
        test_filename = filenames[i]
        test_header_dict = header_dicts[i]
        
        # compare against all header dict groups
        for comparison_dict in distinct_header_dicts :
            
            # if dictionaries are identical, just continue
            if header_dict_1 == comparison_dict :
                
                continue
            
            # if they are not
            else :
                
                # add a new filename group and distinct header dict
                filename_groups.append(test_filename)
                distinct_header_dicts.append(test_header_dict)
                
                # find the keys where the dicts are different
                differing_keys.append(find_dict_differences(test_header_dict, comparison_dict))
                
    # tidy up any duplicates in differing keys
    differing_keys = list(set(differing_keys))
    
    # return groups and differing keys
    return filename_groups, differing_keys
                                            
# set directory to look for dupes in   
subject_duplicate_dir = '/home/jonyoung/IoP_data/Projects/TrialTrackerDownload/images/sMRI_duplicates_tidied/PSYF02001/'

# set verbose option
# if true, list all members of each group
verbose = True

# find duplicate image files within the subject duplicate dir              
NIfTI_files = []
for root, dirs, files in os.walk(subject_duplicate_dir) :
        
    for filename in files :
            
        # add any zipped niftis to the list                
        if filename.split('.')[-2]  == 'nii' and filename.split('.')[-1]  == 'gz' :
                
            NIfTI_files.append(os.path.join(root, filename))            
                
# make a DF from the list of files
NIfTI_data = pd.DataFrame()
NIfTI_files = pd.Series(NIfTI_files)
NIfTI_data['filenames'] = NIfTI_files

# empty list for each images (hash of) data array and header info
data_array_hashes = []
header_dicts = []

# warn if only one file
if len(NIfTI_files) == 1 :
    
    print ('WARNING: only one image file found. Expected at least two files.')


# roll through the files
for index, row in NIfTI_data.iterrows():
   
    # read in the image
    im = nib.load(row['filenames'])
    
    # get data and hash it
    im_data = im.get_data()
    m = md5()
    m.update(im_data.flatten())    
    data_array_hashes.append(m.hexdigest())
    #check[index, :] = im_data.flatten()
    
    # add header to list
    header_dict = dict(im.header)
    header_dicts.append(header_dict)

    
NIfTI_data['data array hash'] = pd.Series(data_array_hashes)
NIfTI_data['header info'] = pd.Series(header_dicts)

# group by data array
NIfTI_data_grp = NIfTI_data.groupby('data array hash')

# if we have one group
if len(NIfTI_data_grp) == 1:
    
    print 'All duplicates have identical data array'
    print 'Now checking metadata...'
    
    metadata_groups, differing_keys = compare_dicts(NIfTI_data['filenames'].tolist(), NIfTI_data['header info'].tolist())
    
    # print out examplar and differing keys for each group
    if len(metadata_groups) == 1 :
        
        print 'All images have identical metadata'
        print 'Example file is ' + metadata_groups[0]
        
    else :
        
        n_metadata_groups = len(metadata_groups)
        print 'Images have different metadata'
        print '%d different versions of the metadata exist' % (n_metadata_groups)
        
        for i, metadata_group in enumerate(metadata_groups) :
            
            if verbose :
                
                print 'Files for metadata group %d are:'
                print metadata_group
                
            else :    
            
                print 'Example file for metadata group %d is ' + metadata_group[0] % (i)
        
        print 'Check the following header fields:'
        print differing_keys
    
    
else :
    
    n_groups = len(NIfTI_data_grp)
    print '%d different data arrays exist for the %d duplicate image files' % (n_groups, len(NIfTI_files))
    
    # iterate through the data array groups
    i = 0
    for name, group in NIfTI_data_grp :
        
        filenames = group['filenames'].tolist()
        
        # if the data array group contains only 1 file
        if len(group) == 1 :
            
            print 'data array group %d contains only 1 file' % (i+1)
            print 'data array group is ' + filenames[0]
            
        # if there are multiple files in the data array group
        else :
            
            print 'data array group %d contains %d files' % (i+1, len(group))
            print 'Now checking metadata for this data array group...'
            
            # compare the metadata
            metadata_groups, differing_keys = compare_dicts(group['filenames'].tolist(), group['header info'].tolist())
            
            # if only 1 metadata group
            if len(metadata_groups) == 1 :
        
                print 'All images in the data array group have identical metadata'                
                if verbose :
                    
                    group_filenames = group['filenames'].tolist()
                    print 'Files for data group %d are:' % (i+1)
                    for group_filename in group_filenames :
                        
                        print group_filename
                    
                else :
                    
                    print 'Example file is ' + metadata_groups[0]
                    
                    
                
            else :
        
                n_metadata_groups = len(metadata_groups)
                print 'Images in the data array group have different metadata'
                print '%d different versions of the metadata exist' % (n_metadata_groups)
        
                for j, metadata_group in enumerate(metadata_groups) :
                    
                    if verbose :
                        
                        print 'Files for metadata group %d are:' + metadata_group % (j+1)
                        print metadata_group
                        
                    else :
            
                        print 'Example file for metadata group %d is ' + metadata_group % (j+1)
        
                print 'Check the following header fields:'
                print differing_keys
            
        i = i + 1
            
    

