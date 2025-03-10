#!/usr/bin/env python

"""
Install & prep test:

virtualenv -p python3 .venv
source .venv/bin/activate

pip install -r requirements.txt
"""


"""
pytest tests
"""


# app
from pathlib import Path
import logging


# lib
from pymetharray.files import SampleSheet
from pymetharray.processing import SampleDataContainer


# logging
logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
#logging.setLevel(logging.DEBUG)



# code
ss = SampleSheet("cache/", recursive=False)


for sample in ss:
    print(" - Sample: "+str(sample.get_sentrix_id()))
    
    sample.load() # should be ran using a getter
    data_container = SampleDataContainer(
            idat_dataset_pair={
                'green_idat': sample.green_idat,
                'red_idat': sample.red_idat
            },
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
            sesame=True,
            pneg_ecdf=False,
            file_format='pickle' # should move into the export function?
        )
    
    data_container.process_all()
    data_container.export("cache/" + sample.get_sentrix_id() + "_data.pkl")


