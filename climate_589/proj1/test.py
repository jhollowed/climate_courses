import glob
import pdb
from jw06_norms_recode import l2_norm as ll
import xarray as xr
import matplotlib.pyplot as plt

#ff = glob.glob('{}/*.nc'.format('/glade/scratch/jhollowed/CAM/cases_589/project1/balance_SE_ne30L30_jw06/run'))[0]
ff = glob.glob('{}/*regrid*.nc'.format('/glade/scratch/jhollowed/CAM/cases_589/project1/BKP*/run'))[0]

d1 = ll(ff, 14)
d2 = ll(ff, 15)
time = xr.open_dataset(ff)['time']
days = [t.day for t in time.values]

ff = plt.figure()
ax1 = ff.add_subplot(121)
ax2 = ff.add_subplot(122)
ax1.plot(days, d1)
ax1.set_title('sym')
ax2.plot(days, d2)
ax2.set_title('err')
plt.show()


