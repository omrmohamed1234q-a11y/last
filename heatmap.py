import numpy as np
import math
import matplotlib.pyplot as plt
from data_utils import get_num_cols


def kde_distance_based(d, R):
    if d <= R:
        return (1 - (d / R) ** 2) ** 2
    else:
        return 0


def make_heatmap(df, x_col, y_col, R, grid_size):
    heat_df = df.dropna(subset=[x_col, y_col])
    if len(heat_df) == 0:
        return None

    X = heat_df[x_col].values
    Y = heat_df[y_col].values

    # make grid
    x_min, x_max = X.min(), X.max()
    y_min, y_max = Y.min(), Y.max()
    pad_x = (x_max - x_min) * 0.1
    pad_y = (y_max - y_min) * 0.1
    x_vals = np.linspace(x_min - pad_x, x_max + pad_x, grid_size)
    y_vals = np.linspace(y_min - pad_y, y_max + pad_y, grid_size)
    heatmap = np.zeros((len(y_vals), len(x_vals)))

    # loop across grid to get densities
    for i, x in enumerate(x_vals):
        for j, y in enumerate(y_vals):
            total_density = 0
            for xi, yi in zip(X, Y):
                d = math.sqrt((x - xi) ** 2 + (y - yi) ** 2)
                total_density += kde_distance_based(d, R)
            heatmap[j, i] = total_density

    # plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(heatmap, extent=(x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]),
               origin="lower", cmap="hot", interpolation="nearest")
    ax.scatter(X, Y, color="blue", label="Data points", edgecolors="black")
    ax.legend()
    ax.set_title(f"Heatmap - Distance-Based (d <= R)")
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.colorbar(ax.images[0], ax=ax, label="Density")
    return fig
