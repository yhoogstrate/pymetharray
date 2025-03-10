#!/usr/bin/env python

# Lib
from beartype import beartype
import os
import logging
from pathlib import Path, PurePath
import pandas as pd
import re
from _io import BufferedReader
import deprecation

# App
from ..models import Channel, SigSet, ArrayType
from ..utils import get_file_object, reset_file
from ..utils.progress_bar import *
from ..files import Manifest, manifest_cache, IdatDataset


__all__ = ['SampleSheet']


formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)s:%(name)s:%(message)s', datefmt="%H:%M:%S")

handler = logging.StreamHandler()
handler.setFormatter(formatter)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel( logging.DEBUG ) # Should not be located in this class
LOGGER.handlers.clear()
LOGGER.addHandler(handler)



class SampleSheet():
    """Validates and parses an Illumina sample sheet file.

    Arguments:
        filepath_or_buffer {file-like} -- the sample sheet file to parse.
        dir_path {string or path-like} -- Base directory of the sample sheet and associated IDAT files.

    Raises:
        ValueError: The sample sheet is not formatted properly or a sample cannot be found.
    """

    #__data_frame = None

    def __init__(self, path = None, recursive = False):
        self.__samples = []


        if path:
            self.find_idat_files(path, recursive)

    def add_sample(self, idat_grn, idat_red):
        at = ArrayType.from_probe_count(idat_grn.n_snps_read)
        mf = manifest_cache.get(at)
        
        sigset = SigSet(idat_grn, idat_red, mf)
        
        self.__samples.append(sigset)

    def find_idat_files(self, path, recursive = False) -> int:
        LOGGER.debug('Scanning path: '+str(path))
        sample_dir = Path(path)
        
        n = 0

        if not sample_dir.is_dir():
            raise FileNotFoundError(f'{dir_path} is not a valid directory path')

        files_grn = sorted([str(_.resolve()) for _ in sample_dir.rglob('*_Grn.idat')] + [str(_.resolve()) for _ in sample_dir.rglob('*_Grn.idat.gz')])
        files_red = sorted([str(_.resolve()) for _ in sample_dir.rglob('*_Red.idat')] + [str(_.resolve()) for _ in sample_dir.rglob('*_Red.idat.gz')])
        
        if len(files_grn) != len(files_red):
            logger.warning("Number of grn and red files found not equal")

        for grn in tqdm(files_grn):
            red = grn
            red = re.sub(r"_Grn.idat.gz$", "_Red.idat.gz", red)
            red = re.sub(r"_Grn.idat$", "_Red.idat", red)

            if red not in files_red:
                raise Exception("Missing file: " + red)
            
            test_grn = IdatDataset(grn, Channel.GREEN, header_only = True) # shallow reading for file validation, force reading when needed
            test_red = IdatDataset(red, Channel.RED,   header_only = True) # shallow reading for file validation, force reading when needed
            
            self.add_sample(test_grn, test_red)
            n += 1
        
        LOGGER.debug(' Done scanning path: '+str(path))
        
        return n



    @beartype
    def get_samples(self) -> list:
        """Retrieves Sample objects from the processed sample sheet rows,
        building them if necessary."""
        if not self.__samples:
            raise Exception("invoked in wrong order, build_samples should have been ran earlier")
        
        LOGGER.debug("returning %i samples in a list", len(self.__samples))
        
        return self.__samples
    
    
    def __iter__(self):
        if not self.__samples:
            raise Exception("invoked in wrong order, build_samples should have been ran earlier")

        for sample in self.__samples:
            yield sample


    def get_sample(self, sample_name):
        """ scans all samples for one matching sample_name, if provided.
        If no sample_name, then it returns all samples."""
        # this isn't automatically done, but needed here to work.
        null = self.get_samples()

        candidates = [
            sample
            for sample in self.__samples
            if sample.name == sample_name
        ]
        # or    sample.GSM_ID == sample_name or
        # sample.Sample_Name == sample_name

        num_candidates = len(candidates)
        if num_candidates != 1:
            raise ValueError(f'Expected sample with name `{sample_name}`. Found {num_candidates}')

        return candidates[0]


