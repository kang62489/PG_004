## Author: Kang
## Last Update: 2025-Jan-26
## Purpose: update the metadata in the comment of each recording file
## based on the *_REC_summary_updated.json file in the notes folder

from hmac import new
import os
import sys
import json
from numpy import save
import tifffile
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import pandas as pd
from glob import glob
from PySide6.QtWidgets import QApplication
from rich import print



# Set event handler
app = QApplication(sys.argv)

# Get the path of the folder containing the rec files
from classes import dialog_getPath
dlg_recs = dialog_getPath.GetPath(title='Select a folder of rec files', filemode = 'dir')
rec_filepath = dlg_recs.get_path()
# rec_filepath = "E:/PRO_iAChSnFR_Specificity/Raw/2023_09_26"

# Control terms
recoveryMode = False
demo = True
update_content_check, save_backup = True, True


# Read and update the metadata in each rec file
if os.path.exists(rec_filepath):
    rec_list = glob(rec_filepath + '/*.rec')
    if rec_list != []:
        if recoveryMode:
            # Get the path of the *_REC_summary_updated.json file
            dlg_json = dialog_getPath.GetPath(title='Select the *_REC_summary_updated.json file', filemode = 'file', filetype='json', init_dir=os.path.join(rec_filepath,'backups'))
            json_filepath = dlg_json.get_path()
            with open(json_filepath, mode="r") as f:
                backup = json.load(f)
            
            for olddata, rec in zip(backup, rec_list):
                with open(rec, mode="w", encoding="utf-16-LE") as f:
                    f.write('\n'.join(olddata))
            print("Recovery Completed!")
            
        else:
            # Get the path of the *_REC_summary_updated.json file
            dlg_json = dialog_getPath.GetPath(title='Select the *_REC_summary_updated.json file', filemode = 'file', filetype='json', init_dir=os.path.join(rec_filepath,'notes'))
            # json_filepath = "E:/PRO_iAChSnFR_Specificity/Raw/2023_09_26/notes/2023_09_26_REC summary_updated.json"
            json_filepath = dlg_json.get_path()
            if os.path.exists(json_filepath):
                
                backup = []
                frames = []
                rec_summary = pd.read_json(json_filepath, dtype=str)
                
                if demo:
                    frames = ['100p']*rec_summary.shape[0]
                else:
                    for rec in rec_list:
                        print("Processing: ", Path(rec).stem)
                        tif_path = rec.replace('.rec', '')
                        with tifffile.TiffFile(tif_path) as img:
                            frames.append(f"{len(img.pages)}p")
                
                prefix = ['SITE_', "CELL_"]        
                for idx, val in enumerate(rec_summary['Cell/Pos'].tolist()):
                    rec_summary.loc[idx, "Cell/Pos"] = prefix[0]+val
                
                for row_idx, rec in enumerate(rec_list):
                    context_kept = []
                    switch_list = []
                    remain_list = []
                    with open(rec, mode="r", encoding="utf-16-LE") as f:
                        context = f.read().splitlines()
                        rewrite_idx_kept = 0
                        for idx, line in enumerate(context):
                            if 'Comment:' in line:
                                rewrite_idx_kept = idx
                                break
                        
                        rewrite_idx_start = rewrite_idx_kept + 1
                        context_kept = context[:rewrite_idx_start]
                    
                    context_kept.append('')
                    
                    rowNames = rec_summary.columns[2:].tolist()
                    if row_idx == 0:
                        print("Original Column Names: \n", rec_summary.columns.tolist())
                    
                    EXP_SETTING =[
                                "PUFF",
                                "PUFF_CONC",
                                "PUFF_PERIOD",
                                "PUFF_COUNT",
                                "PUFF_PRESSURE",
                                "BATH_IN",
                                "BATH_CONC",
                                "WASH"
                                ]
                    
                    CAM_TRIG_MODE = ['EXT_EXP_CTRL', 'EXT_EXP_START']
                    
                    # Update the metadata in the json file
                    switch_list = ['Filename', 'Timestamp', 'OBJ', 'Light', 'Intensity', 'Exposure']
                    remain_list = rec_summary.columns.tolist()[6:]
                    for name in remain_list:
                        switch_list.append(name)
                    new_rec_summary = rec_summary[switch_list]
                    
                    new_rec_summary['Filename'] = new_rec_summary['Filename'].replace('-', '_')
                    new_rec_summary['Light'] = new_rec_summary['Light'].replace('LED', 'LED_BLUE')
                    new_rec_summary.rename(columns={'Light': 'EXC'}, inplace=True)
                    new_rec_summary.rename(columns={'Intensity': 'LEVEL'}, inplace=True)
                    new_rec_summary.rename(columns={'Exposure': 'EXPO'}, inplace=True)
                    new_rec_summary['EXPO'] = new_rec_summary['EXPO'].replace('40ms/50ms', '40ms')
                    new_rec_summary.insert(6, 'EMI', ['GREEN']*new_rec_summary.shape[0])
                    new_rec_summary.insert(7, 'FRAMES', frames)
                    new_rec_summary.insert(8, 'FPS', ['20Hz']*new_rec_summary.shape[0])
                    new_rec_summary.insert(9, 'CAM_TRIG_MODE', [CAM_TRIG_MODE[1]]*new_rec_summary.shape[0])
                    new_rec_summary.rename(columns={'Slice_#': 'SLICE'}, inplace=True)
                    new_rec_summary.rename(columns={'Cell/Pos': 'AT'}, inplace=True)
                    new_rec_summary.rename(columns={'Puff': EXP_SETTING[0]}, inplace=True)
                    new_rec_summary.rename(columns={'P.Conc': EXP_SETTING[1]}, inplace=True)
                    new_rec_summary.insert(14, 'ONSET', ['Frame_101(5s)']*new_rec_summary.shape[0])
                    new_rec_summary.rename(columns={'P.Period': EXP_SETTING[2]}, inplace=True)
                    new_rec_summary.rename(columns={'P.Pulses': EXP_SETTING[3]}, inplace=True)
                    new_rec_summary.rename(columns={'P.Interval': 'PUFF_GAP'}, inplace=True)
                    new_rec_summary.rename(columns={'P.Pressure': EXP_SETTING[4]}, inplace=True)
                    new_rec_summary.rename(columns={'Bathed_with': EXP_SETTING[5]}, inplace=True)
                    new_rec_summary['BATH_IN'] = new_rec_summary['BATH_IN'].replace('Reco_ACSF', 'ACSF')
                    new_rec_summary.rename(columns={'B.Conc.': EXP_SETTING[6]}, inplace=True)
                    new_rec_summary.rename(columns={'B.Flowed': EXP_SETTING[7]}, inplace=True)
                    
                    if row_idx == 0:
                        print("New REC Summary:")
                        print(tabulate(new_rec_summary, headers='keys', showindex=True, tablefmt="simple"))
                    
                    for col_idx, name in enumerate(new_rec_summary.columns.tolist()[2:]):
                        context_kept.append(f"{name}: {new_rec_summary.iloc[row_idx, col_idx+2]}")
                    
                    backup.append(context)
                    if row_idx == 0:
                        print("Updated Content", context_kept)
                    
                    if update_content_check:
                        with open(rec, mode="w", encoding="utf-16-LE") as f:
                            f.write('\n'.join(context_kept))
                
                if save_backup:
                    if not os.path.exists(os.path.join(rec_filepath, "backups")):
                        os.mkdir(os.path.join(rec_filepath, "backups"))
                        
                    backup_path=os.path.join(rec_filepath, f"backups/recs_backup_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
                    with open(backup_path, mode="w") as f:
                        json.dump(backup, f, indent=4)
                    
                    new_rec_summary.to_csv(os.path.join(rec_filepath, f"{rec_filepath.split('/')[-1]}_summary.csv"), index=False)
            else:
                print("Update Cancelled: No JSON file was selected!")
    else:
        print("No rec files found in the selected folder, please try again!")
else:
    print("Update Cancelled: No REC folder was selected!")
    