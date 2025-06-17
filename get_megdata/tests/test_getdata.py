#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 14:19:29 2025

@author: jstout
"""

import glob
import pytest
from ..get_testdata import megdata
import os, os.path as op
import shutil

@pytest.fixture(scope='session')
def test_setup(tmp_path_factory):
    out_dir = tmp_path_factory.getbasetemp()
    return megdata(task_type='rest', output_dir=out_dir)


def test_megdata_download(test_setup):
    assert test_setup.task_type =='rest'
    
    gt_downloads = ['sub-ON08710_ses-1_task-rest_run-01_meg.tar.gz',
                 'sub-ON08710_orthohull.tar.gz',
                 'sub-ON08710_fsrecon.tar.gz',
                 'sub-ON08710_mne_outputs.tar.gz',
                 'sub-ON08710_ses-1_anat.tar.gz',
                 'sub-ON08710_ses-1_task-noise_run-01_meg.tar.gz'
                 ]

    # Test Downloads
    test_setup.download_files()
    for dl_file in gt_downloads:
        _tmp = op.join(test_setup.output_dir, dl_file)
        assert op.exists(_tmp), f'{dl_file} did not download'

def test_megdata_untarring(test_setup):        
    # Test untars
    gt_untars = ['sub-ON08710_ses-1_task-rest_run-01_meg',
                 'sub-ON08710_orthohull',
                 'sub-ON08710_fsrecon',
                 'sub-ON08710_mne_outputs',
                 'sub-ON08710_ses-1_anat',
                 'sub-ON08710_ses-1_task-noise_run-01_meg'
                 ]
    
    test_setup.untar_files()
    for ut_file in gt_untars:
        _tmp = op.join(test_setup.output_dir, ut_file)
        assert op.exists(_tmp)
    
def test_megdata_bids_generation(test_setup):
    # Test BIDS creation 
    test_setup.create_output_layout()
    outputs = glob.glob(op.join(test_setup.output_dir, 'BIDS','**'), recursive=True)
    start_idx = len(op.join(test_setup.output_dir,'BIDS')) + 1
    outputs = [i[start_idx:] for i in outputs]
    outputs = [i for i in outputs if i!='']
    outputs = sorted(outputs)
    
    import pysam
    outputlist_fname = op.join(pysam.__path__[0], 'tests','test_outputs', 'bids_outputs_list.txt')
    
    with open(outputlist_fname,'r') as f:
        test_outputs = f.readlines()
    test_outputs = test_outputs[0].split(',')
    test_outputs = sorted(test_outputs)
    
    for out, testout in zip(outputs, test_outputs):
        assert out == testout
        
# test_setup.output_dir =op.expanduser('~/nihmeg_test_data')
# outputs = glob.glob(op.join(test_setup.output_dir, 'BIDS','**'), recursive=True)
# start_idx = len(op.join(test_setup.output_dir,'BIDS')) + 1
# outputs = [i[start_idx:] for i in outputs]
# outputs = [i for i in outputs if i!='']
# outputs = sorted(outputs)
# outputs = ','.join(outputs)
# with open(op.join(pysam.__path__[0], 'tests','test_outputs','bids_outputs_list.txt'), 'w') as f:
#     f.writelines(outputs)
