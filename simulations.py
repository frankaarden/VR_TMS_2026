from pathlib import Path
from simnibs import sim_struct, run_simnibs

COIL     = "path/MagVenture_Cool-B65.ccd"
OUT_BASE = Path("path/output_folder")

subjects = [
    ('sub1', Path("path/m2m_sub1"), OUT_BASE / "sub_1", [-48.95, 73.94, 61.49]),
    ('sub2', Path("path/m2m_sub2"), OUT_BASE / "sub_2", [-55.02, 59.11, 39.39]),
    ('sub3', Path("path/m2m_sub3"), OUT_BASE / "sub_3", [-49.94, 55.76, 37.07]),
    ('sub4', Path("path/m2m_sub4"), OUT_BASE / "sub_4", [-47.43, 77.26, 52.32]),
    ('sub5', Path("path/m2m_sub5"), OUT_BASE / "sub_5", [-57.02, 87.99, 60.18]),
]

distances = list(range(4, 41))
done, fail = 0, 0

for sub_id, m2m, out_base, f3 in subjects:
    print(f"\n{sub_id}")
    for d in distances:
        out = out_base / f"distance_{d}mm"
        out.mkdir(parents=True, exist_ok=True)
        if list(out.glob("subject_volumes/*_magnE.nii.gz")):
            fail += 1
            continue
        S = sim_struct.SESSION()
        S.subpath   = str(m2m)
        S.pathfem   = str(out)
        S.overwrite = True
        tms = S.add_tmslist()
        tms.fnamecoil = COIL
        pos = tms.add_position()
        pos.centre   = f3
        pos.pos_ydir = [0, 1, 0]
        pos.distance = d
        S.map_to_vol  = True
        S.map_to_surf = False
        S.fields      = 'eEjJ'
        run_simnibs(S)
        print(f"  {d}mm done")
        done += 1

print(f"\ndone: {done}, fail: {fail}")