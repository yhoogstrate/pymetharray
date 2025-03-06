#!/usr/bin/env python

"""
Install & prep test:

virtualenv -p python3 .venv
source .venv/bin/activate


pip install uninstall pymetharray
pip install .
pip list | grep pymetharray

"""


"""
pytest tests
"""




from pathlib import Path


#import os
#if os.path.exists("/home/youri/.cache/pymetharray/HumanMethylationEPIC_manifest_v2.csv.gz"):
#    os.remove("/home/youri/.cache/pymetharray/HumanMethylationEPIC_manifest_v2.csv.gz")


import logging
logging.basicConfig(level=logging.DEBUG)


# legacy code, to be converted to virtual mem objects
#from pymetharray.files import create_sample_sheet
#ss = create_sample_sheet('cache/', output_file='cache/samplesheet.csv', output_path = ".")


from pymetharray.files import SampleSheet
from pymetharray.processing import SampleDataContainer
ss = SampleSheet("cache/", recursive=False)

for sample in ss:
    print(" - Sample: "+str(sample))
    #print("   :: " + sample.green_idat)
    #print("   :: " + sample.red_idat)
    
    data_container = SampleDataContainer(
            idat_dataset_pair={'green_idat': sample.green_idat, 'red_idat': sample.red_idat, 'sample': sample.sample},
            manifest=sample.manifest, # or sample.man
            retain_uncorrected_probe_intensities=True,
            bit='float32',
            switch_probes=True, # this applies all sesame-specific options
            quality_mask= True, # this applies all sesame-specific options (beta / noob offsets too)
            do_noob=True, # None becomes True, but make_pipeline can override with False
            pval=False, #defaults to False as of v1.4.0
            poobah_decimals=3,
            poobah_sig=0.05,
            do_nonlinear_dye_bias=True, # start of run_pipeline sets this to True, False, or None
            #debug=kwargs.get('debug',False),
            sesame=True,
            pneg_ecdf=False,
            file_format='pickle' # should move into the export function?
        )
    
    data_container.process_all()
    data_container.export("cache/out.txt") # apparently caches to a path and not a pkl file



# from pymetharray.processing.pipeline import run_pipeline_ss
# run_pipeline_ss(ss,

    # output_dir = "cache",
    # sample_sheet_filepath="cache/samplesheet.csv",
    # export=True,
    
    # save_uncorrected = False,
    # export_poobah = False,
    # meta_data_frame = False,
    # save_control=False,
    
    # do_save_noob = False
    
    # )

