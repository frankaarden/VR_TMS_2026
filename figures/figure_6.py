import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D

mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.size'] = 16
mpl.rcParams['axes.linewidth'] = 0.8

# paths
EXCEL    = 'path/analysis.xlsx'
OUT      = 'figure_6.png'
BB_DIST  = 9.6   # mean BB coil-to-scalp distance at F3 (mm)
MQ2_DIST = 35.1  # mean MQ2 coil-to-scalp distance at F3 (mm)
LIMIT    = 2.4   # maximum feasible MSO scaling factor


xl   = pd.ExcelFile(EXCEL)
subs = [s for s in xl.sheet_names if s.startswith('sub')]
dist = np.arange(4, 41)

def mean_across(col):
    arrays = []
    for s in subs:
        df = pd.read_excel(EXCEL, sheet_name=s).set_index('distance_mm')
        if col in df.columns:
            arrays.append(df.reindex(dist)[col].values)
    return np.nanmean(arrays, axis=0) if arrays else None

mean_min  = mean_across('roi_min_mso_factor')
mean_mean = mean_across('roi_mean_mso_factor')
mean_p98  = mean_across('roi_p98_mso_factor')

fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.axhline(LIMIT, color='#C0392B', linewidth=0.9, linestyle='--', alpha=0.85, zorder=1)

for d, label in [(BB_DIST, f'BB ({BB_DIST} mm)'), (MQ2_DIST, f'MQ2 ({MQ2_DIST} mm)')]:
    y_top = float(np.interp(d, dist, mean_p98)) if mean_p98 is not None else LIMIT
    ax.plot([d, d], [0.8, y_top], color='#aaaaaa', linewidth=0.7, zorder=2)
    ax.text(d + 0.4, (0.8 + y_top) / 2, label, fontsize=8, color='#444444', va='center', ha='left')

if mean_min  is not None: ax.plot(dist, mean_min,  color='#499C8E', linewidth=1.5, zorder=3)
if mean_mean is not None: ax.plot(dist, mean_mean, color='#49579C', linewidth=1.5, zorder=3)
if mean_p98  is not None: ax.plot(dist, mean_p98,  color='#9C8E49', linewidth=1.5, zorder=3)

ax.set_xlabel('Coil-to-scalp distance (mm)', fontsize=16)
ax.set_ylabel('Required MSO% factor', fontsize=16)
ax.set_xlim(2, 42)
ax.set_ylim(0.8, 5.0)
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(labelsize=10)

ax.legend(handles=[
    Line2D([0],[0], color='#499C8E', linewidth=1.5, label='Minimum E-field strength'),
    Line2D([0],[0], color='#49579C', linewidth=1.5, label='Mean E-field strength'),
    Line2D([0],[0], color='#9C8E49', linewidth=1.5, label='P98 E-field strength'),
    Line2D([0],[0], color='#C0392B', linewidth=0.9, linestyle='--', label='Upper limit (×2.4)'),
    Line2D([0],[0], color='#aaaaaa', linewidth=0.7, label='Mean device distance at F3'),
], fontsize=14, frameon=False, loc='upper left')

plt.tight_layout()
fig.savefig(OUT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()