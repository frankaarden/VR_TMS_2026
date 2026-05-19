# VR_TMS_2026

What's here 


**distance_per_position.py** — compares two Localite XML files one marker at a time. Used for Subject 1, where each coil position was saved as a separate file. Calculates displacement along the coil-to-scalp axis (Localite X = SimNIBS Z).

**distance_26_orientations.py** — compares two multi-position XML files. Used for Subjects 2–5, where all 26 EEG positions × 8 coil orientations are stored in one file. Same displacement metric as above.

**simulations.py** — runs SimNIBS TMS simulations for all 5 subjects at coil-to-scalp distances from 4 to 40 mm (1 mm steps). Uses MagVenture Cool-B65 coil, F3 target with previously individually defined coordinates.

**roi_mask_and_analysis.py** — defines a fixed ROI within the 4 mm baseline simulation as a 10 mm diameter sphere limited to GM mask, center at the peak E voxel. This ROI is applied to all distances. Then the field parameters (min, mean, median, P98, P99, max) within the fixed ROI and globally across GM are extracted, the focality is taken from the SimNIBS logs. MSO scaling factors and normalized focality are calculated relative to the 4 mm baseline. Output - one Excel file with one sheet per subject + summary.

(ROI quality check (confirming peak location matches stimulation site) was performed separately — MNI coordinates of peak voxels are available on request.)


## Important

All scripts require to set paths at the top of each file.
Raw MRI data and head models are not included. 


## Requirements

```
pip install -r requirements.txt
```

SimNIBS must be installed separately: https://simnibs.github.io/simnibs/

Instrument marker generation by Zsolt Turi:
https://github.com/ZsoltTuri/2025_AR_TMS/blob/main/fun/create_instrument_markers.m

---

## Acknowledgements

Code architecture, troubleshooting and error handling were supported in part by AI-assisted programming tools (Claude, Anthropic). Core methodology, domain logic and all scientific decisions are from original research.

Special thanks to Zsolt Turi for the instrument marker generation code and for his generous support throughout this project.
