import sys
import pdb
import numpy as np
import xarray as xr

sys.path.append('/glade/u/home/jhollowed/repos/ncl_exports')
from wrappers import dpres_hybrid_ccm
from wrappers import jw06_l2norm as jw

def l2_norm(f0, norm_type):
    '''
    Computes l2 norms from Jablonowski+Williamson 2006

    Parameters
    ----------
    f0 : string
        path to netcdf file containing the data
    norm_type: int
        Either 14 or 15, giving the equation number from JW06
    '''

    dat = xr.open_dataset(f0)
    u = dat['U']
    ps = dat['PS']
    hyai = dat['hyai']
    hybi = dat['hybi']
    P0 = 100000.0         #Pa, to match ps units
    dp = dpres_hybrid_ccm(ps, P0, hyai, hybi).values
    dp = xr.DataArray(dp, dims=u.dims, coords=u.coords, name='dp')

    
    # approx horizontal weighting
    rad = np.pi/180
    lat = dat['lat']
    wy  = np.cos(lat*rad) #proxy [ sin(j+1/2)-sin(j-1/2) ]

    # get time samples and zonal-mean u
    ntime = len(dat['time'])
    um = u.mean('lon')

    # compute the norm...

    # =============== EQ 14 ===============
    if(norm_type == 14):
        
        norm = np.zeros(ntime)
        for i in range(ntime):
            # the broadcasting here works by matching dimensions by their names, 
            # which importantly comes from the input netcdf file
            diff2 = (u[i] - um[i])**2
            num = np.sum(diff2 * wy * dp[i])
            den = np.sum(wy * dp[i])
            norm[i] = np.sqrt(num/den)
        
        
    # =============== EQ 14 ===============
    elif(norm_type == 15):
        
        norm = np.zeros(ntime)
        for i in range(ntime):
            # the broadcasting here works by matching dimensions by their names, 
            # which importantly comes from the input netcdf file
            diff2 = (um[i] - um[0])**2
            num = np.sum(diff2 * wy * dp[i])
            den = np.sum(wy * dp[i])
            norm[i] = np.sqrt(num/den)
    
    return norm

    
    
    

    
