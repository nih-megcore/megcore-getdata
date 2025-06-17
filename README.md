# megcore-getdata

[![get-megdata-tests](https://github.com/nih-megcore/megcore-getdata/actions/workflows/megcoredata-actions.yml/badge.svg)](https://github.com/nih-megcore/megcore-getdata/actions/workflows/megcoredata-actions.yml)

## Data download has been separated into a separate package for use on multiple projects
```
from get_megdata.get_testdata import megdata
```

```
gd = megdata(task_type='rest')
gd.getdata()  #Downloads data to ~/nihmeg_test_data
```
Namespace variables are dot accessible in the gd.data variable <br>
e.g.) gd.bem provides the path to the bem output <br>
Additional tags: [ 'bem', 'bidsT1w', 'brik_in', 'fwd', 'meg_fname', 'noise_fname', 'orthohull', 'src', 'subjects_dir', 'trans'] <br>



