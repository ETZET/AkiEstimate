# convert Yuri's reference model file to the format that is readable for AkiEstimate
import pandas as pd
import numpy as np
import math
import os
from tqdm import tqdm
import argparse

# Parse Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--litho_ref",type=str, default="/scratch/tolugboj_lab/Prj6_AfrTomography/6_ShareWithGroup/shareWithSiyu")
parser.add_argument("--connection_file",type=str, default="/scratch/tolugboj_lab/Prj6_AfrTomography/6_ShareWithGroup/shareWithSiyu")
parser.add_argument("--output","-o",type=str, default="/scratch/tolugboj_lab/Prj5_HarnomicRFTraces/AkiEstimate/tutorial/Result/GE/reference")
args = parser.parse_args()
litho_ref = args.litho_ref
connection_file = args.connection_file
output_path = args.output

# read in data
refeR = pd.read_csv(os.path.join(litho_ref,"AFRRayleighPhase_LITHO1p0.csv"))
colNm = np.array(refeR.columns)
for n in range(len(colNm)-2):
    colNm[n+2] = colNm[n+2].replace("_Hz","")
refeR.columns = colNm

refeL = pd.read_csv(os.path.join(litho_ref,"AFRLovePhase_LITHO1p0.csv"))
refeL.columns = colNm

errR = pd.read_csv(os.path.join(litho_ref,"AFRRayleighPhase_LITHO1p0_Err.csv"))
errR.columns = colNm

errL = pd.read_csv(os.path.join(litho_ref,"AFRLovePhase_LITHO1p0_Err.csv"))
errL.columns = colNm

# TO-CHANGE
ppConn = pd.read_csv(connection_file)

for index, row in tqdm(ppConn.iterrows(),total=ppConn.shape[0]):
    net1 = row["net1"]
    sta1 = row["sta1"]
    lat1 = row["lat1"]
    lon1 = row["lon1"]
    net2 = row["net2"]
    sta2 = row["sta2"]
    lat2 = row["lat2"]
    lon2 = row["lon2"]
    
    latmid = (lat1 + lat2)/2
    lonmid = (lon1 + lon2)/2
    
    dist = 10
    lat = None
    lon = None
    ind = 0

    for index, row in refeR.iterrows():
        ilat = row["Latitude"]
        ilon = row["Longitude"]
        idist = math.sqrt((latmid-ilat)**2 + (lonmid-ilon)**2)
    
        if idist < dist:
            dist = idist
            lat = ilat
            lon = ilon
            ind = index

    srefR = refeR.iloc[ind]
    srefR.drop(labels = ['Latitude','Longitude'], inplace = True)
    serrR = errR.iloc[ind]
    serrR.drop(labels = ['Latitude','Longitude'], inplace = True)

    referenceR = pd.concat([srefR*1000, serrR*1000], axis=1)

    srefL = refeL.iloc[ind]
    srefL.drop(labels = ['Latitude','Longitude'], inplace = True)
    serrL = errL.iloc[ind]
    serrL.drop(labels = ['Latitude','Longitude'], inplace = True)

    referenceL = pd.concat([srefL*1000, serrL*1000], axis=1)
	
	# TO-CHANGE
    # save the file
    output_R = os.path.join(output_path,"AFRRayleighPhase_LITHO1p0.csv","Rayleigh")
    output_L = os.path.join(output_path,"AFRRayleighPhase_LITHO1p0.csv","Love")
    
    if not os.path.exists(output_R): os.makedirs(output_R)
    if not os.path.exists(output_L): os.makedirs(output_L)
    file = "{}/dispersion_{}-{}_{}-{}_rayleigh.txt".format(
        output_R,net1,sta1,net2,sta2)
    with open(file, 'w') as f:
        f.write('7200\n')

    referenceR.to_csv(file, header = False, sep = ' ', mode = 'a')

    file = "{}/dispersion_{}-{}_{}-{}_love.txt".format(
        output_L,net1,sta1,net2,sta2)
    with open(file, 'w') as f:
        f.write('7200\n')

    referenceL.to_csv(file, header = False, sep = ' ', mode = 'a')
