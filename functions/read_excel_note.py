## Author: Kang
## Last Update: 2025-Feb-03
## Purpose: Read the data in *_ImgRecord.xlsx

import os
import pandas as pd
import tifffile
from glob import glob
from pathlib import Path
from tabulate import tabulate
from rich import print
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def extractExcelData(xlsx_filepath):
    # Read sheet 1 (dataLog) in the xlsx file
    df_1 = pd.read_excel(xlsx_filepath, sheet_name="dataLog",dtype=str)
    df_1.fillna("", inplace=True)
    for col, item in enumerate(df_1.columns.tolist()):
        df_1.rename(columns={item:f"COL_{col:02d}"}, inplace=True)
    df_1 = df_1.iloc[:,0:8]
    
    print("Sheet 1 (dataLog):")
    print(tabulate(df_1, headers='keys', tablefmt='pretty'))
    print("\n\n")
    
    # Read sheet 2 (RECs) in the xlsx file
    rec_filepath = Path(xlsx_filepath).parent.parent
    rec_list = sorted(glob(str(rec_filepath) + '/*.rec'))
    
    timestamps =[]
    comments = []
    EXPO = []
    
    # Get the number of frames in each tif file
    frames = []
    for rec in rec_list:
        print("Processing: ", Path(rec).stem)
        tif_path = rec.replace('.rec', '')
        with tifffile.TiffFile(tif_path) as img:
            frames.append(f"{len(img.pages)}p")
            
    for rec in rec_list:
        with open(rec, mode="r", encoding="utf-16-LE") as f:
            content = f.read().splitlines()
            for line in content:
                if 'Time:' in line:
                    timestamps.append(line.split(' ')[-1])
                if 'Exposure / Delay' in line:
                    EXPO.append(line.split(' ')[-5].split('.')[0]+line.split(' ')[-4])
                    break
        
    
    df_2 = pd.read_excel(xlsx_filepath,sheet_name="RECs",skiprows=[0],dtype=str)
    
    df_2["Index #"] = df_1.iat[0,2].split(' ')[0].replace("-","_") + "-" + df_2["Index #"] + ".tif"
    df_2.rename(columns={"Index #":"Filename"},inplace=True)
    df_2.insert(1, "Timestamp", timestamps)
    df_2.insert(2, "EXPO", EXPO)
    df_2.insert(3, "Frames", frames)
    
    print("Sheet 2 (RECs):")
    print(tabulate(df_2, headers='keys', tablefmt='pretty'))
    print("\n\n")
    
    return df_1, df_2

def exportMarkDown(df_1, rec_filepath):
    # Extract expInfo from the corresponding cells in the sheet 1
    df_expInfo = pd.DataFrame()
    indexName = [
        "Date of Recording",
        "Experimenters",
        "ACUC Protocol",
        "Keywords",
        "Animal ID",
        "Number of Animals",
        "Species",
        "Strain",
        "Sex",
        "Date of Birth",
        "Age(weeks)",
        "Date of Injection",
        "Incubated(weeks)",
        "Injected Brain Area",
        "Coordinates_R(mm)",
        "Coordinates_L(mm)",
        "Virus_R",
        "Virus_L",
        "OS_Cutting(mOsm/Kg)",
        "OS_Holding(mOsm/Kg)",
        "OS_Recording(mOsm/Kg)",
        "LED_Trig_Mode",
        "Onset of Puffing"
    ]
    colName = ['Value_01', 'Value_02', 'Value_03']
    df_expInfo = pd.DataFrame(index=indexName, columns=colName)
    
    # Set Date of Recording
    df_expInfo.iloc[0,0] = df_1.iat[0,2].split(' ')[0]
    # Set Experimenters
    df_expInfo.iloc[1,0] = df_1.iat[1,2]
    # Set ACUC Protocol
    df_expInfo.iloc[2,0] = df_1.iat[5,2]
    # Set Keywords
    df_expInfo.iloc[3] = ["ACh", "Puff",""]
    # Set Animal ID
    df_expInfo.iloc[4,0] = df_1.iat[2,2]
    # Set Number of Animals
    df_expInfo.iloc[5,0] = "1"
    # Set Species
    df_expInfo.iloc[6,0] = df_1.iat[3,6]
    # Set Strain
    df_expInfo.iloc[7,0] = df_1.iat[3,2]
    # Set Sex
    df_expInfo.iloc[8,0] = df_1.iat[2,6]
    # Set Date of Birth
    df_expInfo.iloc[9,0] = df_1.iat[4,2].split(" ")[0]
    # Set Age(weeks)
    df_expInfo.iloc[10,0] = df_1.iat[4,6].split(".")[0]
    # Set Date of Injection
    df_expInfo.iloc[11,0] = df_1.iat[10,2].split(" ")[0]
    # Set Incubated(weeks)
    df_expInfo.iloc[12,0] = df_1.iat[10,6].split(".")[0]
    # Set Injected Brain Area
    df_expInfo.iloc[13,0] = df_1.iat[5,6]
    # Set Coordinates_R(mm)
    df_expInfo.iloc[14] = [df_1.iat[6,2].replace("(mm)","") + df_1.iat[6,3],
                           df_1.iat[6,4].replace("(mm)","").replace("±","") + f"({df_1.iat[6,5]})",
                           df_1.iat[6,6].replace("(mm)","") + df_1.iat[6,7]]
    # Set Virus_R
    df_expInfo.iloc[16] = ["200 nl/site 1:1 mixture", df_1.iat[7,2].split(" ")[0], df_1.iat[7,2].split(" ")[2]]
    
    # Set OS_Cutting(mOsm/Kg)
    df_expInfo.iloc[18,0] = df_1.iat[11,3]
    # Set OS_Holding(mOsm/Kg)
    df_expInfo.iloc[19,0] = df_1.iat[12,3]
    # Set OS_Recording(mOsm/Kg)
    df_expInfo.iloc[20,0] = df_1.iat[13,3]
    
    # Set LED_Trig_Mode
    df_expInfo.iloc[21] = ["TTL_Pulses", '', '']
    df_expInfo.fillna('', inplace=True)
    
    # Set Onset
    df_expInfo.iloc[22,0] = "frame_101(5s)"
    
    print("Output Experiment Information:")
    print(tabulate(df_expInfo, headers='keys', tablefmt='pretty'))
    
    # Export expInfo to a markdown file
    with open(os.path.join(rec_filepath, df_1.iat[0,2].split(' ')[0].replace("-","_") + "_expInfo.md"), "w", encoding="utf-8") as f:
        f.write("---\n")
        for row, item in zip(df_expInfo.index.tolist(), df_expInfo.values.tolist()):
            f.write(f"{row}: "+", ".join([i for i in item if i != ""])+"\n")
        f.write("---\n")