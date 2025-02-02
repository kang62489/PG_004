## Author: Kang
## Last Update: 2025-Feb-02
## Purpose: Scan the texts in each recording file

import tifffile
import pandas as pd
from pathlib import Path

def scan_contents(rec_list):
    list_of_kept_contents = []
    list_of_original_contents = []
    for rec in rec_list:
        with open(rec, mode="r", encoding="utf-16-LE") as f:
            content = f.read().splitlines()
            list_of_original_contents.append(content)
            kept_content_until = 0
            for line_num, line in enumerate(content):
                if 'Comment:' in line:
                    kept_content_until = line_num + 1
                    break
            
            kept_content = content[:kept_content_until]
            kept_content.append("")
            list_of_kept_contents.append(kept_content)
    
    return list_of_kept_contents, list_of_original_contents

def generate_summary(rec_list):
    filenames = []
    timestamps =[]
    comments = []
    EXPO = []
    rec_summary = pd.DataFrame()
    
    # Get the number of frames in each tif file
    frames = []
    for rec in rec_list:
        print("Processing: ", Path(rec).stem)
        tif_path = rec.replace('.rec', '')
        with tifffile.TiffFile(tif_path) as img:
            frames.append(f"{len(img.pages)}p")
    
    for rec in rec_list:
        filenames.append(Path(rec).stem)
        with open(rec, mode="r", encoding="utf-16-LE") as f:
            content = f.read().splitlines()
            for idx, line in enumerate(content):
                if 'Time:' in line:
                    timestamps.append(line.split(' ')[-1])
                if 'Exposure / Delay' in line:
                    EXPO.append(line.split(' ')[-5].split('.')[0]+line.split(' ')[-4])
                if 'Comment:' in line:
                    extract_content_from_line = idx + 1
                    break
        
        comments.append(" ".join(content[extract_content_from_line:]))
        
    rec_summary['Filename'] = filenames
    rec_summary['Timestamp'] = timestamps
    rec_summary['EXPO']= EXPO
    rec_summary['Frames'] = frames
    rec_summary['Comments'] = comments
    
    return rec_summary