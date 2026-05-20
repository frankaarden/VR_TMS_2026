import matplotlib
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 16
import matplotlib.pyplot as plt

OUT = 'figure_4_C.png'

positions = ["0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"]

data = [
    [0.36, 2.29, 4.78, 0.81, 3.46, 1.09, 1.55, 2.62],
    [16.81, 17.53, 9.06, 1.09, 14.07, 16.70, 11.40, 12.52],
    [3.32, 8.11, 4.37, 2.57, 5.19, 7.08, 6.96, 5.52],
    [0.84, 2.41, 1.85, 4.54, 1.19, 2.94, 0.20, 0.84],
    [2.04, 9.92, 7.49, 0.64, 2.33, 9.66, 8.62, 8.41],
]

colors = ['#E97132', '#A02B93', '#156082', '#196B24', '#0F9ED5']
data_by_pos = list(map(list, zip(*data)))

fig, ax = plt.subplots(figsize=(12, 7))
ax.boxplot(data_by_pos, vert=True, patch_artist=True, whis=(0, 100),
           medianprops=dict(color='black', linewidth=2),
           boxprops=dict(facecolor='white', color='black', linewidth=1.2),
           whiskerprops=dict(color='black', linewidth=1.2),
           capprops=dict(color='black', linewidth=1.2))

for sub_i, sub_data in enumerate(data):
    for pos_i, val in enumerate(sub_data):
        ax.plot(pos_i + 1, val, 'o', color=colors[sub_i], markersize=7, zorder=3,
                label=f'Sub {sub_i+1}' if pos_i == 0 else '')

ax.set_xticks(range(1, len(positions) + 1))
ax.set_xticklabels(positions, fontsize=22)
ax.set_ylabel('Coil-to-scalp distance displacement (mm)', fontsize=16)
ax.tick_params(labelsize=14)
ax.legend(fontsize=16, loc='upper left', bbox_to_anchor=(1, 1))
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(bottom=0, top=46)

plt.tight_layout(rect=[0, 0, 0.88, 1])
plt.savefig(OUT, dpi=600, bbox_inches='tight')
plt.close()