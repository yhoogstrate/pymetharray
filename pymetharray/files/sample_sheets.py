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


LOGGER = logging.getLogger(__name__)

REQUIRED_HEADERS = {'Sample_Name', 'Sentrix_ID', 'Sentrix_Position'}
ALT_REQUIRED_HEADERS = {'Sample_Name', 'SentrixBarcode_A', 'SentrixPosition_A'}



class SampleSheet():
    """Validates and parses an Illumina sample sheet file.

    Arguments:
        filepath_or_buffer {file-like} -- the sample sheet file to parse.
        dir_path {string or path-like} -- Base directory of the sample sheet and associated IDAT files.

    Raises:
        ValueError: The sample sheet is not formatted properly or a sample cannot be found.
    """

    __data_frame = None

    def __init__(self, path = None, recursive = False):
        self.__samples = []
        #self.fields = {}
        #self.renamed_fields = {}

        #self.headers = []
        #self.alt_headers = None

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
        
        return n


    @beartype
    @staticmethod
    def is_sample_sheet(filepath_or_buffer) -> bool:
        """Checks if the provided file-like object is a valid sample sheet.

        Method:
            If any row in the file contains these column names, it passes: `{0}`
            Alternatively, if all of these column names are present instead, it also passes, and processing will expect these: `{1}`

        Arguments:
            filepath_or_buffer {{file-like}} -- the sample sheet file to parse.

        Returns:
            [boolean] -- Whether the file is a valid sample sheet.
        """.format(REQUIRED_HEADERS, ALT_REQUIRED_HEADERS)
        data_frame = pd.read_csv(filepath_or_buffer, header=None, nrows=25)

        reset_file(filepath_or_buffer)

        for _, row in data_frame.iterrows():
            if REQUIRED_HEADERS.issubset(row.values):
                return True
            elif ALT_REQUIRED_HEADERS.issubset(row.values):
                return True

        return False


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


    @beartype
    def build_samples(self) -> int:
        """Builds Sample objects from the processed sample sheet rows.

        Added to Sample as class_method: if the idat file is not in the same folder, (check if exists!) looks recursively for that filename and updates the data_dir for that Sample.
        """

        self.__samples = []

        logging.info('Building samples')

        for _index, row in self.__data_frame.iterrows():
            if self.alt_headers:
                sentrix_id = row['SentrixBarcode_A'].strip()
                sentrix_position = row['SentrixPosition_A'].strip()
            else:
                sentrix_id = row['Sentrix_ID'].strip()
                sentrix_position = row['Sentrix_Position'].strip()

            if not (sentrix_id and sentrix_position):
                continue

            sample = Sample(
                data_dir=self.data_dir,  # this assumes the .idat files are in the same folder with the samplesheet.
                sentrix_id=sentrix_id,
                sentrix_position=sentrix_position,
                channel_grn=row['channel_Grn'].strip(),
                channel_red=row['channel_Red'].strip(),
                **row,
            )
            if sample.renamed_fields != {}:
                self.renamed_fields.update(sample.renamed_fields)
            self.fields.update(sample.fields)
            self.__samples.append(sample)
    
        logging.debug("Has built: " + str(len(self.__samples)) + " samples")
        
        return len(self.__samples)

    def contains_column(self, column_name):
        """ helper function to determine if sample_sheet contains a specific column, such as GSM_ID.
        SampleSheet must already have __data_frame in it."""
        if column_name in self.__data_frame:
            return True
        return False


    @beartype
    def read(self, sample_sheet_file: BufferedReader) -> int:
        """Validates and reads a sample sheet file, building a DataFrame from the parsed rows.

        Method:
            It autodetects whether a sample sheet is formatted in Infinium MethylationEPIC style, or without the headers.
            Rows must contain these columns: {0}
            See https://support.illumina.com/downloads/infinium-methylationepic-sample-sheet.html for more information about file formatting.

            Format 1: First row of file contains header data.
            Format 2: header is not the first row. Header begins on the row after [Data] appears in first column.

        Dev notes:
            It loads whole file using pandas.read_csv to better handle whitespace/matching on headers.""".format(REQUIRED_HEADERS)

        LOGGER.debug('Parsing sample_sheet: '+str(sample_sheet_file))

        if not self.is_sample_sheet(sample_sheet_file):
            columns = ', '.join(REQUIRED_HEADERS)
            alt_columns = ', '.join(ALT_REQUIRED_HEADERS)
            raise ValueError(f'Cannot find header with values: {columns} or {alt_columns}')

        # first, parse headers and reset
        # this puts all the sample_sheet header rows into SampleSheet.headers list.
        rows_to_scan=100
        cur_line = sample_sheet_file.readline()
        while not cur_line.startswith(b'[Data]'):
            if rows_to_scan == 0:
                if self.headers == {}:
                    LOGGING.info("Finished scanning sample_sheet; did not find header info.")
                break
            raw_line = cur_line.decode()
            if raw_line:
                self.headers.append(raw_line)
            cur_line = sample_sheet_file.readline()
            rows_to_scan -= 1
        reset_file(sample_sheet_file)

        test_sheet = pd.read_csv(
            sample_sheet_file,
            header = None,  # this ensures row[0] included as data -- [this is for looking for the header]
            keep_default_na=False,
            skip_blank_lines=True,
            dtype=str,
        )
        test_sheet = test_sheet.to_dict('records')  # list of dicts
        rows_to_scan = 25 # scan first 25 rows of document
        start_row = None
        for idx,row in enumerate(test_sheet):  # header is not the first row. alt format is that header begins on row after [Data]
            if rows_to_scan == 0:
                LOGGER.info(f'DEBUG {cur_line} {line_bits}')
                raise ValueError('Sample sheet is invalid. Could not find start of data row, assuming there should be a [Data] row to start data, and no more than 25 preceding rows.')
            if '[Data]' in row.values():
                # Format 1 parsing: assume the header begins right after [Data]
                start_row = idx + 1
                break
            if REQUIRED_HEADERS.issubset(row.values()):
                # Format 2 parsing: no [Data] and probably first row is header.
                start_row = idx
                self.alt_headers = False
                break
            if ALT_REQUIRED_HEADERS.issubset(row.values()):
                # Format 2 parsing: no [Data] and probably first row is header.
                start_row = idx
                self.alt_headers = True
                break
            rows_to_scan -= 1
        if start_row == None:
            raise ValueError("error - did not parse header right")

        # preceding code uses `start_row` to strip out any non-data rows from sample_sheet_file before loading into dataframe.
        reset_file(sample_sheet_file)
        self.__data_frame = pd.read_csv(
            sample_sheet_file,
            header=start_row,
            keep_default_na=False,
            skip_blank_lines=True,
            dtype=str,
        )
        reset_file(sample_sheet_file)

        # rename ALT columns to standard columns in the sample_sheet dataframe now.
        if self.alt_headers:
            self.rename_alt_headers()
        
        self.build_samples()
        
        return len(self.__data_frame)

    def rename_alt_headers(self):
        columns = {'SentrixBarcode_A':'Sentrix_ID','SentrixPosition_A':'Sentrix_Position'}
        self.__data_frame = self.__data_frame.rename(columns=columns)
        LOGGER.info(f"Renamed SampleSheet columns {columns}")

    def build_meta_data(self, samples = None):
        """Takes a list of samples and returns a data_frame that can be saved as a pickle. """
        if samples:
            pass
        elif not samples and hasattr(self, '__samples'):
            samples = getattr(self, '__samples')
        else:
            raise ValueError("Either provide a list of samples or run SampleSheet.get_samples() first.")
        field_classattr_lookup = {
            'Sentrix_ID': 'sentrix_id',
            'Sentrix_Position': 'sentrix_position',
            'Sample_Group': 'group',
            'Sample_Name': 'name',
            'Sample_Plate': 'plate',
            'Pool_ID': 'pool',
            'Sample_Well': 'well',
            'GSM_ID': 'GSM_ID',
            'Sample_Type': 'type',
            'Sub_Type': 'sub_type',
            'Control': 'is_control',
        }
        # sample_sheet.fields is a complete mapping of original and renamed_fields
        cols = list(self.fields.values()) + ['Sample_ID']
        meta_frame = pd.DataFrame(columns=cols)
        # row contains the renamed fields, and pulls in the original data from sample_sheet
        rows = []
        for sample in samples:
            row = {}
            for field in self.fields.keys():
                if self.fields[field] in field_classattr_lookup:
                    row[ self.fields[field] ] = getattr(sample, field_classattr_lookup[self.fields[field]] )
                elif field in self.renamed_fields:
                    row[ self.fields[field] ] = getattr(sample, self.renamed_fields[field])
                else:
                    LOGGER.info(f"extra column: {field} ignored")
            # add the UID that matches m_value/beta value pickles
            #... unless there's a GSM_ID too
            row['Sample_ID'] = f"{row['Sentrix_ID']}_{row['Sentrix_Position']}"
            rows.append(row)
  
        meta_frame = pd.DataFrame(columns=cols, data=rows)
        
        return meta_frame



@beartype
def create_sample_sheet(dir_path, matrix_file=False, output_file='samplesheet.csv',
    sample_type='', sample_sub_type='', output_path=None, file_basename_filters = None):
    """Creates a samplesheet.csv file from the .IDAT files of a GEO series directory

    Arguments:
        dir_path {string or path-like} -- Base directory of the sample sheet and associated IDAT files.
        matrix_file {boolean} -- Whether or not a Series Matrix File should be searched for names. (default: {False})
        file_basename_filters -- Subselections of files to include in the sample sheet, e.g. ["206467011168_R01C01"] or ["206467010068_R01C01_Grn.idat"]

        ========== | ========= | ==== | =======
        parameter  | required | type | effect
        ========== | =========  ==== | =======
        sample_type | optional | string | label all samples in created sheet as this type (i.e. blood, saliva, tumor cells)
        sample_sub_type |  optional | string | further detail sample type for batch
        controls | optional | list of sample_names | assign all samples in controls list to be "control samples", not treatment samples.
        ========== | ========= | ==== | =======

    Note:
        Because sample_names are only generated from Matrix files, this method won't let you assign controls to samples from CLI.
        Would require all sample names be passed in from CLI as well, a pretty messy endeavor.

    Raises:
        FileNotFoundError: The directory could not be found.
    """

    sample_dir = Path(dir_path)

    if not sample_dir.is_dir():
        raise FileNotFoundError(f'{dir_path} is not a valid directory path')

    idat_files = sample_dir.rglob('*Grn.idat*') #.gz OK

    _dict = {'GSM_ID': [], 'Sample_Name': [], 'Sentrix_ID': [], 'Sentrix_Position': [], 
            'channel_Grn': [], 'channel_Red': [] 
            }

    # additional optional columns
    addl_cols = []
    if sample_type:
        _dict['Sample_Type'] = []
        addl_cols.append('Sample_Type')
    if sample_sub_type:
        _dict['Sample_Sub_Type'] = []
        addl_cols.append('Sample_Sub_Type')

    file_name_error_msg = "This .idat file does not have the right pattern to auto-generate a sample sheet: {0}"
    for idat in idat_files:
        LOGGER.debug("Found: "+str(idat))
        
        try:
            filename = os.path.basename(idat)

            if file_basename_filters is None:
                _match = True
            else:
                _match = False
                for filter in file_basename_filters:
                    if filename.find(filter) != -1:
                        _match = True

            if _match:
                split_filename = filename.split("_")

                if split_filename[0].startswith('GSM'):
                    _dict['GSM_ID'].append(split_filename[0])
                    _dict['Sentrix_ID'].append(split_filename[1])
                    _dict['Sentrix_Position'].append(split_filename[2])
                elif len(split_filename) == 3:
                    _dict['GSM_ID'].append("")
                    _dict['Sentrix_ID'].append(split_filename[0])
                    _dict['Sentrix_Position'].append(split_filename[1])
                else:
                    raise ValueError(file_name_error_msg.format(idat))

                _dict['channel_Grn'].append(os.path.join(str(sample_dir), filename))
                _dict['channel_Red'].append(os.path.join(str(sample_dir), re.sub("_Grn(\\.[^/]+)$","_Red\\1",filename)))

                if sample_type:
                    _dict['Sample_Type'].append(sample_type)
                if sample_sub_type:
                    _dict['Sample_Sub_Type'].append(sample_sub_type)

        except:
            raise ValueError(file_name_error_msg.format(idat))

    print(_dict)

    if matrix_file:
        _dict['Sample_Name'] = sample_names_from_matrix(dir_path, _dict['GSM_ID'])
    else:
        # generate sample names
        for i in range (1, len(_dict['GSM_ID']) + 1):
            _dict['Sample_Name'].append("Sample_" + str(i))

    df = pd.DataFrame(data=_dict)

    if output_path is None:
        exp_path = (PurePath(dir_path, output_file))
    else:
        exp_path = (PurePath(str(output_path), output_file)) # e.g. for storage of idats on read only mount points
    LOGGER.debug("final output file: "+str(exp_path))
    df.to_csv(path_or_buf=exp_path,index=False)

    LOGGER.info(f"[!] Created sample sheet: {exp_path} with {len(_dict['GSM_ID'])} GSM_IDs")
    
    #return (SampleSheet(output_file, output_path if output_path is not None else dir_path))
    return (dir_path)

