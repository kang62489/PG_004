---
Established: 2024-01-26
Last Updated: 2024-01-26
Description: The python programs used for update metadata in each recording file based on previous note files (JSON)
tags:
  - python
---
# OUTPUT
![](update_metadata_in_rec_files.png)

The program also generate a summary csv file and a "backups" folder for recovery
![](generated_files.png)
# MEMO
- A class of file dialog (dialog_getPath.py) is made to quickly generate a dialog for getting path of recording files or other types (xls, csv, json, text, ) of files.
- The xlsx_to_json.py is used for extracting values from an old template of expInfo and recs. I just keep it in case of future excel file applications.


