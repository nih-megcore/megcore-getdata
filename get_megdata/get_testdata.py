#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 10:35:27 2025

@author: jstout
"""

from zipfile import ZipFile
import requests
import os, os.path as op
import tarfile
import shutil
import glob
from types import SimpleNamespace

TEST_DATADIR_URL = 'https://megcore.nih.gov/TEST_DATA/'

#%%
data_keys = ['meg_fname', 'orthohull','fs_recon','mne_outputs', 'noise_fname', 'bids_anat']
# Assign all versions of the data here
# All entries need to be added to data_dict[TASKTYPE][VERSION]
# All new conditions need to be added to data_keys above
data_dict={}
data_dict['rest']= dict()
data_dict['rest']['v1.0.0'] = dict(
                         parent_dir = 'REST_V1_0_0',
                         meg_fname = 'sub-ON08710_ses-1_task-rest_run-01_meg.tar.gz', 
                         orthohull = 'sub-ON08710_orthohull.tar.gz',
                         fs_recon = 'sub-ON08710_fsrecon.tar.gz',
                         mne_outputs = 'sub-ON08710_mne_outputs.tar.gz',
                         noise_fname = 'sub-ON08710_ses-1_task-noise_run-01_meg.tar.gz',
                         out_dir = 'rest/v_1_0_0', 
                         bids_anat = 'sub-ON08710_ses-1_anat.tar.gz', 
                         out_options = ['bids','flat']
                         )
data_dict['hvdata'] = dict()
data_dict['hvdata']['v2.0.0'] = dict(
                        parent_dir = 'HVDATA_V2_0_0',
                        out_dir = 'hvdata/v_2_0_0',
                        out_options = ['flat']
                        
                        )



## Define output structure
outputs = {}
outputs['bids'] = dict(
    topdir = 'BIDS',
    meg_fname = op.join('sub-ON08710', 'ses-1','meg'),
    fs_recon = op.join('derivatives', 'freesurfer', 'subjects'),
    mne_outputs = op.join('derivatives', 'nihmeg', 'sub-ON08710', 'ses-1','meg' ),
    orthohull = op.join('derivatives', 'nihmeg', 'sub-ON08710', 'ses-1','meg'),
    noise_fname = op.join('sub-ON08710', 'ses-1','meg' ),
    bids_anat = op.join('sub-ON08710', 'ses-1','anat')
    )

outputs['single'] = dict(
    topdir = None,
    meg_fname = 'REST',
    fs_recon = 'subjects',
    mne_outputs = '....',
    orthohull = 'REST'
    )



#%%


class megdata():
    def __init__(self, 
                 task_type=None, 
                 output_dir=None, 
                 version=None,
                 get_types=['all'],
                 out_format='bids'
                 ):
        '''
        task_type : 'rest' | 'hvdata'
        get_types = ['meg','ortho','fsrecon','mneout','noise','all']
        
        out_format = bids | flat
        '''
        
        self.task_type = task_type
        self.version = self._get_version(version)
        
        ## Select files to download
        'Set the download_url to be different if not wanted in ~/nihmeg_test_data'
        self.download_urls = self._assemble_download_urls(get_types) 
        
        ## Set output top directory
        if output_dir != None:
            self.output_dir = output_dir #op.join(TEST_DATADIR_URL, fname) 
        else:
            self.output_dir = op.join(op.expanduser(f'~/nihmeg_test_data'))
        if not op.exists(self.output_dir):
            os.makedirs(self.output_dir)  
        
        self.downloaded_fname_list = [] #Initialize the list 
        
        self.output_format = out_format
            
        
        
    def _assemble_download_urls(self, get_types=['meg']):
        if type(get_types) is str:
            get_types = [get_types]
        _out_fname = []
        _conv_dict=dict(meg='meg_fname',
                        ortho='orthohull',
                        fsrecon='fs_recon',
                        mnederiv='mne_outputs',
                        noise='noise_fname',
                        t1nii='bids_anat',
                        )
        
        # Verify that names are valid
        _remote_name_dict = data_dict[self.task_type][self.version]
        if 'all' in [i.lower() for i in get_types]:
            get_types = list(_conv_dict.keys())
        for i in get_types:
            if i not in list(_conv_dict.keys()):
                raise ValueError(f'Specified type ({i}) is not in available types: {list(_conv_dict.keys())}')
        
        # Generate Relative Paths
        for _type in get_types:
            _remote_key = _conv_dict[_type] 
            _out_fname.append(_remote_name_dict[_remote_key])
        
        # Prepend path
        _out_fname = [op.join(TEST_DATADIR_URL, _remote_name_dict['parent_dir']  ,i) for i in _out_fname]
        
        return _out_fname
        
        
    def _get_version(self, version):
        'Logic to assess specified version vs latest version'
        if version!=None:
            assert version in data_dict[self.task_type].keys(), f"That version does not exists, must be in :{data_dict[self.task_type].keys()}"
        
        if version==None:
            num_vers = data_dict[self.task_type].keys().__len__()
            if num_vers > 1:
                #Pick the most recent version
                version = sorted(data_dict[self.task_type].keys())[-1]
            elif num_vers == 1:
                version = list(data_dict[self.task_type].keys())[0]
            elif num_vers == 0:
                raise ValueError(f'There are no versions for {self.task_type}. Pick from task_type in {list(data_dict.keys())}')
        return version
    
    def _populate_data_paths(self):
        ##FIX!! -- This won't work if the data isn't present, since it searches using glob
        
        fmt_outputs = outputs[self.output_format] #Selected between bids or single
        topdir = op.join(self.output_dir, fmt_outputs['topdir'])
        bidsout = op.join(topdir, fmt_outputs['mne_outputs'])
        self.data = SimpleNamespace(subjects_dir = op.join(topdir, fmt_outputs['fs_recon']), 
                                    meg_fname = glob.glob(op.join(topdir, fmt_outputs['meg_fname'], f'*{self.task_type}*.ds'))[0],
                                    fwd = glob.glob(op.join(bidsout, '*_fwd.fif'))[0],
                                    src = glob.glob(op.join(bidsout, '*_src.fif'))[0],
                                    trans = glob.glob(op.join(bidsout, '*_trans.fif'))[0],
                                    bem = glob.glob(op.join(bidsout, '*_bem.fif'))[0],
                                    orthohull = glob.glob(op.join(bidsout, '*_orthohull'))[0],
                                    brik_in = glob.glob(op.join(bidsout, '*_orthohull','*T1w+orig.BRIK'))[0],
                                    noise_fname = glob.glob(op.join(topdir, fmt_outputs['noise_fname'],'*-noise*.ds'))[0],
                                    bidsT1w = glob.glob(op.join(topdir, fmt_outputs['bids_anat'], '*.nii.gz'))[0]
                                                        
                                    )
                                    
        
    def download_files(self):
        assert hasattr(self, 'download_urls'), 'The download_urls tag has not been filled - this appears to be an error'
        assert len(self.download_urls) > 0,  'There is nothing to download - this appears to be an errror'
        for i in self.download_urls:
            self._download_file(i)
            
    def untar_files(self):
        assert len(self.downloaded_fname_list) > 0, 'There is nothing to untar'
        for fname in self.downloaded_fname_list:
            self._untar(fname)
        
    def _download_file(self, fname_url):
        try:
            response = requests.get(fname_url, stream=True)
            response.raise_for_status()  
            
            output_tarfile = self._get_output_name(fname_url)

            with open(output_tarfile, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded '{fname_url}' successfully.")
            
            self.downloaded_fname_list.append(output_tarfile)

        except requests.exceptions.RequestException as e:
            print(f"Error downloading '{fname_url}': {e}")
    
    def _get_output_name(self, fname_url):
        _base_fname =  op.basename(fname_url)
        return op.join(self.output_dir, _base_fname)
        
    
    def _untar(self, fname):
        output_fname = fname.replace('.tar.gz', '')
        with tarfile.open(fname, 'r') as tar:
            tar.extractall(path=output_fname)
        print(f'Untarred file: {output_fname}')
        os.remove(fname)

    def _move_dir(self, data_type, topdir):
        _in_dict = data_dict[self.task_type][self.version]
        _out_dict = outputs[self.output_format]
        _dirname = _in_dict[data_type]
        indir = op.join(self.output_dir, _dirname).replace('.tar.gz','')
        indata = glob.glob(op.join(indir,'*'))
        outdir = op.join(self.output_dir, _out_dict['topdir'], _out_dict[data_type])
        
        if op.basename(indata[0]) == op.basename(outdir):
            indata = glob.glob(op.join(indir, '*','*')) #FIX - This may not always work
        if not op.exists(outdir):
            os.makedirs(outdir)
        for data in indata:
            shutil.move(data, outdir)
        if len(os.listdir(indir))==0:
            shutil.rmtree(indir)
        elif os.listdir(indir) == ['meg']:
            shutil.rmtree(indir)
        elif os.listdir(indir) == ['anat']:
            shutil.rmtree(indir)
        
        
    def create_output_layout(self):
        output_dict = outputs[self.output_format]
        
        if not op.exists(op.join(self.output_dir,output_dict['topdir'])):
            os.mkdir(op.join(self.output_dir,output_dict['topdir']))
        
        for key in data_dict[self.task_type][self.version].keys():
            if key not in data_keys:
                continue
            self._move_dir(key, output_dict['topdir'])
            
    def getdata(self):
        '''
        Run the following steps to fully organize the data
        1) download_files
        2) untar_files
        3) create_output_layout
        4) _populate_data_paths

        Returns
        -------
        None.

        '''
        
        self.download_files()
        self.untar_files()
        self.create_output_layout()
        self._populate_data_paths()
        
        
        
        
     
    


    
    
