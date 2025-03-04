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


import os
if os.path.exists("/home/youri/.cache/pymetharray/HumanMethylationEPIC_manifest_v2.csv.gz"):
    os.remove("/home/youri/.cache/pymetharray/HumanMethylationEPIC_manifest_v2.csv.gz")


import logging
logging.basicConfig(level=logging.DEBUG)


# legacy code, to be converted to virtual mem objects
from pymetharray.files import create_sample_sheet
ss = create_sample_sheet('cache/', output_file='cache/samplesheet.csv', output_path = ".")


from pymetharray.files import SampleSheet
ss = SampleSheet("cache/", recursive=False)

for sample in ss:
    print(" - Sample: "+str(sample))
    #sample.set_export_filepath(Path("cache/203927450093_R01C01_processed.csv"))



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


"""
# should trigger error - and indeed it does
for sample in ss:
    print(" - Sample: "+str(sample))
    sample.set_export_filepath(Path("cache/203927450093_R01C01_processed.csv"))
"""
