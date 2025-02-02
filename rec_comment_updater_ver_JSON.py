## Author: Kang
## Last Update: 2025-Feb-03
## Purpose: update the metadata in the comment of each recording file
## based on the *_REC_summary_updated.json file in the notes folder

import os
import sys
import json
import tifffile
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import pandas as pd
from glob import glob
from PySide6.QtWidgets import QApplication
from rich import print

from classes import GetPath, Confirm
from functions import recovery, scan_contents, contentUpdater

# Set event handler
app = QApplication(sys.argv)

# Get the path of the folder containing the rec files
dlg_recs = GetPath(title='Select a folder of rec files', filemode = 'dir')
rec_filepath = dlg_recs.get_path()
# rec_filepath = "E:/PRO_iAChSnFR_Specificity/Raw/2023_09_26"

# Control terms
recovery_mode = False

# Read and update the metadata in each rec file
if os.path.exists(rec_filepath):
    rec_list = sorted(glob(rec_filepath + '/*.rec'))
    if rec_list != []:
        if recovery_mode:
            recovery(rec_filepath, rec_list)
        else:
            # Get the path of the *_REC_summary_updated.json file
            dlg_json = GetPath(title='Select the *_REC_summary_updated.json file', filemode = 'file', filetype='json', init_dir=os.path.join(rec_filepath,'notes'))
            json_filepath = dlg_json.get_path()
            
            if os.path.exists(json_filepath):
                # Scan the content of each rec file
                list_of_kept_contents, list_of_original_contents = scan_contents(rec_list)
                
                
                # Read REC summary from the json file
                with open(json_filepath, mode="r") as f:
                    rec_summary = pd.DataFrame(json.load(f), dtype=str)
                
                rec_summary.fillna("", inplace=True)
                
                # Update the read REC summary
                # Add prefix to the 'Cell/Pos' column of the rec_summary
                prefix = ['SITE_', "CELL_"]        
                for idx, val in enumerate(rec_summary['Cell/Pos'].tolist()):
                    rec_summary.loc[idx, "Cell/Pos"] = prefix[0]+val
                
                # swap the columns
                columns_to_be_swapped = ['Filename', 'Timestamp', 'OBJ', 'Light', 'Intensity', 'Exposure', 'Signal', 'Frames']
                columns_unchanged = rec_summary.columns.tolist()[len(columns_to_be_swapped):]
                for name in columns_unchanged:
                    columns_to_be_swapped.append(name)
                    
                print("REC Summary from JSON file (adjusted):")
                print(tabulate(rec_summary, headers='keys', showindex=True, tablefmt="pretty"))
                print("\n\n")
                
                rec_summary = rec_summary[columns_to_be_swapped]
                
                # Chanege the column names, add new columns and update the values
                EXP_SETTING =[
                            "PUFF",
                            "PUFF_CONC",
                            "PUFF_PERIOD",
                            "PUFF_COUNT",
                            "PUFF_PRESSURE",
                            "BATHED_IN",
                            "BATHED_CONC",
                            "FLOWED"
                            ]
                
                CAM_TRIG_MODE = ['EXT_EXP_CTRL', 'EXT_EXP_START']
                
                new_rec_summary = rec_summary.rename(columns={
                    'OBJ': 'OBJ',
                    'Light': 'EXC',
                    'Intensity': 'LEVEL',
                    'Exposure': 'EXPO',
                    'Signal': 'EMI',
                    'Frames': 'FRAMES',
                    'Slice_#': 'SLICE',
                    'Cell/Pos': 'AT',
                    'Puff': EXP_SETTING[0],
                    'P.Conc': EXP_SETTING[1],
                    'P.Period': EXP_SETTING[2],
                    'P.Pulses': EXP_SETTING[3],
                    'P.Pressure': EXP_SETTING[4],
                    # 'Bathed_with': EXP_SETTING[5],
                    # 'B.Conc.': EXP_SETTING[6],
                    # 'B.Flowed': EXP_SETTING[7]
                })
                
                # Get the number of frames in each tif file
                frames = []
                for rec in rec_list:
                    print("Processing: ", Path(rec).stem)
                    tif_path = rec.replace('.rec', '')
                    with tifffile.TiffFile(tif_path) as img:
                        frames.append(f"{len(img.pages)}p")
                
                # Update the values of the new columns
                list_of_Signal = rec_summary['Signal'].tolist()
                list_of_EMI = []
                list_of_EXC = []
                for sig in list_of_Signal:
                    if sig in ['GFP']:
                        list_of_EMI.append('GREEN')
                        list_of_EXC.append('LED_BLUE')
                    elif sig in ['mCherry']:
                        list_of_EMI.append('RED')
                        list_of_EXC.append('LED_GREEN')
                    elif sig in ["IRDIC", "IR"]:
                        list_of_EMI.append('IR')
                        list_of_EXC.append('HLG')
                    else:
                        pass
                
                list_of_Exposure = rec_summary['Exposure'].tolist()
                list_of_EXPOs = [item.split('/')[0] for item in list_of_Exposure]
                
                new_rec_summary.loc[:, 'EXC'] = list_of_EXC
                new_rec_summary.loc[:, 'EXPO'] = list_of_EXPOs
                new_rec_summary.loc[:, 'EMI'] = list_of_EMI
                new_rec_summary.loc[:,'FRAMES'] = frames
                
                insert_FPS = new_rec_summary.columns.get_loc('FRAMES') + 1
                new_rec_summary.insert(insert_FPS, 'FPS', ['20Hz']*new_rec_summary.shape[0])
                insert_CAM_TRIG_MODE = new_rec_summary.columns.get_loc('FPS') + 1
                new_rec_summary.insert(insert_CAM_TRIG_MODE, 'CAM_TRIG_MODE', [CAM_TRIG_MODE[1]]*new_rec_summary.shape[0])
                
                list_of_PPeriod = rec_summary['P.Period'].tolist()
                list_of_periods = [item.split('/')[0] if item != "" else "" for item in list_of_PPeriod]
                list_of_gaps = [item.split('/')[1] if item != "" else "" for item in list_of_PPeriod ]
                new_rec_summary[EXP_SETTING[2]] = list_of_periods
                
                list_of_PPulses = rec_summary['P.Pulses'].tolist()
                list_of_counts = [item.lstrip('x') if item != "" else "" for item in list_of_PPulses]
                new_rec_summary[EXP_SETTING[3]] = list_of_counts
                
                insert_PUFF_GAP = new_rec_summary.columns.get_loc(EXP_SETTING[3]) + 1
                new_rec_summary.insert(insert_PUFF_GAP, 'PUFF_GAP', list_of_gaps)
                
                # new_rec_summary[EXP_SETTING[5]] = new_rec_summary[EXP_SETTING[5]].replace('Reco_ACSF', 'ACSF')
                
                print("Updated REC Summary:")
                print(tabulate(new_rec_summary, headers='keys', showindex=True, tablefmt="pretty"))
                
                list_of_new_content = contentUpdater(new_rec_summary, list_of_kept_contents)
                print("Updated Content (last one):")
                print(list_of_new_content[-1])
                
                dlg_checkUpdate = Confirm(title='Update the REC files?', msg='Do you want to update the REC files?')
                if dlg_checkUpdate.exec():
                    # Save backup files
                    if not os.path.exists(os.path.join(rec_filepath, "backups")):
                        os.mkdir(os.path.join(rec_filepath, "backups"))
                        
                    backup_path=os.path.join(rec_filepath, f"backups/recs_backup_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
                    with open(backup_path, mode="w") as f:
                        json.dump(list_of_original_contents, f, indent=4)
                        print("Backup saved!")
                    
                    new_rec_summary.to_csv(os.path.join(rec_filepath, f"{rec_filepath.split('/')[-1]}_summary.csv"), index=False)
                    print("Summary saved!")
                    
                    for rec , new_conent in zip(rec_list, list_of_new_content):
                        with open(rec, mode="w", encoding="utf-16-LE") as f:
                            f.write('\n'.join(new_conent))
                    print("All recording files are updated!")
                else:
                    print("Update Cancelled!")
            else:
                print("Update Cancelled: No JSON file was selected!")
    else:
        print("No rec files found in the selected folder, please try again!")
else:
    print("Update Cancelled: No REC folder was selected!")
    