# VR_TMS_2026

What's here 

**distance_per_position.py** - compares two Localite XML files one-to-one. We have used this for Subject 1 where each position was saved as a separate file.

**distance_26_orientations.py** - compares two multi-position XML files. Use this for Subjects 2-5 where all 26 positions with 8 orientations each are in one file. Both scripts calculate displacement along the coil-scalp distance (Localite X axis = SimNIBS Z axis). 

**simulations.py** - runs SimNIBS simulations for all 5 subjects at 4-40 mm coil-to-scalp distance (1 mm steps). Requires SimNIBS 4.5 or newer and individual head models. 

**roi_mask_and_analysis.py** - defines a fixed ROI from the 4 mm simulation (10 mm diameter, spherical, but limited within GM; the center was defined as peak E voxel in GM, QC for matching with the stimulation site was performed separately), then extracts field parameters and focality (from logs) across all distances. Output - one Excel file.

**Requirements **

pip install numpy pandas matplotlib nibabel scipy openpyxl

Instrument marker generation by Zsolt Turi:  https://github.com/ZsoltTuri/2025_AR_TMS/blob/main/fun/create_instrument_markers.m
