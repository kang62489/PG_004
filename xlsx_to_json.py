## Author: Kang
## Last Update: 2025-Jan-25
## Purpose: Extract infos and recs from the xlsx file and export them as json files

# Modules
import os
import sys
import pandas as pd
from classes import dialog_getPath
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

# Get the path of the xlsx file
dlg = dialog_getPath.GetPath(title="Please select a recording xlsx file", filemode='file')
xlsx_filepath = dlg.get_path()

# Extract infos and recs from the xlsx file
if os.path.exists(xlsx_filepath):
    # Read sheet 1 in the xlsx file
    df_1 = pd.read_excel(xlsx_filepath, sheet_name="dataLog",dtype={"Fluorescence Imaging Recording Basic Infos": str, 
                                                                  "Unnamed: 1": str,
                                                                  "Unnamed: 2": str,
                                                                  "Unnamed: 3": str,
                                                                  "Unnamed: 4": str,
                                                                  "Unnamed: 5": str,
                                                                  "Unnamed: 6": str,
                                                                  "Unnamed: 7": str,})
    df_1.fillna("", inplace=True)

    # Read sheet 2 in the xlsx file
    df_2 = pd.read_excel(xlsx_filepath,sheet_name="RECs",skiprows=[0],dtype={"Index #": str,
                                                                             "Slice #": str,
                                                                             "Cell #": str})
    
    df_2["Index #"] = df_1.iat[0,2].split(' ')[0].replace("-","_") + "_" + df_2["Index #"] + ".tif"
    df_2.rename(columns={"Index #":"Filename"},inplace=True)

    # Extract values from the corresponding cells in the sheet 1
    cellValues_dataLog = {
        "infos": {
            df_1.iat[0,0]: {
                df_1.iat[0,1]: df_1.iat[0,2].split(' ')[0].replace("-","_"),
                df_1.iat[1,1]: df_1.iat[1,2],
            },
            df_1.iat[2,0]: {
                df_1.iat[2,1]: df_1.iat[2,2],
                df_1.iat[2,5]: df_1.iat[2,6],
                df_1.iat[3,1]: df_1.iat[3,2],
                df_1.iat[3,5]: df_1.iat[3,6],
                df_1.iat[4,1]: df_1.iat[4,2].split(' ')[0],
                df_1.iat[4,5]: df_1.iat[4,6] + " weeks"
            },
            df_1.iat[5,0]: {
                df_1.iat[5,1]: df_1.iat[5,2],
                df_1.iat[5,5]: df_1.iat[5,6],
                df_1.iat[6,1]: df_1.iat[6,2] + " " + df_1.iat[6,3] + ", " + df_1.iat[6,4] + " " + df_1.iat[6,5] + ", " + df_1.iat[6,6] + " " + df_1.iat[6,7],
                df_1.iat[7,1]: df_1.iat[7,2],
                df_1.iat[8,1]: df_1.iat[8,2],
                df_1.iat[9,1]: df_1.iat[9,2].split(' ')[0],
                df_1.iat[9,5]: df_1.iat[9,6] + " weeks"
            },
            df_1.iat[10,0]: {
                df_1.iat[10,1]: df_1.iat[10,2] + ": " + df_1.iat[10,3] + "; " + df_1.iat[10, 5] + ": " + df_1.iat[10,6],
                df_1.iat[11,1]: df_1.iat[11,2] + ": " + df_1.iat[11,3] + "; " + df_1.iat[11, 5] + ": " + df_1.iat[11,6],
                df_1.iat[12,1]: df_1.iat[12,2] + ": " + df_1.iat[12,3] + "; " + df_1.iat[12, 5] + ": " + df_1.iat[12,6]
            },
            df_1.iat[13,0]: {
                df_1.iat[13,1]: df_1.iat[13,2],
                df_1.iat[13,5]: df_1.iat[13,6],
                df_1.iat[14,1]: df_1.iat[14,2],
                df_1.iat[15,1]: df_1.iat[15,2] + " ms",
                df_1.iat[16,1]: df_1.iat[16,2] + " ms",
                df_1.iat[17,1]: df_1.iat[17,2] + " Hz",
                df_1.iat[18,1]: df_1.iat[18,2] + " frames",
                df_1.iat[19,1]: df_1.iat[19,2] + " frames"
            }
        }
    }

    expInfo = pd.DataFrame(cellValues_dataLog)

    # Export dataFrame to the designate directory
    exportFilePath_1 = os.path.join(os.path.dirname(xlsx_filepath), df_1.iat[0,2].split(' ')[0].replace("-","_") + "_dataLog.json")
    exportFilePath_2 = os.path.join(os.path.dirname(xlsx_filepath), df_1.iat[0,2].split(' ')[0].replace("-","_") + "_RECs.json")
    
    with open(exportFilePath_1, "w", encoding="utf-8") as f:
        expInfo.to_json(f, indent=4, force_ascii=False)

    with open(exportFilePath_2, "w", encoding="utf-8") as g:
        df_2.to_json(g, orient="table", indent=4, force_ascii=False)
