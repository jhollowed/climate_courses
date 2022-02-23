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
    FV_runs = glob.glob('{}/FV_f09L30*/run/*h0*.nc'.format(cases))
    FV3_runs = glob.glob('{}/FV3_C96L30*/run/*h0*regrid*'.format(cases))
    SE_runs = glob.glob('{}/SE_ne30L30*/run/*h0*.nc'.format(cases))
elif(res==0.5):
    FV_runs = glob.glob('{}/FV_f05L30*/run/*h0*.nc'.format(cases))
    FV3_runs = glob.glob('{}/FV3_C192L30*/run/*h0*regrid*'.format(cases))
    SE_runs = glob.glob('{}/SE_ne60L30*/run/*h0*.nc'.format(cases))
print('\n{} FV runs found'.format(len(FV_runs)))
print('{} FV3 runs found'.format(len(FV3_runs)))
print('{} SE runs found'.format(len(SE_runs)))

all_runs = [FV_runs, FV3_runs, SE_runs]
compvars = ['U', 'OMEGA', 'RELHUM']
units = ['m/s', 'Pa/s', '%']
lims = [[-40, 60], [-236, 295], [0, 100]]

#get time
dd = xr.open_dataset(all_runs[0][0])
t = dd['time']
time = np.array([tt.hour/24 + tt.day for tt in t.values]) - t.values[0].day

for k in range(len(time)):
    k = k*2
    print('\n============ WORKING ON TIME {} ============'.format(k))
    fig1 = plt.figure(figsize=(10,8.5))
    fig2 = plt.figure(figsize=(10,8.5))
    fig3 = plt.figure(figsize=(10,8.5))
    figs = [fig1, fig2 ,fig3]

    
    for i in range(len(all_runs)):
        for j in range(len(all_runs[i])):
            run = all_runs[i][j]
            model = '{}_{}_{}'.format(run.split('/')[-3].split('_')[0], 
                                      run.split('/')[-3].split('_')[1],
                                      run.split('/')[-3].split('_')[-1])
            
            print('\n========== working on {}'.format(model))

            vert_f1 = './plt_data/{}_vert_{}.npy'.format(model, compvars[0])
            vert_f2 = './plt_data/{}_vert_{}.npy'.format(model, compvars[1])
            vert_f3 = './plt_data/{}_vert_{}.npy'.format(model, compvars[2])
            
            data = xr.open_dataset(run)
            lon = data['lon'].values
            lev = data['lev'].values
            
            try: vert_1 = np.load(vert_f1)
            except:    
                dat = data.sel(lat=40, method='nearest')
                vert_1 = dat[compvars[0]]
                np.save(vert_f1, vert_1)
            # get at current time
            vert_1_k = vert_1[k]
            
            try: vert_2 = np.load(vert_f2)
            except:    
                dat = data.sel(lat=40, method='nearest')
                vert_2 = dat[compvars[1]]
                np.save(vert_f2, vert_2)
            # get at current time
            vert_2_k = vert_2[k]
            
            try: vert_3 = np.load(vert_f3)
            except:    
                dat = data.sel(lat=40, method='nearest')
                vert_3 = dat[compvars[2]]
                np.save(vert_f3, vert_3)
            # get at current time
            vert_3_k = vert_3[k]

            verts_k = [vert_1_k, vert_2_k, vert_3_k]
            verts = [vert_1, vert_2, vert_3]

            # get axis position
            model_name = '{}_{}'.format(model.split('_')[0], model.split('_')[1])
            width = model.split('_')[-1]
            if(model_name.split('_')[0] == 'FV'): col = 1
            if(model_name.split('_')[0] == 'FV3'): col = 2
            if(model_name.split('_')[0] == 'SE'): col = 3
            if(width == '3.0'): row=1
            if(width == '7.0'): row=2
            if(width == '15.0'): row=3
            ncol = 3
            nrow = 4
            idx = col + (row-1)*3
    
            cmap = plt.cm.jet
            LON, LEV = np.meshgrid(lon, lev)
            
            axes = [fig.add_subplot(3, 3, idx) for fig in figs]

            for y in range(len(axes)):
                ax = axes[y]
                fig = figs[y]
                vert = verts[y]
                vert_k = verts_k[y]
                lim = lims[y]

                levels = np.linspace(lim[0], lim[1], 12)
                cc = ax.contourf(LON, LEV, vert_k, levels=levels, cmap=cmap, extend='both')
                ax.tick_params(axis='both', which='major', labelsize=8)
                ax.set_ylim([10, np.max(lev)])
                ax.invert_yaxis()
                ax.set_yscale('log')
                
                if(row == 3): 
                    ax.set_xlabel('lon', fontsize=9)
                else:
                    ax.get_xaxis().set_ticklabels([])
 
                if(col == 1): 
                    ax.set_ylabel('lev  [hPa]', fontsize=9)
                else:
                    ax.get_yaxis().set_ticklabels([])
                
                if(col == 3): 
                    cb = fig.colorbar(cc, ax=ax, extend='both')
                    cb.ax.tick_params(labelsize=7)
                
                if(row == 1):
                    ax.set_title('{}\n{} deg'.format(model_name, width), fontsize=9)
                else:
                    ax.set_title('{} deg'.format(width), fontsize=9)
                fig.suptitle('{} at 40N [{}]'.format(compvars[y], units[y]), fontsize=12)

            
    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()
    if(res == 0.5): res = "05"
    if(res == 1): res = "1"
    fig1.savefig('vert_anim/{}deg_{}_t{:02d}.png'.format(res, compvars[0], k), dpi=200)
    #fig2.savefig('vert_anim/deg{}/{}_t{:02d}.png'.format(res, compvars[1], k), dpi=200)
    fig3.savefig('vert_anim/{}deg_{}_t{:02d}.png'.format(res, compvars[2], k), dpi=200)
