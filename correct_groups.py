#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:16:34 2019

@author: jonyoung
"""

from os import system
from os.path import isdir
from glob import glob

# set data dir
raw_data_dir = '/data/project/PSYSCAN/Raw_data_from_IXICO/PSYSCAN/'

# loop through the top level directories
contents = glob(raw_data_dir + '*')
for item in contents :
    
    # if it is a directory, correct the permissions
    if isdir(item) :
    
        # assemble and execute the command
        print 'correcting ' + item
        cmd = 'chgrp -R psyscan ' + item
        system(cmd)
