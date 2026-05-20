import re
import numpy as np
import pandas as pd
import nibabel as nib
from pathlib import Path
from nibabel.processing import resample_from_to

# paths
OUT_BASE   = Path("path/simulation_output_folder")
OUTPUT_DIR = OUT_BASE / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

subjects = [
    {'id': 'sub1', 'output_base': OUT_BASE / "sub_1", 'f3_coords': [-48.95, 73.94, 61.49], 'm2m_path': Path("path/m2m_sub1")},
    {'id': 'sub2', 'output_base': OUT_BASE / "sub_2", 'f3_coords': [-55.02, 59.11, 39.39], 'm2m_path': Path("path/m2m_sub2")},
    {'id': 'sub3', 'output_base': OUT_BASE / "sub_3", 'f3_coords': [-49.94, 55.76, 37.07], 'm2m_path': Path("path/m2m_sub3")},
    {'id': 'sub4', 'output_base': OUT_BASE / "sub_4", 'f3_coords': [-47.43, 77.26, 52.32], 'm2m_path': Path("path/m2m_sub4")},
    {'id': 'sub5', 'output_base': OUT_BASE / "sub_5", 'f3_coords': [-57.02, 87.99, 60.18], 'm2m_path': Path("path/m2m_sub5")},
]

distances       = list(range(4, 41))
roi_diameter_mm = 10
# identifies the gray matter (GM) nii.gz of the headmodel, if not found searches for compartment 2 (GM) in the final tissues
def load_gm_mask(m2m_path, target_affine, target_shape):
    def to_bool(nii_obj):
        data = nii_obj.get_fdata()
        if data.ndim == 4:
            data = data[..., 0]
        mask = data > 0.5
        if mask.shape == target_shape:
            return mask
        nii_3d = nib.Nifti1Image(mask.astype(np.float32), nii_obj.affine)
        return resample_from_to(nii_3d, (target_shape, target_affine), order=0).get_fdata() > 0.5
    gm_file = Path(m2m_path) / "gm.nii.gz"
    if gm_file.exists():
        return to_bool(nib.load(str(gm_file)))
    ft_file = Path(m2m_path) / "final_tissues.nii.gz"
    if ft_file.exists():
        nii  = nib.load(str(ft_file))
        data = nii.get_fdata()
        if data.ndim == 4:
            data = data[..., 0]
        return to_bool(nib.Nifti1Image((data == 2).astype(np.float32), nii.affine))
    print(f"no GM mask found in {m2m_path}")
    return None
# builds a spherical roi mask around the peak E element in the GM, limits it to GM
def build_roi(magnE_file, gm_mask, diameter_mm=roi_diameter_mm):
    nii  = nib.load(str(magnE_file))
    data = nii.get_fdata()
    if gm_mask is not None:
        peak_vox = np.array(np.unravel_index(np.argmax(data * gm_mask), data.shape))
    else:
        peak_vox = np.array(data.shape) // 2
    r = diameter_mm / 2
    x, y, z = np.ogrid[:data.shape[0], :data.shape[1], :data.shape[2]]
    sphere = np.sqrt((x-peak_vox[0])**2 + (y-peak_vox[1])**2 + (z-peak_vox[2])**2) <= r
    roi = sphere & gm_mask if gm_mask is not None else sphere
    return roi, peak_vox
# exports the field valus from the defined roi
def field_stats(arr):
    if len(arr) == 0:
        return {'min': 0, 'mean': 0, 'median': 0, 'p98': 0, 'p99': 0, 'max': 0}
    return {
        'min':    np.min(arr),
        'mean':   np.mean(arr),
        'median': np.median(arr),
        'p98':    np.percentile(arr, 98),
        'p99':    np.percentile(arr, 99),
        'max':    np.max(arr)
    }
# exports the focality values from the simulation log files
def get_focality(log_file):
    try:
        content = Path(log_file).read_text()
        m = re.search(r'\|magnE\s+\|\s*([\d.e+]+)\s*mm[^|]*\|\s*([\d.e+]+)\s*mm', content)
        if m:
            return float(m.group(1)), float(m.group(2))
    except Exception as e:
        print(f"  log warning: {e}")
    return None, None

def analyze_subject(sub):
    sub_id      = sub['id']
    output_base = sub['output_base']
    m2m_path    = sub['m2m_path']
    print(f"\n{sub_id}")
    # identifies the reference (4mm) simulation, builds the roi
    ref_magnE = list((output_base / "distance_4mm").glob("subject_volumes/*_magnE.nii.gz"))
    if not ref_magnE:
        print("  4mm simulation not found")
        return None

    ref_nii = nib.load(str(ref_magnE[0]))
    gm      = load_gm_mask(m2m_path, ref_nii.affine, ref_nii.shape)
    roi, peak_vox = build_roi(ref_magnE[0], gm)
    print(f"  ROI: {int(np.sum(roi))} GM voxels, peak={peak_vox}")

    results, ref_params = [], None
    # identifies field values and focality in all simulations
    for d in distances:
        magnE = list((output_base / f"distance_{d}mm").glob("subject_volumes/*_magnE.nii.gz"))
        logs  = list((output_base / f"distance_{d}mm").glob("*.log"))
        if not magnE or not logs:
            print(f"  {d}mm not found")
            continue
        try:
            roi_vals  = nib.load(str(magnE[0])).get_fdata()[roi]
            roi_vals  = roi_vals[roi_vals > 0]
            glob_data = nib.load(str(magnE[0])).get_fdata()
            glob_vals = glob_data[(glob_data > 0) & ~np.isnan(glob_data)]
            f75, f50  = get_focality(logs[0])
            roi_s  = field_stats(roi_vals)
            glob_s = field_stats(glob_vals)
            row = {
                'subject_id':  sub_id,
                'distance_mm': d,
                'roi_min':     roi_s['min'],
                'roi_mean':    roi_s['mean'],
                'roi_median':  roi_s['median'],
                'roi_p98':     roi_s['p98'],
                'roi_p99':     roi_s['p99'],
                'roi_max':     roi_s['max'],
                'glob_min':    glob_s['min'],
                'glob_mean':   glob_s['mean'],
                'glob_median': glob_s['median'],
                'glob_p98':    glob_s['p98'],
                'glob_p99':    glob_s['p99'],
                'glob_max':    glob_s['max'],
                'focality_75': f75,
                'focality_50': f50,
                'roi_voxels':  int(np.sum(roi))
            }
            if d == 4:
                ref_params = {}
                for k, v in row.items():
                    if k in ('subject_id', 'distance_mm'):
                        continue
                    if isinstance(v, (int, float)) and v > 0:
                        ref_params[k] = v
            results.append(row)
            print(f"  {d}mm done  roi_p98={roi_s['p98']:.3f}  f75={f75}")
        except Exception as e:
            print(f"  {d}mm error {e}")

    if not results:
        return None
    # determines the mso increase factor and the degree of focality increase in comparison to the reference simulation values
    df = pd.DataFrame(results)
    if ref_params:
        for col, ref_val in ref_params.items():
            if col in df.columns and col not in ('focality_75', 'focality_50'):
                df[f'{col}_mso_factor'] = ref_val / df[col]
        for col in ['focality_75', 'focality_50']:
            ref_val = ref_params.get(col)
            if ref_val and ref_val > 0:
                df[f'{col}_norm'] = df[col] / ref_val
    return df

def main():
    all_dfs = []
    for sub in subjects:
        df = analyze_subject(sub)
        if df is not None:
            all_dfs.append(df)
    if not all_dfs:
        print("No data found")
        return
    excel_path = OUTPUT_DIR / "analysis.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for df in all_dfs:
            df.to_excel(writer, sheet_name=df['subject_id'].iloc[0], index=False)
        summary = []
        for df in all_dfs:
            sid = df['subject_id'].iloc[0]
            for _, row in df.iterrows():
                summary.append({
                    'subject_id':         sid,
                    'distance_mm':        row['distance_mm'],
                    'roi_p98_mso_factor': row.get('roi_p98_mso_factor'),
                    'focality_75_norm':   row.get('focality_75_norm'),
                    'focality_50_norm':   row.get('focality_50_norm')
                })
        pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)
    print(f"\nSaved: {excel_path.name}")

if __name__ == "__main__":
    main()
