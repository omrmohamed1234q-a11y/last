import matplotlib.pyplot as plt


def make_3d_plot(df, x, y, z, elev, azim):
    plot_df = df.dropna(subset=[x, y, z])
    if len(plot_df) == 0:
        return None

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(plot_df[x], plot_df[y], plot_df[z], c=plot_df[z], cmap='viridis', s=60, alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_zlabel(z)
    ax.set_title(f"{x} vs {y} vs {z}")
    ax.view_init(elev=elev, azim=azim)
    return fig
