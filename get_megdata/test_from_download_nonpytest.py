#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 13:11:45 2025

@author: jstout
"""

from pysam.sam import SAM, PREPROC_MRI
from pysam.get_testdata import megdata
import mne

dat = megdata(task_type='rest')
dat.getdata()


meg_fname = dat.data.meg_fname 
mri_fname = dat.data.brik_in    
mriprep = PREPROC_MRI(mri_fname=mri_fname,
                      meg_fname=meg_fname, 
                      output_dir=dat.data.orthohull
                      )
mriprep.compute_orthohull()
mriprep.compute_localSpheres()

raw = mne.io.read_raw_ctf(meg_fname, clean_names=True, system_clock='ignore')
src = dat.data.src 
trans_fname = dat.data.trans 
trans = mne.read_trans(trans_fname) 

mriprep.write_fs_src_targetfile(out_fname='src_targets.txt', 
                            src_file=src, trans=trans, raw = raw)


sam = SAM(meg_fname = dat.data.meg_fname,
        cov_fmin = 1, 
        cov_fmax = 110, 
        ori_fmin = 15,
        ori_fmax = 35,
        notch = True,
        cov_fname= 'rest',
        mridir = dat.data.orthohull,
        reg = None, #'*0.01',
        # noise_fmin = 200, 
        # noise_fmax = 300,
        targetfile='src_targets.txt',
        er_meg_fname=dat.data.noise_fname
        )

# Compute Covariance
sam.delete_samdir()
sam._assemble_cmddict()
sam.compute_cov()

# kwargs=dict(TargetFile='src_targets.txt')
sam.compute_wts()

stc = sam.make_stc(src_fname = src, downsamp_sfreq=300)

tmpstc = copy.deepcopy(stc)

tmpstc.crop(10,20)
# tmpstc.plot(subject='sub-ON08710', subjects_dir='/fast2/BIDS/derivatives/freesurfer/subjects')

er_fname = '/fast2/BIDS/sub-ON08710/ses-1/meg/sub-ON08710_ses-1_task-noise_run-01_meg.ds'
er_raw = mne.io.read_raw_ctf(er_fname, system_clock='ignore', preload=True, 
                             clean_names=True)
er_raw.filter(1,110, n_jobs=-1).notch_filter([60,120], n_jobs=-1)

