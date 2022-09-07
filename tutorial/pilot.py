######################################
#
# Pilot Program to Conduct AkiEsimate 
#
# Author: Enting Zhou
# Created: 2022-08-15
#
#
######################################

import os
import time
import argparse

# SLURM INFO
def write_slurm_file_header():
    slurm_file = open("temp.slurm",'w')
    slurm_file.write("#!/bin/bash\n")
    slurm_file.write("#SBATCH -J Aki01\n")
    slurm_file.write("#SBATCH -N 1\n")
    slurm_file.write("#SBATCH --reservation=ezhou12_20220808\n")
    slurm_file.write("#SBATCH -p reserved\n")
    slurm_output_path = "/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/Result/GE_TEST/slurm"
    if not os.path.exists(slurm_output_path): os.makedirs(slurm_output_path)
    slurm_file.write("#SBATCH --output={}/%j.out\n".format(slurm_output_path))
    slurm_file.close()

# INVERSION PARAMETER
FILTER = 3
FMIN=0.025
FMAX=0.2
RHO=1e3
VS=1e3
XI=0.5
VPVS=1
SKIP=20

# CODE PATH
source_code_path = "/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate"
# GLOBAL OUTPUT PATH
output_path = "/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/Result/GE_TEST"

# INPUT PATH

# litho reference file path much contain files list below
# Litho reference model file: AFRRayleighPhase_LITHO1p0.csv, AFRLovePhase_LITHO1p0.csv
# Litho reference model err file: AFRRayleighPhase_LITHO1p0_Err.csv, AFRLovePhase_LITHO1p0_Err.csv
litho_ref_files = "/scratch/tolugboj_lab/Prj6_AfrTomography/6_ShareWithGroup/shareWithSiyu"
connection_file = "/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/data_Enting/GE_staconns.csv"
# INPUT path must contain the x correlation result
noise_xcorrelation_input = "/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/Extra_from_noise/CCF_auto/text_output"


if not os.path.exists(output_path): os.makedirs(output_path)

########################################
#          Main Procedure              #
########################################

def step0():
    # STEP 0
    # Generate reference model for inversion process
    ref_out = os.path.join(output_path,"reference")
    os.system("python 00_get_reference.py --litho_ref {} --connection_file {} -o {}".format(litho_ref_files,\
                                                                                        connection_file,\
                                                                                        output_path))
    # Generate station list
    station_list_file = output_path+"/stations.txt"
    os.system("ls {}/Love > {}".format(ref_out,station_list_file))


def step01():
    # INPUT for create initial model
    estimate_code_path = source_code_path+"/InitialPhase/scripts/estimate_joint_phase_amplitude.py"
    step01_output = output_path + "/01_Result"
    if not os.path.exists(step01_output): os.makedirs(step01_output)
    
    # parse station list to get station pairs
    station_list_file = output_path+"/stations.txt"
    #station_list_file = "/Users/ezhou12/Documents/Bluehive/AkiEstimate/stations.txt"
    file = open(station_list_file,'r')
    job_counter = 0
    for line in file.readlines():
        # read the pair
        filename = line.split(".")[0]
        sta1 = filename.split('_')[1]
        sta2 = filename.split('_')[2]
        pair = sta1+"_"+sta2
        
        # define input and output for this pair
        ref_out = os.path.join(output_path,"reference")
        ray_ref = os.path.join(ref_out,"Rayleigh/dispersion_{}_rayleigh.txt".format(pair))
        love_ref = os.path.join(ref_out,"Love/dispersion_{}_love.txt".format(pair))
        pair_output = os.path.join(step01_output,"phase_{}".format(pair))
        # if not os.path.exists(pair_output): os.makedirs(pair_output)
        
        #create slurm file
        write_slurm_file_header()
        with open('temp.slurm','a') as f:
            f.write("module load gcc/9.1.0 python/2.7.12 fftw3/3.3.7/b1 gsl/2.5/b1\n")
            f.write("python2 {} -R {} -r {} -p {} -s {} -f {} -F {} -o {} --filter {} --noshow\n".format(\
                estimate_code_path, ray_ref, love_ref, noise_xcorrelation_input,\
                pair,FMIN,FMAX,pair_output,FILTER))
        
        # submit the slurm job
        os.system("sbatch --export=pair={} temp.slurm".format(pair))
        # sleep to prevent exceeding job limit
        job_counter += 1
        if job_counter >= 100: 
            time.sleep(60)
            job_counter = 0
    
    # clean-up
    file.close()
    os.remove('temp.slurm')
    
def step02():
    # INPUT for fitting physical earth model to initial dispersion curve
    midpoint_litho_ref = output_path+"/litho_ref"
    optimize_code_path = source_code_path+"/InitialPhase/optimizer/optimizejoint"
    
    # Part 1 Generate Litho reference dispersion curve
    print("Generating Litho Reference")
    if not os.path.exists(midpoint_litho_ref): os.makedirs(midpoint_litho_ref)
    os.system('module load matlab; matlab -nodisplay -nodesktop -nosplash -r \"addpath "utils\" ;makemdlfiles_litho "{}" "{}";exit;\"'.format(connection_file,midpoint_litho_ref))
    
    # Part 2 Fitting
    # parse station list to get station pairs
    print("Submitting Initial Fitting Jobs")
    station_list_file = output_path+"/stations.txt"
    file = open(station_list_file,'r')
    job_counter = 0
    for line in file.readlines():
        # read the pair
        filename = line.split(".")[0]
        sta1 = filename.split('_')[1]
        sta2 = filename.split('_')[2]
        pair = sta1+"_"+sta2
        
        # define input output for this pair
        x_corr_ray = noise_xcorrelation_input+"RayleighResponse/dispersion_{}.txt".format(pair)
        x_corr_love = noise_xcorrelation_input+"LoveResponse/dispersion_{}.txt".format(pair)
        init_ray = output_path+"/01_Result/phase_{}.rayleigh".format(pair)
        init_love = output_path+"/01_Result/phase_{}.love".format(pair)
        pair_output = output_path+"/02_Result/Initial_{}/opt".format(pair)
        pair_ref = "{}/{}.txt".format(midpoint_litho_ref,pair)
        os.system("mkdir -p {}".format(pair_output))
        
        # create slurm file
        write_slurm_file_header()
        with open('temp.slurm','a') as f:
            f.write("module load gcc/9.1.0 python/2.7.12 fftw3/3.3.7/b1 gsl/2.5/b1\n")
            f.write("python utils/changeformat.py {} {}\n".format(noise_xcorrelation_input,pair))
            f.write("{} -i {} -I {} -c {} -C {} -o {} -r {} -f {} -F {} -R {} -V {} -X {} -S {} -M {} -N {} -e {} -T {}\n".format(
                optimize_code_path,
                x_corr_love,
                x_corr_ray,
                init_love,
                init_ray,
                pair_output,
                pair_ref,
                FMIN,
                FMAX,
                RHO,
                VS,
                XI,
                VPVS,
                0,60,1.0,
                SKIP   
            ))
        
        # submit the slurm job
        os.system("sbatch --export=pair={} temp.slurm".format(pair))
        # sleep to prevent exceeding job limit
        job_counter += 1
        if job_counter >= 100: 
            time.sleep(120)
            job_counter = 0
    
    # clean-up
    file.close()
    os.remove('temp.slurm')

def step03():
    # INPUT for fitting Bessel function
    step02_ref = output_path+"/02_Result"
    step03_output_path = output_path+"/03_Result"
    optimize_code_path = source_code_path+"/InitialPhase/optimizer/optimizejoint"
    
    # Fitting
    station_list_file = output_path+"/stations.txt"
    file = open(station_list_file,'r')
    job_counter = 0
    for line in file.readlines():
        # read the pair
        filename = line.split(".")[0]
        sta1 = filename.split('_')[1]
        sta2 = filename.split('_')[2]
        pair = sta1+"_"+sta2
        
        # Define input for the pair
        x_corr_ray = noise_xcorrelation_input+"RayleighResponse/dispersion_{}.txt".format(pair)
        x_corr_love = noise_xcorrelation_input+"LoveResponse/dispersion_{}.txt".format(pair)
        pair_ref = step02_ref+"/Initial_{}/opt.model".format(pair)
        pair_out = step03_output_path + "/Final_{}/opt".format(pair)
        
        # create slurm file
        write_slurm_file_header()
        with open('temp.slurm','a') as f:
            f.write("module load gcc/9.1.0 python/2.7.12 fftw3/3.3.7/b1 gsl/2.5/b1\n")
            f.write("{} -i {} -I {} -o {} -r {} -f {} -F {} -R {} -V {} -X {} -S {} -M {} -G {} -N {} -e {} -J -T {}\n".format(
                optimize_code_path,
                x_corr_love,
                x_corr_ray,
                pair_out,
                pair_ref,
                FMIN,
                FMAX,
                RHO,
                VS,
                XI,
                VPVS,
                0, 1.0, 60, 1.0, SKIP 
            ))
        
        # submit the slurm job
        os.system("sbatch --export=pair={} temp.slurm".format(pair))
        # sleep to prevent exceeding job limit
        job_counter += 1
        if job_counter >= 100: 
            time.sleep(120)
            job_counter = 0
        


        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step",type=int)
    args = parser.parse_args()
    step = args.step
    if step == 0:
        step0()
    elif step == 1:
        step01()
    elif step == 2:
        step02()
    elif step == 3:
        step03()


