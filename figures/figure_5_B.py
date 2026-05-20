import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D

mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.linewidth'] = 0.8

# path
EXCEL = 'path/analysis.xlsx'
OUT   = 'figure_5_B.png'


COLOR = '#9C8E49'

xl   = pd.ExcelFile(EXCEL)
subs = [s for s in xl.sheet_names if s.startswith('sub')]
dist = np.arange(4, 41)

p98_all = []
for s in subs:
    df = pd.read_excel(EXCEL, sheet_name=s).set_index('distance_mm')
    if 'roi_p98' in df.columns:
        p98_all.append(df.reindex(dist)['roi_p98'].values)

a         = np.array(p98_all)
mean_p98  = np.nanmean(a, axis=0)
sd_p98    = np.nanstd(a, axis=0, ddof=1)

fig, ax = plt.subplots(figsize=(5, 5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.fill_between(dist, mean_p98-sd_p98, mean_p98+sd_p98, color=COLOR, alpha=0.2, zorder=2)
ax.plot(dist, mean_p98, color=COLOR, linewidth=1.5, zorder=3)

ax.set_xlabel('Coil-to-scalp distance (mm)', fontsize=10)
ax.set_ylabel('P98 in ROI (V/m)', fontsize=10)
ax.set_xlim(2, 42)
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(labelsize=10)
ax.legend(handles=[
    Line2D([0],[0], color=COLOR, linewidth=1.5, label='P98 in ROI (mean ± SD)'),
], fontsize=9, frameon=False, loc='upper right')

plt.tight_layout()
fig.savefig(OUT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()