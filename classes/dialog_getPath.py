## Author: Kang
## Last Update: 2025-Jan-25
## Purpose: To generate a dialog to request a directory

from PySide6.QtWidgets import QFileDialog

class GetPath(QFileDialog):
    def __init__(self, title="Please select a folder of file", filemode='dir', filetype='excel', init_dir=''):
        super().__init__()
        if filemode == 'dir':
            self.setFileMode(QFileDialog.Directory)
            self.setOption(QFileDialog.ShowDirsOnly)
            self.setDirectory(init_dir)
        else:
            self.setFileMode(QFileDialog.ExistingFile)
            self.setDirectory(init_dir)
            match filetype:
                case 'excel':
                    self.setNameFilter("Excel Files (*.xlsx *.xls)")
                    
                case 'csv':
                    self.setNameFilter("CSV Files (*.csv)")
                    
                case 'json':
                    self.setNameFilter("JSON Files (*.json)")
                    
                case 'text':
                    self.setNameFilter("Text Files (*.txt)")

                    


        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setWindowTitle(title)
        
    def get_path(self):
        if self.exec():
            return self.selectedFiles()[0]
        else:
            return ""
        