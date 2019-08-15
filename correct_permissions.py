#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 13:14:49 2019

@author: jonyoung
"""

from os import system
from os.path import isdir
from glob import glob

# set data dir
raw_data_dir = '/data/project/PSYSCAN/curated_data/'

# loop through the top level directories
contents = glob(raw_data_dir + '*')
for item in contents :
    
    # if it is a directory, correct the permissions
    if isdir(item) :
    
        # assemble and execute the command
        print 'correcting ' + item
        cmd = 'chmod -R u=rwX,g=rX,o= ' + item
        system(cmd)
