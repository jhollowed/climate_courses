import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

f1 = '/glade/scratch/jhollowed/CAM/cases_589/project1/balance_FV3_C96L30_jw06/run/nativegrid_balance_FV3_C96L30_jw06.cam.h0.0001-01-01-00000.nc'
f2 = '/glade/scratch/jhollowed/CAM/cases_589/project1/balance_FV3_C96L30_jw06/run/balance_FV3_C96L30_jw06.cam.h0.0001-01-01-00000.regrid.1x1.nc'

ff1 = xr.open_dataset(f1)
ff2 = xr.open_dataset(f2)

print('meshing 1')
lat1, lon1 = ff1['lat'].values, ff1['lon'].values

print('meshing 2')
lat2, lon2 = np.meshgrid(ff2['lat'].values, ff2['lon'].values)
lat2 = np.ravel(lat2)
lon2 = np.ravel(lon2)
    
print('u1, u2')
u1 = (ff1['U'].values)[0][0]
u2 = (ff2['U'].values)[0][0]

fig = plt.figure(figsize=(10,7))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

#import pdb
#pdb.set_trace()

ax1.scatter(lon1, lat1, c=u1)
#ax2.scatter(lon2, lat2, c=u2)
ax2.imshow(u2)

plt.tight_layout()
plt.savefig('FV3_test.png', dpi=300)
