import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.lines import Line2D

mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.linewidth'] = 0.8

# paths
EXCEL = 'path/analysis.xlsx'
OUT   = 'figure_5_A.png'

COLOR_F75 = '#499C8E'
COLOR_F50 = '#49579C'

xl   = pd.ExcelFile(EXCEL)
subs = [s for s in xl.sheet_names if s.startswith('sub')]
dist = np.arange(4, 41)

f75_all, f50_all = [], []
for s in subs:
    df = pd.read_excel(EXCEL, sheet_name=s).set_index('distance_mm')
    if 'focality_75' in df.columns:
        f75_all.append(df.reindex(dist)['focality_75'].values)
    if 'focality_50' in df.columns:
        f50_all.append(df.reindex(dist)['focality_50'].values)

def mean_sd(arrays):
    a = np.array(arrays)
    return np.nanmean(a, axis=0), np.nanstd(a, axis=0, ddof=1)

mean_f75, sd_f75 = mean_sd(f75_all)
mean_f50, sd_f50 = mean_sd(f50_all)

fig, ax = plt.subplots(figsize=(5, 5))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

ax.fill_between(dist, mean_f75-sd_f75, mean_f75+sd_f75, color=COLOR_F75, alpha=0.2, zorder=2)
ax.fill_between(dist, mean_f50-sd_f50, mean_f50+sd_f50, color=COLOR_F50, alpha=0.2, zorder=2)
ax.plot(dist, mean_f75, color=COLOR_F75, linewidth=1.5, zorder=3)
ax.plot(dist, mean_f50, color=COLOR_F50, linewidth=1.5, zorder=3)

ax.set_xlabel('Coil-to-scalp distance (mm)', fontsize=10)
ax.set_ylabel('E-field spatial spread (mm³)', fontsize=10)
ax.set_xlim(2, 42)
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(labelsize=10)
ax.legend(handles=[
    Line2D([0],[0], color=COLOR_F75, linewidth=1.5, label='75% threshold (mean ± SD)'),
    Line2D([0],[0], color=COLOR_F50, linewidth=1.5, label='50% threshold (mean ± SD)'),
], fontsize=9, frameon=False, loc='upper left')

plt.tight_layout()
fig.savefig(OUT, dpi=600, bbox_inches='tight', facecolor='white')
plt.close()