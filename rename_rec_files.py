## Author: Kang
## Last Updata: 2025-02-01
## Purpose: Rename recording files based on timestamps

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import pandas as pd
from glob import glob
from PySide6.QtWidgets import QApplication
from rich import print
from classes import dialog_getPath
from classes import dialog_confirm

# Set event handler
app = QApplication(sys.argv)

# Get the path of the folder containing the rec files
dlg_recs = dialog_getPath.GetPath(title='Select a folder of rec files', filemode = 'dir')
rec_filepath = dlg_recs.get_path()
recovery_mode = False

if os.path.exists(rec_filepath):
    rec_list = sorted(glob(rec_filepath + '/*.rec'))
    if rec_list != []:
        rec_summary = pd.DataFrame(columns=['Filename', 'Timestamp', 'Comments'])
        timestamps = []
        comments = []
        filenames =[]
        for row_idx, rec in enumerate(rec_list):
            filenames.append(Path(rec).stem)
            with open(rec, mode="r", encoding="utf-16-LE") as f:
                context = f.read().splitlines()
                for idx, line in enumerate(context):
                    if 'Time:' in line:
                        timestamps.append(line.split(' ')[-1])
                    if 'Comment:' in line:
                        kept_context_to_line = idx
                        break
                
                update_context_from = kept_context_to_line + 2
                comments.append(" ".join(context[update_context_from:]))

        rec_summary['Filename'] = filenames
        rec_summary['Timestamp'] = timestamps
        rec_summary['Comments'] = comments
        
        rec_summary_new = rec_summary.sort_values(by='Timestamp').reset_index(drop=True)
        
        new_names =[]
        date = Path(rec_filepath).name
        for row, filename in enumerate(rec_summary_new['Filename']):
            name = f"{date}-{row:04d}.tif"
            new_names.append(name)
        
        rec_summary_new['New Filename'] = new_names
        
        print(tabulate(rec_summary_new, headers='keys', showindex=True, tablefmt="pretty"))
        if recovery_mode == False:    
            dlg_confirm_rename = dialog_confirm.Confirm(title='Confirm to rename rec files', msg='Do you want to rename the rec and tif files?')
            if dlg_confirm_rename.exec():
                ## Save backup
                if os.path.exists(rec_filepath + '/backups') == False:
                    os.mkdir(rec_filepath + '/backups')
                
                backup_filepath = rec_filepath + '/backups'
                backup_filename = f"renamed_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
                rec_summary_new.to_csv(backup_filepath + '/' + backup_filename, index=False)
                
                for idx, original in enumerate(rec_summary_new['Filename']):
                    new = rec_summary_new['New Filename'][idx]
                    os.rename(rec_filepath + '/' + original + '.rec', rec_filepath + '/' + new + '.rec')
                    os.rename(rec_filepath + '/' + original , rec_filepath + '/' + new)
                    print(f"[green]{original} -> {new}[/green]")
                    print(f"[green]{original}.rec -> {new}.rec[/green]")
                    print("\n")
                    
                print(f"[green]Renaming completed![/green]")
            else:
                print(f"[red]Renaming cancelled![/red]")
        else:
            get_recovery = dialog_getPath.GetPath(title='Select a csv backup file', filemode = 'file', filetype='csv')
            csv_filepath = get_recovery.get_path()
            if os.path.exists(csv_filepath):
                rec_summary_recovery = pd.read_csv(csv_filepath)
                for idx, original in enumerate(rec_summary_recovery['Filename']):
                    new = rec_summary_recovery['New Filename'][idx]
                    os.rename(rec_filepath + '/' + new + '.rec', rec_filepath + '/' + original + '.rec')
                    os.rename(rec_filepath + '/' + new, rec_filepath + '/' + original)
                    print(f"[green]{new} -> {original}[/green]")
                    print(f"[green]{new}.rec -> {original}.rec[/green]")
                    print("\n")
                    
                print(f"[green]Recovery completed![/green]")
            else:
                print("Recovery cancelled!")
        
    else:
        print(f"[red]No rec files in the folder[/red]")
else:
    print(f"[red]No folder is selected[/red]")