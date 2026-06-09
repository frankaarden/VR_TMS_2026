import os
import numpy as np
from simnibs import sim_struct, run_simnibs

# Preliminaries
project_path = os.path.join("C:", os.sep, "prg-win", "3_projects", "2026_vr_tms")
subjects = [f"sub-{s:03d}" for s in range(2, 3)]
distances = range(4,41)

# Run simulations
for subject in subjects:
    for distance in distances:
        out_dir = os.path.join(project_path, "sims", subject, f"F3_{distance}mm")
        os.makedirs(out_dir, exist_ok=True)

        S = sim_struct.SESSION()
        S.fnamehead = os.path.join(project_path, "data", subject, f"{subject}.msh") 
        S.pathfem = os.path.join(project_path, "sims", subject, f"F3_{distance}mm")
        S.fields = 'eE'
        S.open_in_gmsh = False
        tms = S.add_tmslist()
        tms.fnamecoil = os.path.join(project_path, "data", "coil", 'MagVenture_Cool-B65.ccd')
        pos = tms.add_position()
        pos.centre = 'F3'  
        pos.pos_ydir = 'Fz'  
        pos.distance = distance  
        pos.didt = 1000000 * 1.49
        run_simnibs(S)