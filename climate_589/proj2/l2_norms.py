import numpy as np
import matplotlib.pyplot as plt
import glob
import pdb
import sys
import xarray as xr

sys.path.append('/glade/u/home/jhollowed/repos/climate_analysis')
from climate_toolbox import l2_norm as l2 


cases='/glade/scratch/jhollowed/CAM/cases_589/project2/new'
sfx = 7.0
res = float(sys.argv[1])

if(res == 1):
    FV_runs = glob.glob('{}/FV_f09*{}/run/*h0*.nc'.format(cases, sfx))
    FV3_runs = glob.glob('{}/FV3_C96*{}/run/*h0*regrid*'.format(cases, sfx))
    SE_runs = glob.glob('{}/SE_ne30*{}/run/*h0*.nc'.format(cases, sfx))
elif(res==0.5):
    FV_runs = glob.glob('{}/FV_f05*{}/run/*h0*.nc'.format(cases, sfx))
    FV3_runs = glob.glob('{}/FV3_C192*{}/run/*h0*regrid*'.format(cases, sfx))
    SE_runs = glob.glob('{}/SE_ne60*{}/run/*h0*.nc'.format(cases, sfx))
print('\n{} FV runs found'.format(len(FV_runs)))
print('{} FV3 runs found'.format(len(FV3_runs)))
print('{} SE runs found'.format(len(SE_runs)))

all_runs = [FV_runs, FV3_runs, SE_runs]
ls = ['-', '--', ':', '-.']
colors=['m','r', 'b']
compvars = ['PS', 'U850', 'PRECL', 'Q850']
units = ['hPa', 'm/s', 'm/s', 'kg/kg']
factor=[1/100, 1, 1, 1]

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(121)
ax2 = ax.twinx()
ax3 = fig.add_subplot(122)
ax4 = ax3.twinx()
axes = [ax, ax2, ax3, ax4]

for i in range(len(all_runs)):
    runs = all_runs[i]
    model = '{}_{}'.format(runs[0].split('/')[-1].split('_')[0], 
                           runs[0].split('/')[-1].split('_')[1].split('L')[0])

    print('========== working on {}'.format(model))

    try:
        dat1 = xr.open_dataset(runs[0])
        dat2 = xr.open_dataset(runs[1])
    except:
        continue
    t = dat1['time']
    time = np.array([tt.hour/24 + tt.day for tt in t.values]) - t.values[0].day
  
    for j in range(len(compvars)):
        var = compvars[j]
        label = '{} [{}]'.format(var, units[j])
        norm_f = './plt_data/{}_norm_{}.npy'.format(model, var)
        try:
            norm = np.load(norm_f)
        except:
            norm = l2(dat1, var, compdat=dat2)
            dat1[var] + dat2[var]
            np.save(norm_f, norm)
        axes[j].plot(time, norm*factor[j], ls[j], color=colors[i])
        axes[j].set_ylabel(label, fontsize=11)
 
    # dummies for legend
    ax.scatter([2], [2], color=colors[i], label=model)
    ax.scatter([2], [2], color='w', s=60)
    
# dummies for legend
ax.plot([0,0], [0,0], ls[0], color='k', label=compvars[0])
ax.plot([0,0], [0,0], ls[1], color='k', label=compvars[1])
ax3.plot([0,0], [0,0], ls[2], color='k', label=compvars[2])
ax3.plot([0,0], [0,0], ls[3], color='k', label=compvars[3])
ax.legend(fontsize=11)
ax3.legend(fontsize=11)


ax.set_xlim([0, 12])
ax3.set_xlim([0, 12])
ax.set_xlabel('time  [days]', fontsize=11)
ax3.set_xlabel('time  [days]', fontsize=11)
ax.tick_params(axis='both', which='major', labelsize=9)
ax2.tick_params(axis='both', which='major', labelsize=9)
ax3.tick_params(axis='both', which='major', labelsize=9)
ax4.tick_params(axis='both', which='major', labelsize=9)

fig.suptitle('Difference in L30, L58 (l2 norm)')

plt.tight_layout()
plt.savefig('figs/NLEV_{}deg_l2.png'.format(res), dpi=300)
plt.show()
