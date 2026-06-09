import os
import pandas as pd
import numpy as np

project_path = os.path.join("C:", os.sep, "prg-win", "3_projects", "2026_vr_tms")
subjects = [f"sub-{s:03d}" for s in range(2, 3)]

f3_coords = []
for s, subject in enumerate(subjects, start=2):
    eeg_pos = pd.read_csv(os.path.join(project_path, "data", subject, f"m2m_{subject}", "eeg_positions", "EEG10-10_UI_Jurak_2007.csv"), header=None) 
    f3_row = eeg_pos[eeg_pos.iloc[:, 4] == "F3"]
    f3 = f3_row.iloc[0, 1:4].to_numpy()
    f3_coords.append(np.concatenate(([s], f3)))

f3_coords = np.asarray(f3_coords, dtype=np.float32)
np.save(os.path.join(project_path, "data", "F3_coords.npy"), f3_coords)