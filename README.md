# megcore-getdata

[![get-megdata-tests](https://github.com/nih-megcore/megcore-getdata/actions/workflows/megcoredata-actions.yml/badge.svg)](https://github.com/nih-megcore/megcore-getdata/actions/workflows/megcoredata-actions.yml)

## Data download has been separated into a separate package for use on multiple projects
```
from get_megdata.get_testdata import megdata
```

```
megdata(
    task_type=None,
    output_dir=None,
    version=None,
    get_types=['all'],
    out_format='bids',
)

```
