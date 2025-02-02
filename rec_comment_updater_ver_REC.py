## Author: Kang
## Last Update: 2025-Feb-03
## Purpose: update the metadata in the comment of each recording file
## based on the context in the comment of each recording file

import os
import sys
import json
from datetime import datetime
from tabulate import tabulate
from glob import glob
from PySide6.QtWidgets import QApplication
from rich import print
from classes import GetPath, Confirm
from functions import recovery, scan_contents, generate_summary, contentUpdater

# Set event handler
app = QApplication(sys.argv)

# Get the path of the folder containing the rec files
dlg_recs = GetPath(title='Select a folder of rec files', filemode = 'dir')
rec_filepath = dlg_recs.get_path()

# Control terms
recovery_mode = False

# Read and update the metadata in each rec file
if os.path.exists(rec_filepath):
    rec_list = sorted(glob(rec_filepath + '/*.rec'))
    if rec_list != []:
        if recovery_mode:
            recovery(rec_filepath, rec_list)
        else:
            list_of_kept_contents, list_of_original_contents = scan_contents(rec_list)
            rec_summary = generate_summary(rec_list)
            
            print(tabulate(rec_summary, headers='keys', showindex=True, tablefmt="pretty"))
            
            # Make a new summary dataframe based on comments
            new_rec_summary = rec_summary.iloc[:, :2]
            BASIC = [
                'OBJ',
                'EXC',
                'LEVEL',
                'EXPO',
                'EMI',
                'FRAMES',
                'FPS',
                'CAM_TRIG_MODE',
                'SLICE',
                'AT',
            ]
            
            CAM_TRIG_MODE = ['EXT_EXP_CTRL', 'EXT_EXP_START']
            
            # Check and extract information from the comments
            OBJ =[None]*rec_summary.shape[0]
            EXC = [None]*rec_summary.shape[0]
            LEVEL = [None]*rec_summary.shape[0]
            EMI = [None]*rec_summary.shape[0]
            SLICE = [None]*rec_summary.shape[0]
            AT = [None]*rec_summary.shape[0]
            
            checklist_01 = ['10x', '10X', '60x', '60X']
            checklist_02 = ['GREEN', 'Green', 'RED', 'Red', 'GFP', 'mCherry', 'IRDIC', 'IR']
            checklist_03 = ['LV3', 'LV4', 'LV6', 'LV8', 'LV9', 'max', 'MAX', 'LVMAX', 'LV']
            checklist_04 = ['slice', 'Slice', 'slide', 'Slide']
            checklist_05 = ['cell', 'Cell', 'pos', 'Pos']
            
            # Scan the comments for "basic" information
            for row, comment in enumerate(rec_summary['Comments']):
                comment_parts = comment.split(' ')
                for findStr_01 in checklist_01:
                    if findStr_01 in comment_parts:
                        OBJ[row] = findStr_01.upper()
                        break
                
                for findStr_02 in checklist_02:
                    if findStr_02 in comment_parts:
                        if findStr_02 in ['Green', 'GFP', 'GREEN']:
                            EXC[row] = 'LED_BLUE'
                            EMI[row] = 'GREEN'
                        elif findStr_02 in ['Red', 'mCherry', 'RED']:
                            EXC[row] = 'LED_GREEN'
                            EMI[row] = 'RED'
                        elif findStr_02 in ['IRDIC', 'IR']:
                            EXC[row] = 'HLG'
                            EMI[row] = 'IR'
                        else:
                            pass
                        break
                
                for findStr_03 in checklist_03:
                    if findStr_03 in comment_parts:
                        if findStr_03 == 'LVMAX':
                            LEVEL[row] = 'MAX'
                        elif findStr_03 == 'LV':
                            if comment_parts[comment_parts.index(findStr_03)+1] in ['MAX','max']:
                                LEVEL[row] = 'MAX'
                            else:
                                LEVEL[row] = 'LV'+ comment_parts[comment_parts.index(findStr_03)+1]
                        elif findStr_03 == 'MAX':
                            LEVEL[row] = 'MAX'
                        elif findStr_03 == 'max':
                            LEVEL[row] = 'MAX'
                        else:
                            LEVEL[row] = findStr_03.upper()
                        break
                
                for findStr_04 in checklist_04:
                    if findStr_04 in comment_parts:
                        idx = comment_parts.index(findStr_04)
                        SLICE[row]=comment_parts[idx+1].lstrip('0')
                        break
                
                for findStr_05 in checklist_05:
                    if findStr_05 in comment_parts:
                        idx = comment_parts.index(findStr_05)
                        if findStr_05 in ['cell', 'Cell']:
                            AT[row]='CELL_'+comment_parts[idx+1].lstrip('0')
                        elif findStr_05 in ['pos', 'Pos']:
                            AT[row]='SITE_'+comment_parts[idx+1].lstrip('0')
                        else:
                            pass
                        break
                
            new_rec_summary['OBJ'] = OBJ
            new_rec_summary['EXC'] = EXC
            new_rec_summary['LEVEL'] = LEVEL
            new_rec_summary['EXPO'] = rec_summary['EXPO']
            new_rec_summary['EMI'] = EMI
            new_rec_summary['FRAMES'] = rec_summary['Frames']
            new_rec_summary['FPS'] = '20Hz'
            new_rec_summary['CAM_TRIG_MODE'] = CAM_TRIG_MODE[1]
            new_rec_summary['SLICE'] = SLICE
            new_rec_summary['AT'] = AT
            
            # Extract the conditions from the comments
            EXP_SETTINGS = {
                'ABF_SERIAL': False,
                'PUMP': False,
                'PUFF': False,
                "PUFF": False,
                "PUFF_CONC": False,
                "PUFF_PERIOD": False,
                "PUFF_COUNT": False,
                "PUFF_PRESSURE": False,
                "BATHED_IN": False,
                "BATHED_CONC": False,
                "FLOWED": False,
            }
            
            EXP_CHECKLISTS = {
                'ABF_SERIAL':['abf', 'ABF', 'Patch', 'ABF_#', 'pclamp'],
                'PUMP':['pump', 'Pump', 'PUMP']
            }
            
            CONDITIONS = EXP_SETTINGS['PUMP'] = True
            
            for cond in EXP_SETTINGS.keys():
                if EXP_SETTINGS[cond]:
                    print(f"Condition: {cond} added!")
                    new_rec_summary[cond] = [None]*rec_summary.shape[0]
            
            for row, comment in enumerate(rec_summary['Comments']):
                comment_parts = comment.split(' ')
                for cond in EXP_SETTINGS.keys():
                    if EXP_SETTINGS[cond]:
                        for findStr in EXP_CHECKLISTS[cond]:
                            if findStr in comment_parts:
                                idx = comment_parts.index(findStr)
                                new_rec_summary.loc[row, cond]=comment_parts[idx+1]
                                break
            
            print(tabulate(new_rec_summary, headers='keys', showindex=True, tablefmt="pretty"))
            
            new_contents = contentUpdater(new_rec_summary, list_of_kept_contents)
            print("Content to be updated (last one): \n")
            print(new_contents[-1])
            
            # Update the content to each rec file
            dlg_checkUpdate = Confirm(title='Update the REC files?', msg='Do you want to update the REC files?')
            if dlg_checkUpdate.exec():
                # Save the backup and the new summary
                if not os.path.exists(os.path.join(rec_filepath, "backups")):
                    os.mkdir(os.path.join(rec_filepath, "backups"))
                
                backup_path=os.path.join(rec_filepath, f"backups/backup_recs_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
                with open(backup_path, mode="w") as f:
                    json.dump(list_of_original_contents, f, indent=4)
                    print(f"Backup saved!")

                new_rec_summary.to_csv(os.path.join(rec_filepath, f"{rec_filepath.split('/')[-1]}_summary.csv"), index=False)
                print(f"New summary saved!")
                
                for file in rec_list:
                    with open(file, mode="w", encoding="utf-16-LE") as f:
                        f.write('\n'.join(new_contents[rec_list.index(file)]))
                print("All recording files are updated!")
                
            else:
                print("Content update cancelled!")
    else:
        print("No rec files found in the selected folder, please try again!")
else:
    print("Update Cancelled: No REC folder was selected!")
    