"""
We should use:
ftp://ftp.ngdc.noaa.gov/STP/GEOMAGNETIC_DATA/INDICES/KP_AP/

but for now use:
ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt

Michael Hirsch
"""
from __future__ import division,absolute_import
from pathlib import Path
from datetime import datetime
from dateutil.parser import parse
from six import integer_types,PY2,string_types
from numpy import loadtxt,nan
from pandas import DataFrame
if PY2: FileNotFoundError = IOError

def readmonthlyApF107(yearmon,fn='RecentIndices.txt'):
    fn = Path(fn)
#%% date handle
    if isinstance(yearmon,string_types):
        yearmon = parse(yearmon)
    #not elif
    if isinstance(yearmon,datetime):
        yearmon = int(str(yearmon.year) + '{:02d}'.format(yearmon.month))

    assert isinstance(yearmon,(integer_types))
#%% load data
    if not fn.is_file():
        raise FileNotFoundError(str(fn.resolve()) +' download from ftp://ftp.swpc.noaa.gov/pub/weekly/RecentIndices.txt')

    d = loadtxt(str(fn),comments=('#',':'), usecols=(0,1,7,8,9,10))
#  genfromtxt didn't eliminate missing values, unsure if bug
#    d = genfromtxt(fn,comments='#', usecols=(0,1,7,8,9,10), skip_header=2,dtype=float,
 #                missing_values={-1:-1},filling_values={-1:nan},invalid_raise=False)
#%% process and pack data
    ind=[]
    for ym in d[:,:2]:
        ind.append(int(str(int(ym[0])) + '{:02d}'.format(int(ym[1]))))

    data = DataFrame(index=ind,data=d[:,2:],columns=['f107o','f107s','Apo','Aps'])

    data[data==-1] = nan #by defn of NOAA

    ApF107 = data.loc[yearmon,:]

    return ApF107

if __name__ == '__main__':
    data = readmonthlyApF107('2015-03-01T12:34:56','RecentIndices.txt')