#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 12 13:57:33 2018

@author: jonyoung
"""

import numpy as np
import pandas as pd
from hashlib import md5
import os
import pydicom as dicom
from glob import glob
from natsort import natsorted
from dicom_numpy import combine_slices
import dcmstack

# get a 3-d array of DICOM data, and the associated metadata
def get_DICOM_data(DICOM_dir, keys='minimal') :
    
    # find DICOM files in the specified directory
    DICOM_file_paths = glob(DICOM_dir + '*.dcm')
    DICOM_file_paths = natsorted(DICOM_file_paths)
    
    # initialise metadata dictionary
    metadata = {}
    
    # hard code basic dicom tags
    minimal_keys= ['EchoTime', 'RepetitionTime', 'AcquisitionNumber', 'SeriesNumber', 'InversionTime', 'FlipAngle', 'ImageOrientationPatient', 'ContentTime', 'ProtocolName', 'InstanceNumber', 'Rows', 'TriggerTime', 'AcquisitionTime', 'InPlanePhaseEncodingDirection', 'SeriesInstanceUID', 'Columns', 'PixelSpacing']
    
    ############################## DICOM_NUMPY ################################
    
    datasets = [dicom.read_file(f) for f in DICOM_file_paths]
    
    # use dcmstack metadata if possible
    dcmstack_metadata = False
    
    try :
    
        DICOM_data, DICOM_affine = combine_slices(datasets)
        
    except Exception, e :
        
        print e
        print 'WARNING: could not assemble valid DICOM image for ' + DICOM_dir
        DICOM_data = np.array(-1)
        DICOM_affine = 'WARNING: could not get affine matrix'
        print 'Trying alternative method to construct DICOM image'
        
        ######################## DICOM STACK ##################################
        
        # read into stack of data
        DICOM_stack = dcmstack.DicomStack()
        
        try :
            
            for DICOM_file_path in DICOM_file_paths :
            
                DICOM_file = dicom.read_file(DICOM_file_path)
                DICOM_stack.add_dcm(DICOM_file)
        
            # get data and affine
            DICOM_data = DICOM_stack.get_data()
            DICOM_affine = DICOM_stack.get_affine()
            
            # get a nifti wrapper for the DICOM stack
            nii_wrp = DICOM_stack.to_nifti_wrapper()
            
            if keys == 'minimal' :
                
                # just get minimal keys from the stack
                keys = DICOM_stack.minimal_keys
            
            elif keys == 'all' :
                
                # get all metadata keys
                keys = nii_wrp.meta_ext.get_keys()
                
            else :
                    
                print ('WARNING: keys arguments must be set to "minimal" to search for a default set of basic DICOM tags, or "all" to search for all tags associated with each image.')
                
            # build dictionary of key-value pairs for the metadata
            for key in keys :
                
                metadata.update({key: nii_wrp.get_meta(key)})
                
            dcmstack_metadata = True
                
        except Exception, e :
                
            print e
            print 'WARNING: could not assemble valid DICOM image for ' + DICOM_dir + 'with alternative method'
            DICOM_data = np.array(-1)
            DICOM_affine = 'WARNING: could not get affine matrix'
    
    # if we do not have metadata from dcmstack, at least get it from first slice
    if not dcmstack_metadata :
    
        # build dictionary of key-value pairs for the metadata
        if keys ==  'minimal' : 
        
            for key in minimal_keys :
            
                try :
            
                    metadata.update({key: datasets[0].data_element(key).value})
                
                except KeyError, e:
                
                    print e
                    print 'WARNING: did not find the following expected key in minimal keyset: ' + key
                    metadata.update({key: None})
                    
        elif keys == 'all' :
            
            # get metadata from first dataset
            keys = datasets[0].dir()
            
            for key in keys :
    
                metadata.update({key: datasets[0].data_element(key).value})
                
        else :
            
            print ('WARNING: keys arguments must be set to "minimal" to search for a default set of basic DICOM tags, or "all" to search for all tags associated with each image.')
        
        
    
    ###################### DCMSTACK ###########################################
    
    # read into stack of data
#    DICOM_stack = dcmstack.DicomStack()
#    for DICOM_file_path in DICOM_file_paths :
#        DICOM_file = dicom.read_file(DICOM_file_path)
#        DICOM_stack.add_dcm(DICOM_file)
#        
#    # get data and affine
#    DICOM_data = DICOM_stack.get_data()
#    DICOM_affine = DICOM_stack.get_affine()
#    
#    # get a nifti wrapper for the DICOM stack
#    nii_wrp = DICOM_stack.to_nifti_wrapper()
#    
#    if keys == 'minimal' :
#        
#        # just get minimal keys from the stack
#        keys = DICOM_stack.minimal_keys
#    
#    elif keys == 'all' :
#        
#        # get all metadata keys
#        keys = nii_wrp.meta_ext.get_keys()
#        
#    else :
#            
#        print ("keys argument must be 'minimal' (default) to return a minimal set of metadata that can be expected to be present in all \
#               DICOM images, or 'all' to return all metadata items present in the image.")
#        
#   #  build dictionary of key-value pairs for the metadata
#    for key in keys :
#        
#        metadata.update({key: nii_wrp.get_meta(key)})
#
#    
    return DICOM_data, DICOM_affine, metadata
    

# compare dictionaries
def compare_dicts(filenames, header_dicts) :
    
    # hold lists: groups of files, groups of metadata dicts, differing keys, and keys with differing values
    filename_groups = []
    metadata_dicts = []
    all_differing_keys = []
    all_differing_value_keys = []
    
    # get the first dictionary
    header_dict_1 = header_dicts[0]
    metadata_dicts.append(header_dict_1)
    
    # 1st group contains (at least) the first file
    filename_groups.append([filenames[0]])
    
    # roll through the other files
    for i in range(1, len(filenames)) :
        
        # get the header dict and file
        test_filename = filenames[i]
        test_header_dict = header_dicts[i]
        
        # compare the header dictionary against all existing groups of header dictionaries
        matched = False
        for j, comparison_header_dict in enumerate(metadata_dicts):
            
            # if metadata dictionaries are identical, add the filename to the group of the comparison dict
            if test_header_dict == comparison_header_dict :
                
                filename_groups[j].append(test_filename)
                matched = True
                break
            
        # if no match is found, add a new group
        if not matched :
                
            filename_groups.append([test_filename])
            metadata_dicts.append(test_header_dict)
                
            # find where the dictionaries differ
            # first check for keys that are in one dict but not another
            key_set_diff = list(set(test_header_dict.keys()).symmetric_difference(set(comparison_header_dict.keys())))
            
            # find any keys which have differing values
            common_keys = set(test_header_dict.keys()).intersection(set(comparison_header_dict.keys()))
            differing_value_keys = []
            for common_key in common_keys :
                
                if not test_header_dict[common_key] == comparison_header_dict[common_key] :
                    
                    differing_value_keys.append(common_key)
                
                
        all_differing_keys = all_differing_keys + key_set_diff
        all_differing_value_keys = all_differing_value_keys + differing_value_keys
                
    # tidy up any duplicates in differing keys or values
    all_differing_keys = list(set(all_differing_keys))
    all_differing_value_keys = list(set(all_differing_value_keys))
    
    # return groups and differing keys
    return filename_groups, all_differing_keys, all_differing_value_keys
                                          
# set directory to look for dupes in   
subject_duplicate_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/PSYF02001/MR-ep2d_bold_TR1980/'

# set verbose option
# if true, list all members of each group
verbose = True

# find directories containing duplicate image files within the subject duplicate dir              
DICOM_dirs = []
for root, dirs, files in os.walk(subject_duplicate_dir) :
        
    for directory in dirs :
            
        # add any directories containing DICOMs to the list   
        full_dir = root + '/' + directory + '/'
        # remove common element of directories, ie original duplicate directory, to make shorter discriminative 
        # directory names for convenience, just prefix with original directory when reading files etc
        disc_dir = full_dir.replace(subject_duplicate_dir, '')             
        if len(glob(full_dir + '*.dcm')) > 0 :
                
            #DICOM_dirs.append(os.path.join(root, filename))
            DICOM_dirs.append(disc_dir)
                
# make a DF from the list of files
DICOM_data = pd.DataFrame()
DICOM_dirs = pd.Series(DICOM_dirs)
DICOM_data['DICOM dirs'] = DICOM_dirs

# empty list for each images (hash of) data array and header info
data_array_hashes = []
header_dicts = []
affine_matrices = []

# warn if only one file
if len(DICOM_dirs) == 1 :
    
    print ('WARNING: only one directory containing images file found. Expected at least two such directories.')


# roll through the files
for index, row in DICOM_data.iterrows():
   
    # read in the image data
    DICOM_array_data, DICOM_affine, metadata = get_DICOM_data(subject_duplicate_dir + row['DICOM dirs'], keys='all')
    
    # hash data array if it is there
    if np.array_equal(DICOM_array_data, np.array(-1)) :
        
        data_array_hashes.append('WARNING: could not assemble valid DICOM image')
        
    else :
        
        m = md5()
        m.update(DICOM_array_data.flatten())    
        data_array_hashes.append(m.hexdigest())
    #check[index, :] = im_data.flatten()
    
    # add header to list
    header_dict = metadata
    header_dicts.append(header_dict)
    
    # add affine to list
    affine_matrices.append(DICOM_affine)

#  add the new lists to the     
DICOM_data['data array hash'] = pd.Series(data_array_hashes)
DICOM_data['header info'] = pd.Series(header_dicts)
DICOM_data['affine matrices'] = pd.Series(affine_matrices)

# group by data array
DICOM_data_grp = DICOM_data.groupby('data array hash')

# if we have one group
if len(DICOM_data_grp) == 1:
   
    affines = DICOM_data['affine matrices'].tolist()
        
    if type(affines[0]) == str and affines[0] == 'WARNING: could not get affine matrix' :
         
        print 'WARNING: In all DICOM directories, a valid DICOM could not be assembled'
   
    else :
    
        print 'All duplicates have identical data array'
        
    print 'Now checking metadata...'
    
    metadata_groups, differing_keys, differing_value_keys = compare_dicts(DICOM_data['DICOM dirs'].tolist(), DICOM_data['header info'].tolist())
    
    # print out examplar and differing keys for each group
    if len(metadata_groups) == 1 :
        
        print 'All images have identical metadata'
        print 'Example file directory is ' + subject_duplicate_dir + metadata_groups[0][0]
        
    else :
        
        n_metadata_groups = len(metadata_groups)
        print 'Images have different metadata'
        print '%d different versions of the metadata exist' % (n_metadata_groups)
        
        for i, metadata_group in enumerate(metadata_groups) :
            
            if verbose :
                
                print 'File directories for metadata group %d are:' % (i+1)
                print map(lambda x: subject_duplicate_dir + x, metadata_group)
                
            else :    
            
                print 'Example file directory for metadata group %d is ' + subject_duplicate_dir + metadata_group[0] % (i)
                
        if len(differing_keys) > 0 :
            print 'Check the following header field(s) as they are present in some images and not in others:'
            print differing_keys
        if len(differing_value_keys) > 0 :    
            print 'Check the following header field(s) as they have different values in different images:'
            print differing_value_keys
    
    
else :
    
    n_groups = len(DICOM_data_grp)
    print '%d different data arrays exist for the %d duplicate DICOM directories' % (n_groups, len(DICOM_dirs))
    
    # iterate through the data array groups
    i = 0
    for name, group in DICOM_data_grp :
        
        filenames = group['DICOM dirs'].tolist()
        affines = group['affine matrices'].tolist()
        if type(affines[0]) == str and affines[0] == 'WARNING: could not get affine matrix' :
            
            print 'WARNING: data array group %d contains directory/directories where a valid DICOM could not be assembled' % (i+1)
            
        # if the data array group contains only 1 file
        if len(group) == 1 :
            
            print 'data array group %d contains only 1 DICOM directory' % (i+1)
            print 'data array group is ' + filenames[0]
            
        # if there are multiple files in the data array group
        else :
            
            print 'data array group %d contains %d DICOM directories' % (i+1, len(group))
            print 'Now checking metadata for this data array group...'
            
            # compare the metadata
            metadata_groups, differing_keys, differing_value_keys = compare_dicts(group['DICOM dirs'].tolist(), group['header info'].tolist())
            
            # if only 1 metadata group
            if len(metadata_groups) == 1 :
        
                print 'All images in the data array group have identical metadata'                
                if verbose :
                    
                    group_filenames = group['filenames'].tolist()
                    print 'File directories for data group %d are:' % (i+1)
                    for group_filename in group_filenames :
                        
                        print group_filename
                    
                else :
                    
                    print 'Example file directory is ' + metadata_groups[0]
                    
                    
                
            else :
        
                n_metadata_groups = len(metadata_groups)
                print 'Images in the data array group have different metadata'
                print '%d different versions of the metadata exist' % (n_metadata_groups)
        
                for j, metadata_group in enumerate(metadata_groups) :
                    
                    if verbose :
                        
                        print 'File directories for metadata group %d are:' % (j+1)
                        print metadata_group
                        
                    else :
            
                        print 'Example file for metadata group %d is ' + metadata_group % (j+1)
                if len(differing_keys) > 0 :        
                    print 'Check the following header field(s) as they are present in some images and not in others:'
                    print differing_keys
                if len(differing_value_keys) > 0 :
                    print 'Check the following header field(s) as they have different values in different images:'
                    print differing_value_keys
            
        i = i + 1
            
    

