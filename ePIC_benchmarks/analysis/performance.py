'''
    check tracking eff, resol, etc
    Shujie Li, Sept 2024
'''
## this block of functions are copied from epic_analysis.ipynb 
from matplotlib.backends.backend_pdf import PdfPages

import os
import sys
import pandas as pd

import awkward as ak
# import ROOT
import uproot as ur

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.pylab as plt

print('Uproot version: ' + ur.__version__) ## this script assumed version 4 
ur.default_library="pd" ## does not work???

#Pandas view options
pd.set_option('display.max_rows', 500)
pd.options.display.max_rows = 40
pd.options.display.min_rows = 20
pd.options.display.max_columns = 100

#Matplotlib figure options
plt.rcParams['figure.figsize'] = [8.0, 6.0]
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['xaxis.labellocation'] = 'right'
plt.rcParams['yaxis.labellocation'] = 'top'

XS_FONT = 8
S_FONT = 9
M_FONT = 12
L_FONT = 16


#Matplotlib font options
plt.rc('font', size=S_FONT)          # controls default text sizes
plt.rc('axes', titlesize=M_FONT)     # fontsize of the axes title
plt.rc('axes', labelsize=M_FONT)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=XS_FONT)    # fontsize of the tick labels
plt.rc('ytick', labelsize=M_FONT)    # fontsize of the tick labels
plt.rc('legend', fontsize=S_FONT)    # legend fontsize
plt.rc('figure', titlesize=L_FONT)  # fontsize of the figure title]

#Set numpy to ignore divide by 0 errors that commonly occur in simulation context
np.seterr(divide='ignore', invalid='ignore')

CWD = os.getcwd()

deg2rad = np.pi/180.0

## convert theta to eta
def theta2eta(xx, inverse=0):
    xx = np.array(xx)
    if inverse==1:
        return np.arctan((np.e)**(-xx))*2
    else:
        return -np.log(np.tan(xx/2.))
    
def gaussian(x, amp, cen, wid):

    return (amp / (np.sqrt(2 * np.pi) * wid)) * np.exp(-(x - cen) ** 2 / (2 * wid ** 2))
        
## read a root tree with uproot 
# dir = 'EPIC/RECO/23.11.0/epic_craterlake/DIS/NC/18x275/minQ2=10/'
# file = 'pythia8NCDIS_18x275_minQ2=10_beamEffects_xAngle=-0.025_hiDiv_1.0000.eicrecon.tree.edm4eic.root'
def read_ur(file_path, tree_name, s3_dir=None):
    
    if s3_dir is not None: # read from JLab server
        server = 'root://dtn-eic.jlab.org//work/eic2/'
        file_path = server + s3_dir + file_path

    tree = ur.open(file_path)[tree_name]
    print(f"read_ur: read {file_path}:{tree_name}. {tree.num_entries} events in total")
    return tree

## read a branch from uproot tree with an option to flatten, return pandas dataframe
#  use kflatten=0 if want to get the nested dataframe
#  iev: event index, default=-1: get all events
def get_branch(tree, branch_name="", kflatten=1):

    if branch_name not in tree.keys():
        sys.exit("ERROR(get_branch): can't find branch "+branch_name)

    df = tree[branch_name].array(library="ak")
    df = ak.to_dataframe(df)
    if isinstance(df,pd.Series):
        return df #df.to_frame(name=bname.split("_")[-1])
    
    colls = df.columns
    if len(colls) < 1:
        print('cannot find any leaf under branch {}'.format(branch_name))
        return pd.DataFrame()

    #remove prefix in name
    cols = [str(c) for c in colls if str(c).startswith('{}.'.format(branch_name))]
    #if it's an array member, the only column is "value"
    if not cols:
        return df
    # drop nested entry
    for cname in list(cols):
        if "[" in cname:
            cols.remove(cname) ## can not convert array to python. drop for now
        elif "covariance.covariance" in cname: ## for TrackParameters
            cols.remove(cname) 
    # rename and flat
    df = df[cols]
    df.rename(columns={c: c.replace(branch_name + '.', '') for c in df.columns}, inplace=True)
    if kflatten:
        df = df.reset_index()
    # df.rename(columns={c: c[0].upper() + c[1:] for c in df.columns}, inplace=True)
    return  df


def pre_proc(fname,dir_path):
    tree_name = "events"
    tree    = read_ur(fname, tree_name, dir_path)

    branch_name = "CentralCKFTrackParameters"
    params  = get_branch(tree, branch_name)
    ## to deal with the nested subsubentry created by the covariance column
    ## also keep only the first track if more than one are reconstructed
    params  = params[(params.subentry==0) & (params.subsubentry==0)].reset_index() 
    params["eta"] = theta2eta(params.theta)
    params  = params.drop(['index','subsubentry'],axis=1)

    branch_name = "MCParticles"
    part    = get_branch(tree, branch_name)
    # primary particle
    cond1   = part.generatorStatus==1
    # pi+
    cond2   = part.PDG==211 

    pion    = part[cond1&cond2].reset_index()
    x,y,z   = pion[["momentum.x", "momentum.y", "momentum.z"]].to_numpy().T
    r       = np.sqrt(x**2 + y**2 + z**2)  # Magnitude of the vector (distance to origin)
    pion["theta"]= np.arccos(z / r) 
    pion["phi"]  = np.arctan2(y, x)
    pion["eta"]  = theta2eta(pion.theta)
    pion["mom"]  = r
    # select particles that get reconstructed
    pion_o = pion #save all generaged pions
    cond = pion.entry.isin(params.entry)
    pion = pion.drop('index',axis=1)
    pion = pion[cond].reset_index()
    # now pion and params should be one-to-one
    return pion_o,pion, params #, traj

def plot_z_scores(ax, mean : float, std : float, ampl : float, max_z_mag : int):

    ax.axvline(x=mean)

    for z in range(1, max_z_mag + 1):
        z_offset = z * std
        y = gaussian(z_offset, ampl, mean, std)
        ax.axvline(x=(mean - z_offset), ymax=y, label=f'Z : {-z}')
        ax.axvline(x=(mean + z_offset), ymax=y, label=f'Z : {z}')

from lmfit.models import GaussianModel
def hist_gaus(dataset, ax, bins=100, klog=0, header=None, plot_zcores=False, max_z_score=2):
    ## select data in range if bins is provided as an array
    if not np.isscalar(bins):
        c1 = dataset <= bins[-1]
        c2 = dataset >= bins[0]
        dataset = dataset[c1 & c2]
    ## ----1st fit------
    n, bins, _ = ax.hist(dataset, bins, density=False, facecolor='b', alpha=0.3)
    xx    = bins[0:-1] + (bins[1] - bins[0]) / 2.0
    ymax  = np.max(n)
    std   = np.std(dataset)
    mean  = np.mean(dataset)

    c1 = xx <= (mean + 2 * std)
    c2 = xx >= (mean - 2 * std)
    cond  = c1 & c2

    ii = 0
    while len(n[cond]) < len(bins) / 2.0:
        # ax.cla()
        ax.clear()
        diff = (bins[-1] - bins[0]) / 2.0 / 2.0
        n, bins, _ = ax.hist(
            dataset,
            np.linspace(
                bins[0] + diff,
                bins[-1] - diff,
                len(bins)
            ),
            density=False,
            facecolor='b',
            alpha=0.3
        )
        xx = bins[0:-1] + (bins[1]-bins[0]) / 2.0
        c1 = xx <= (mean + 2 * std)
        c2 = xx >= (mean - 2 * std)
        cond = c1 & c2
        ii += 1
        if ii > 10:
            print("ERROR(hist_gaus): can not adjust the range.")
            return -1, -1, -1

    model = GaussianModel()
    # create parameters with initial guesses:
    params = model.make_params(center=np.median(xx[cond]), amplitude=np.max(n), sigma=np.std(xx[cond]))  
    result = model.fit(n, params, x=xx)
    
    # -----2nd fit--------
    std = result.params['sigma']
    # std = result.params['sigma'].get_value
    # print(mean,std)
    c1 = xx <= (mean + 2 * std)
    c2 = xx >= (mean - 2 * std)
    cond = c1 & c2
    if len(xx[cond]) < 10:
        print("Fit failed")
        return -1, -1, -1        
    model = GaussianModel()
    params = model.make_params(center=np.median(xx[cond]), amplitude=np.max(n[cond]), sigma=np.std(xx[cond]))  
    try: 
        result = model.fit(n[cond], params, x=xx[cond])
    except TypeError:
        print("Fit failed")
        return -1, -1,-1
    if result.params['sigma'].stderr ==  None:
        print("Fit failed")
        return -1, -1, -1
    #     print(result.fit_report())
        
    #     print (result.best_values)
    # plt.plot(xx, result.best_fit, 'r-', label='best fit')
    rv_mean = float(result.params['center'])
    rv_std = float(result.params['sigma'])
    rv_std_err = float(result.params['sigma'].stderr)
    rv_ampl = float(result.params['amplitude'])

    if len(result.best_fit) > 0:
        ax.plot(xx[cond], result.best_fit, 'r-', label='sigma=%g, err=%g' %(result.params['sigma'], result.params['sigma'].stderr))

    if plot_zcores:
        plot_z_scores(ax, rv_mean, rv_std_err, rv_ampl, max_z_mag=max_z_score)

    ax.legend(title=header, frameon=False, loc='upper left')

    ymax  = np.max(n)
    if klog:
        ax.set_yscale('log')
        ax.set_ylim(1, ymax * 10)
    else:
        ax.set_ylim(0, ymax * 1.3)
    return float(result.params['center']), float(result.params['sigma']), float(result.params['sigma'].stderr)


def plot_eff(pion_o, pion,eta_bins=np.linspace(-4, 4, 21)):
    fig, ax = plt.subplots(1,1,figsize=[6,6])
    plt.title("")
    ## eff
    # original eta of all particle
    sim_eta, _ = np.histogram(pion_o['eta'].values, bins=eta_bins)
    # original eta of particles get reconstruted
    rec_eta, _ = np.histogram(pion['eta'], bins=eta_bins)
    track_eff_total = np.sum(rec_eta) / np.sum(sim_eta)

    eta_centers = (eta_bins[1:] + eta_bins[:-1]) / 2.
    eta_binsize = np.mean(np.diff(eta_centers))
    track_eff = np.nan_to_num(np.array(rec_eta) / np.array(sim_eta))
    
    # binary distribution, pq*sqrt(N)
    # TODO check the errors
    # eff = np.mean(track_eff)
    track_err = np.nan_to_num(track_eff * (1. - track_eff) * np.reciprocal(np.sqrt(sim_eta)))
    # rec_err = eff*(1. - eff)*np.sqrt(rec_eta)
    # track_eff_lower = track_eff - np.maximum(np.zeros(shape=rec_eta.shape), (rec_eta - rec_err)/sim_eta)
    # track_eff_upper = np.minimum(np.ones(shape=rec_eta.shape), (rec_eta + rec_err)/sim_eta) - track_eff
    track_eff_lower = track_eff - np.maximum(np.zeros(shape=rec_eta.shape), track_eff - track_err)
    track_eff_upper = np.minimum(np.ones(shape=rec_eta.shape), track_eff + track_err) - track_eff
    
    ax.errorbar(eta_centers, track_eff, xerr=eta_binsize/2., yerr=[track_eff_lower, track_eff_upper],
                fmt='o', capsize=3)
    ax.set_ylim(0.0, 1.1)
    ax.set_xlim(-4.5, 4.5)
    ax.set_ylabel('Tracking Efficiency')#, fontsize=20)
    ax.set_xlabel('$\eta$')#, fontsize=20)
    ax.text(-4, 1.04, "recon/generated events= %d / %d =%.3f" %(len(pion), len(pion_o), len(pion) / len(pion_o)))
    ax.axhline(1, ls='--', color='grey')
    return track_eff,track_err, eta_centers, fig



def plot_resol(pion, params, plot_resol_zscores=False):
    fig, axs = plt.subplots(2, 2, figsize=(10,6), dpi=300)
    plt.title("")

    ## calculate resolutions
    dp_lim=10 * 4 #%
    th_lim=0.005 * 2 #rad
    ph_lim=0.03 * 2
    dca_lim = 3
    nbins  = 200

    # ----------------momentum resolution----------------------
    i  = 0
    ax = axs.flat[i]
    obs    = 'theta'
    rec_th   = 1./np.array(params['qOverP'])
    sim_th = np.array(pion['mom'])
    dth_th = 100 * (rec_th - sim_th) / sim_th # in %
    mean_mom, sig_mom, err_mom = hist_gaus(
        dth_th,
        ax,
        np.linspace(-dp_lim, dp_lim, nbins+1),
        klog=0, 
        header=None,
        plot_zcores=plot_resol_zscores
    )
    ax.set_xlabel(r'$\delta p/p$ [%]')#, fontsize=20)

    # ----------------theta resolution----------------------
    i+=1
    ax = axs.flat[i]
    obs = 'theta'
    rec_th   = np.array(params[obs])
    sim_th = np.array(pion[obs])
    dth_th = (rec_th - sim_th)
    mean_th, sig_th, err_th = hist_gaus(
        dth_th,
        ax,
        np.linspace(-th_lim, th_lim, nbins+1),
        klog=0, 
        header=None,
        plot_zcores=plot_resol_zscores
    )
    ax.set_xlabel(r'$d\theta$ [rad]')#, fontsize=20)

    # ----------------phi resolution----------------------
    i+=1
    ax = axs.flat[i]
    obs = 'phi'
    rec_th   = np.array(params[obs])
    sim_th = np.array(pion[obs])
    dth_th = (rec_th - sim_th)
    mean_ph, sig_ph, err_ph = hist_gaus(
        dth_th,
        ax,
        np.linspace(-ph_lim, ph_lim, nbins+1),
        klog=0, 
        header=None,
        plot_zcores=plot_resol_zscores
    )
    ax.set_xlabel(r'$d\phi$ [rad]')#, fontsize=20)

    # ----------------theta resolution----------------------
    i+=1
    ax = axs.flat[i]
    obs = 'loc.a'
    rec_th = np.array(params[obs])
    sim_th = 0 #np.array(pion[obs])
    dth_th = (rec_th - sim_th)
    mean_dca, sig_dca, err_dca = hist_gaus(
        dth_th,
        ax,
        np.linspace(-dca_lim, dca_lim, nbins+1),
        klog=0, 
        header=None,
        plot_zcores=plot_resol_zscores
    )
    ax.set_xlabel(r'DCA$_r$ [mm]')#, fontsize=20)
    return sig_mom, err_mom, sig_th, err_th, sig_ph, err_ph, sig_dca, err_dca, fig


## set eff_eta_bins to [] to disable eff plots. similar for resol
def performance_plot(
        file_path,
        dir_path=None, plot_resol_zscores=False,
        eff_eta_bins=np.arange(-4, 4.1, 0.5),
        resol_eta_bins=np.arange(-4, 4.1, 0.5), kchain=0,
        output_name=None, output_dir=CWD):
   
    ## If output name is not given, use the filename 
    if output_name is None:

        #Removes parent directories from path
        file_name = os.path.basename(file_path) 

        #Removes the file extension
        output_name = os.path.splitext(file_name)[0] 

    ## read events tree
    pion_o, pion, params = pre_proc(file_path, dir_path)
    
    ## chain files (for now use s3 format)
    ii = 1
    if len(resol_eta_bins) > 1:
        while ii < kchain:
            ii += 1
            file_path = file_path.replace(f"{ii-1:04d}", f"{ii:04d}")
            print("chain ", file_path)
            p1, p2, p3 = pre_proc(file_path, dir_path)
            pion_o = pd.concat([pion_o, p1], ignore_index=True)
            pion   = pd.concat([pion  , p2], ignore_index=True)
            params = pd.concat([params, p3], ignore_index=True)

    ## eff plot
    if len(eff_eta_bins)>0:

        track_eff, track_err, eta_centers, fig = plot_eff(pion_o, pion, eff_eta_bins)

        fig.axes[0].set_title(file_path)

        plot_filename = f'eff_{output_name}.png'
        plot_file_path = os.path.join(output_dir, plot_filename)

        fig.savefig(plot_file_path)
        plt.close()

        formatted_string = (
            f"{output_name};"
            f"{track_eff.tolist()};"
            f"{track_err.tolist()};"
            f"{eta_centers.tolist()}"
        )

        eff_out_file_name = f"eff_out.txt"
        eff_out_file_path = os.path.join(output_dir, eff_out_file_name)

        with open(eff_out_file_path, 'a') as eff_file:
            eff_file.write(formatted_string + '\n')

    ## resolutions    
    if len(resol_eta_bins) > 0:

        if len(resol_eta_bins) == 1:

            sig_mom, err_mom, sig_th, err_th, sig_ph, err_ph, sig_dca, err_dca, fig = plot_resol(
                pion, params, plot_resol_zscores=plot_resol_zscores
            )

            fig.axes[0].set_title(f"{output_name}")

            image_file_name = f'resol_{output_name}.png'
            image_file_path = os.path.join(output_dir, image_file_name)

            fig.savefig(image_file_path)
            plt.close()

            temp = [sig_mom, err_mom, sig_th, err_th, sig_ph, err_ph, sig_dca, err_dca]
            temp = ' '.join(map(str, temp))
            formatted_string = f"{output_name} {temp}"

            text_file_path = os.path.join(output_dir, 'resol_out_whole.txt')
            with open(text_file_path, 'a') as resol_file:
                resol_file.write(formatted_string + '\n')

        ## need to make slices of eta/theta for simulation campaign data
        else:
            for dd in np.arange(len(resol_eta_bins) - 1): 

                deg_lo = resol_eta_bins[dd]
                deg_hi = resol_eta_bins[dd+1]

                cond1  = (pion.eta) > deg_lo
                cond2  = (pion.eta) <= deg_hi
                cond   = cond1 & cond2

                pion_slice   = pion[cond].reset_index()
                params_slice = params[cond].reset_index()

                ## only proceed with good stats
                if len(pion_slice) > 100:

                    sig_mom, err_mom, sig_th, err_th, sig_ph, err_ph, sig_dca, err_dca, fig = plot_resol(pion_slice, params_slice)

                    fig.axes[0].set_title(f"{deg_lo} < eta < {deg_hi} in {output_name}")

                    filename = f'resol_{output_name}_eta_{deg_lo}_{deg_hi}.png'
                    output_path = os.path.join(output_dir, filename)

                    fig.savefig(output_path)
                    plt.close()

                    temp = [sig_mom, err_mom, sig_th, err_th, sig_ph, err_ph, sig_dca, err_dca]
                    temp = ' '.join(map(str, temp))
                    formatted_string = f"{output_name} {deg_lo} {deg_hi} {temp}"

                    resolution_out_path = os.path.join(output_dir, 'resol_out_slices.txt')
                    with open(resolution_out_path, 'a') as resol_file:
                        resol_file.write(formatted_string + '\n')
