
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import numpy as np
import glob
import pdb
import sys
params = {'text.usetex': False, 'mathtext.fontset': 'stixsans'}
plt.rcParams.update(params)

sys.path.append('/glade/u/home/jhollowed/repos/ncl_exports')
#from wrappers import jw06_l2norm as l2norm        #CJ version
from jw06_norms_recode import l2_norm as l2norm    #custom version


# --------------------------------------------------------------

def makeplots(eq=15):
  
    runs = np.array(glob.glob('/glade/scratch/jhollowed/CAM/cases_589/project1/balance*/run/b*.nc'))
    
    if(eq==15):
        m = np.ones(len(runs), dtype=bool)
        #m = ['FV3' not in r for r in runs]
        #m = ['FV3' in r for r in runs]
    if(eq==14):
        m = np.ones(len(runs), dtype=bool)
        #m = np.array(['SE' in r for r in runs])
    runs = runs[m]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = plt.cm.gnuplot2(np.linspace(0.2, 0.8, len(runs)))

    for i in range(len(runs)):

        model_name = runs[i].split('balance_')[-1].split('_jw06')[0]
        print('\n\n----------- working on {}-----------'.format(model_name))
        
        run = xr.open_dataset(runs[i])
        time = run['time']
        time = np.array([t.values.tolist().day for t in time]) - 1
        l2_file = './norms/l2_eq{}_{}.npy'.format(model_name, eq)
        try:
            print('reading l2...')
            l2 = np.load(l2_file)
        except:
            print('computing l2...')
            l2 = l2norm(runs[i], norm_type=eq)
            np.save(l2_file, l2)
       
        ax.plot(time, l2, color=colors[i], label=model_name)
        
    if(eq==14): ylabel = r'$l_2(u-\bar{u})$  (JW06 Eq.14)'
    if(eq==15): ylabel = r'$l_2(\bar{u}-\bar{u}(t=0))$  (JW06 Eq.15)'
    ax.legend(fontsize=11, loc='upper left')
    ax.set_xlabel(r'Days', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    if(eq == 15):
        ax.set_ylim([0, 3.5])
        ax.set_xlim([0, 20])
        pass
    if(eq==14):
        #ax.set_ylim([0, 1e-4])
        ax.set_yscale('log')
        ax.set_xlim([0, 20])
        
    plt.tight_layout()
    if(eq == 14):
        plt.savefig('figs/steady_state_l2_py_eq{}.png'.format(eq, model_name.split('_')[0]))
    if(eq == 15):
        plt.savefig('figs/steady_state_l2_py_eq{}.png'.format(eq))
    
#for eq in [14, 15]:
    #makeplots(eq)






def makeanim():
  
    runs = np.array(glob.glob('/glade/scratch/jhollowed/CAM/cases_589/project1/balance*/run/b*.nc'))
            
    for t in range(11):
        print('\n\n======= DAY {} ==============='.format(t))
        
        fig = plt.figure(figsize=(10,6))

        for i in range(len(runs)):
            
            ax = fig.add_subplot(2, 2, i+1)

            model_name = runs[i].split('balance_')[-1].split('_jw06')[0]
            print('----------- working on {}-----------'.format(model_name))
            
            # take zonal mean
            run = xr.open_dataset(runs[i])
            run = run.mean('lon')
            udat = run['U']

            u = udat[t]
            #u = udat[t] - udat[0]
            
            time = run['time']
            day = (np.array([t.values.tolist().day for t in time]) - 1)[t]
            
            lat = run['lat'].values
            lev = run['lev'].values
            
            cmap = mpl.cm.jet.copy()
            cmap.set_bad(cmap(0),1.)
            cmap.set_under(cmap(0),1.)
            levels = np.linspace(0, np.log10(40), 15)
            #levels = 17

            var = np.log10(u)
            var[np.where(var == -float("inf"))] = -9999
            im = ax.contourf(lat, lev, var, levels=levels, cmap=cmap, extend='both')
            im.cmap.set_under(cmap(0))
            im.cmap.set_over(cmap(1))
            im.cmap.set_bad(cmap(0))
            cbar = fig.colorbar(im, ax=ax, extend='both')
            cbar.set_label('log10(u)', fontsize=11)

            ax.set_title('{}'.format(model_name.split('_')[0]))
            if(i == 0 or i == 2):
                ax.set_ylabel('lev  [hPa]', fontsize=11)
            else:
                ax.yaxis.set_ticklabels([])
            if(i == 2 or i == 3):
                ax.set_xlabel('lon  [deg]', fontsize=11)
            else:
                ax.xaxis.set_ticklabels([])
            ax.invert_yaxis()
            ax.set_yscale('log')

        fig.suptitle('Day {}'.format(day), fontsize=14)
        plt.tight_layout()
        plt.savefig('figs/anim/anim{}.png'.format(day), dpi=300)

#makeanim()



def makeanimi_horiz(var='U', unit='m/s'):
  
    runs = np.array(glob.glob('/glade/scratch/jhollowed/CAM/cases_589/project1/balance*/run/b*.nc'))
    runs[0], runs[2] = runs[2], runs[0]
            
    for t in range(22):
        print('\n\n======= DAY {} ==============='.format(t))
        
        fig = plt.figure(figsize=(10,6))
        if(t!=21):
            #if(i==2 or i==3): continue
            continue
            sfx=''
        else:
            print('HERE')
            sfx='_all'
            t -= 1

        for i in range(len(runs)):
            
                
            ax = fig.add_subplot(2, 2, i+1)

            model_name = runs[i].split('balance_')[-1].split('_jw06')[0]
            print('----------- working on {}-----------'.format(model_name))
           
            # open data at nearest lev to the center of the jet
            run = xr.open_dataset(runs[i]).sel(lev=252, method='nearest')
            udat = run[var]

            u = udat[t]
            u = udat[t] - udat[0]
            
            time = run['time']
            day = (np.array([t.values.tolist().day for t in time]) - 1)[t]
            
            lat = run['lat'].values
            lon = run['lon'].values
            lev = run['lev'].values
            
            cmap = mpl.cm.jet.copy()
            cmap.set_bad(cmap(0),1.)
            cmap.set_under(cmap(0),1.)
            
            cc = [0, 0]
            if(var == 'U'):
                #if('FV3' in model_name): cc = [-6, 3]
                #elif('FV_' in model_name): cc = [-0.0025, 0.03]
                if('SE' in model_name): cc = [-0.01, 0.015]
                if('EUL' in model_name): cc = [-0.01, 0.025]
            if(var == 'T'): 
                #if('FV3' in model_name): cc = [-2.3, 2.3]
                #elif('FV_' in model_name): cc = [-0.0048, 0.0048]
                if('SE' in model_name): cc = [-0.003, 0.0095]
                if('EUL' in model_name): cc = [-0.005, 0.016]
            
            if(cc[0] - cc[1] == 0):
                levels = 15
            else:
                levels = np.linspace(cc[0], cc[1], 15)
            
            im = ax.contourf(lon, lat, u, levels=levels, cmap=cmap, extend='both')
            im.cmap.set_under(cmap(0))
            im.cmap.set_over(cmap(1))
            im.cmap.set_bad(cmap(0))
            cbar = fig.colorbar(im, ax=ax)
            cbar.ax.tick_params(labelsize=8) 
            cbar.set_label('{0} - {0}(t=0)  [{1}]'.format(var, unit), fontsize=11)

            ax.set_title('{}'.format(model_name.split('_')[0]))
            if(i == 0 or i == 2):
                ax.set_ylabel('lat', fontsize=11)
            else:
                ax.yaxis.set_ticklabels([])
            if(i == 2 or i == 3):
                ax.set_xlabel('lon', fontsize=11)
            else:
                ax.xaxis.set_ticklabels([])

        if(var=='U'): fig.suptitle('{:.2f} hPa, Day {}'.format(lev, day), fontsize=14)
        plt.tight_layout()
        plt.savefig('figs/anim/anim_horiz_{}_{}{}.png'.format(var, day, sfx), dpi=300)

makeanimi_horiz('U', 'm/s')
makeanimi_horiz('T', 'K')
 




