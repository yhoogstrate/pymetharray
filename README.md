# pymethyarray: API fork and rewrite of foxotech/methylprep

`pymetharray` is a fork of the python package, `methylprep` which became unmaintained.
As such, `pymetharray` is a python package for processing Illumina methylation array data.
It primarily serves as API interface for embedded array classifiers rather than direct
analysis, for which different optimizations and data structures were needed. Some
behaviour will break and become backwards incompatible.

Major difference in design philosopy:
 - Input is considered per .idat file, not per array or per dataset
 - As such, API is restructured and not backwards compatible


## Installation

```shell
$ git clone https://github.com/yhoogstrate/pymetharray
$ git checkout -b dev origin/dev
$ cd pymetharray

$ make

$ virtualenv -p python3 .venv
$ source .venv/bin/activate
$ pip install .

```


## Testing code

todo

```
$ source .venv/bin/activate
$ pip install pytest
$ pytest
```

## Tutorials and Guides

Example code on how to create a SampleSheet object:

```
>>> from pymetharray.files import SampleSheet
>>> ss = SampleSheet("cache/", recursive=False)
>>> samples = [_ for _ in ss]
>>> 
```
