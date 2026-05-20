import matplotlib
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 16
import matplotlib.pyplot as plt

OUT = 'figure_4_B.png'

positions = ["0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"]

data = [
    [33.27, 26.14, 34.60, 30.07, 34.99, 37.11, 34.40, 36.12],
    [43.44, 43.16, 38.86, 31.45, 42.06, 42.65, 40.07, 40.71],
    [29.41, 32.08, 29.62, 22.58, 24.78, 30.90, 31.97, 29.32],
    [18.58, 23.83, 21.75, 13.49, 13.07, 24.74, 23.84, 21.73],
    [34.10, 35.78, 32.82, 25.87, 30.37, 36.32, 35.17, 32.95],
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