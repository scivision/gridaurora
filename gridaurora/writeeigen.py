from __future__ import division,absolute_import
from six import string_types
import h5py
from os.path import expanduser
from datetime import datetime
from pytz import UTC
#
from histutils.fortrandates import forceutc

epoch = datetime(1970,1,1,tzinfo=UTC)

def writeeigen(fn,Ebins,diffnumflux,ver,prates,lrates,tezs,latlon):
    if not isinstance(fn,string_types):
        return

    if fn.endswith('.h5'):
        fn = expanduser(fn)
        print('writing to '+ fn)

        ut1_unix = [(forceutc(t)-epoch).total_seconds() for t in ver.labels.to_pydatetime()]

        with h5py.File(fn,'w',libver='latest') as f:
            bdt = h5py.special_dtype(vlen=bytes)
            d=f.create_dataset('/sensorloc',data=latlon)
            d.attrs['unit']='degrees';d.attrs['description']='geographic coordinates'
            #input precipitation flux
            d=f.create_dataset('/Ebins',data=Ebins); d.attrs['unit']='eV'

            d=f.create_dataset('/altitude',data=ver.major_axis);    d.attrs['unit']='km'
            d=f.create_dataset('/ut1_unix',data=ut1_unix);          d.attrs['unit']='sec. since Jan 1, 1970 midnight' #float
            d=f.create_dataset('/diffnumflux',data=diffnumflux);    d.attrs['unit']='cm^-2 s^-1 eV^-1'
            #VER
            d=f.create_dataset('/ver/eigenprofile',data=ver.values,compression='gzip')
            d.attrs['unit']='photons cm^-3 sr^-1 s^-1'; d.attrs['size']='Ntime x NEnergy x Nalt x Nwavelength'
            d=f.create_dataset('/ver/wavelength',data=ver.minor_axis); d.attrs['unit']='Angstrom'
            #prod
            d=f.create_dataset('/prod/eigenprofile',data=prates.values,compression='gzip')
            d.attrs['unit']='particle cm^-3 sr^-1 s^-1'; d.attrs['size']='Ntime x NEnergy x Nalt x Nreaction'
            d=f.create_dataset('/prod/reaction',data=prates.minor_axis,dtype=bdt); d.attrs['description']= 'reaction species state'
            #loss
            d=f.create_dataset('/loss/eigenprofiles',data=lrates.values,compression='gzip')
            d.attrs['unit']='particle cm^-3 sr^-1 s^-1'; d.attrs['size']='Ntime x NEnergy x Nalt x Nreaction'
            d=f.create_dataset('/loss/reaction',data=lrates.minor_axis,dtype=bdt); d.attrs['description']= 'reaction species state'
            #energy deposition
            d=f.create_dataset('/energydeposition',data=tezs.values,compression='gzip')
            d.attrs['unit']='ergs cm^-3 s^-1'; d.attrs['size']='Ntime x Nalt x NEnergies'