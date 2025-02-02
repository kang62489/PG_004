## Author: Kang
## Last Update: 2025-Feb-02
## Purpose: recover the metadata in the comment of each recording file

import os
import json
from classes import dialog_getPath

def recovery(rec_filepath, rec_list):
    # Get the path of the *_REC_summary_updated.json file
    dlg_json = dialog_getPath.GetPath(title='Select the *_REC_summary_updated.json file', filemode = 'file', filetype='json', init_dir=os.path.join(rec_filepath,'backups'))
    json_filepath = dlg_json.get_path()
    if os.path.exists(json_filepath):
        with open(json_filepath, mode="r") as f:
            backup = json.load(f)

        for olddata, rec in zip(backup, rec_list):
            with open(rec, mode="w", encoding="utf-16-LE") as f:
                f.write('\n'.join(olddata))
        print("Recovery Completed!")
    else:
        print("Recovery Cancelled!")