## Author: Kang
## Last Update: 2025-Jan-24
## Purpose: Create a database and table in SQLite3

import sqlite3
import random
from tabulate import tabulate
import pandas as pd
from rich import print
conn = sqlite3.connect('mydatabase.db')

OBJ = ['10X', '60X']
EXC = ['HLG', 'LED']
LEVEL = ['LV9', 'LV6', 'LVMAX']
EMI = ['IR', 'GREEN', 'RED']
SLICE = ['1', '2', '3']
SAMPLE = ['1', '2', '3']
FRAMES =['1200p','1000p','10p']
FPS =['20hz']
CAM_TRIG_MODE = ['EXT EXP START', 'EXT EXP CTRL']

# Create a cursor
cursor = conn.cursor()


## Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        timestamp TEXT,
        OBJ TEXT,
        EXC TEXT,
        LEVEL TEXT,
        EMI TEXT,
        SLICE TEXT,
        SAMPLE TEXT,
        FRAMES TEXT,
        FPS TEXT,
        "CAM.TRIG.MODE" TEXT
    )
''')

## Insert data
# for i in range(10):
#     cursor.execute('''
#         INSERT INTO records (filename, timestamp, OBJ, EXC, LEVEL, EMI, SLICE, SAMPLE, FRAMES, FPS, "CAM.TRIG.MODE")
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
#         (f'file_{i+1}', '2025-01-24 12:00:00', '1', '1', '1', '1', '1', '1', '1', '1', '1')
#     )
# cursor.execute('''DELETE FROM records WHERE id BETWEEN 1 AND 9''')

## Update data
for i in range(10):
    cursor.execute('''UPDATE records SET
                        OBJ = ?,
                        EXC = ?,
                        LEVEL = ?,
                        EMI = ?,
                        SLICE = ?,
                        SAMPLE = ?,
                        FRAMES = ?,
                        FPS = ?,
                        "CAM.TRIG.MODE" = ?
                        WHERE id = ?''',(random.choice(OBJ),
                                        random.choice(EXC),
                                        random.choice(LEVEL),
                                        random.choice(EMI),
                                        random.choice(SLICE),
                                        random.choice(SAMPLE),
                                        random.choice(FRAMES),
                                        random.choice(FPS),
                                        random.choice(CAM_TRIG_MODE),
                                        i+1))

conn.commit()

## Select data and save in a dataframe then print with tabulate
cursor.execute("SELECT * FROM records;")
rows = cursor.fetchall()
colNames = [desc[0] for desc in cursor.description]
print(" | ".join(colNames))
df = pd.DataFrame(rows, columns=colNames)

df_sorted = df.sort_values(by=['SLICE','SAMPLE'])
print(tabulate(df_sorted, headers=df.columns, tablefmt='pretty'))

