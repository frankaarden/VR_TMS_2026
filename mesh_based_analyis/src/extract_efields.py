import os
import numpy as np
import simnibs

# Preliminaries
project_path = os.path.join("C:", os.sep, "prg-win", "3_projects", "2026_vr_tms")
subjects = [f"sub-{s:03d}" for s in range(2, 3)]
distances = range(4,41)
coords = np.load(os.path.join(project_path, "data", "F3_coords.npy"), allow_pickle=True)  
rii = np.arange(5.0, 15.0 + 2.5, 2.5)   
smin = 2
rmax = max(rii)

# Extract E-fields
for s, subject in enumerate(subjects, start=2):
    f3_coords = coords[coords[:, 0] == s, 1:4][0]
        
    for distance in distances:
        mesh_dir = os.path.join(project_path, "sims", subject, f"F3_{distance}mm")
        head_mesh = simnibs.read_msh(os.path.join(mesh_dir, f"{subject}_TMS_1-0001_MagVenture_Cool-B65_scalar.msh")) 
        gray_matter = head_mesh.crop_mesh(2)
        elm_centers = gray_matter.elements_baricenters()[:]
        gm_dists = np.linalg.norm(elm_centers - f3_coords, axis=1)
        closest_idx = np.argmin(gm_dists)
        roi_center = elm_centers[closest_idx]

        for r in rii:            
            roi = np.linalg.norm(elm_centers - roi_center, axis=1) < r
            elm_vols = gray_matter.elements_volumes_and_areas()[:]
            gray_matter.add_element_field(roi, f"roi_radius-{r}mm") 
            field_name = "normE"
            field = gray_matter.field[field_name][:]
            if distance == 4:
                np.save(os.path.join(project_path, "sims", subject, 'elem_vols.npy'), elm_vols[roi]) 
            if distance == 4 and s == smin and r == rmax:
                gray_matter.write(os.path.join(project_path, "sims", subject, "gray_matter_with_roi.msh"))
                #gray_matter.view(visible_fields="roi").show()
            np.save(os.path.join(project_path, "sims", subject, f"E-fields_electrode-F3_distance-{distance}mm_radius-{r:.1f}mm.npy"), field[roi])