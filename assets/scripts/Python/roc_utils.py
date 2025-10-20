# ================================================================
# File: roc_utils.py
# Author: Xi Hu
# Description:
#   Utility functions for ROC analysis and visualization:
#   (1) Compute ROC AUC and 95% Confidence Interval (bootstrapped)
#   (2) Plot ROC curves for multiple datasets (faceted)
#   (3) Plot multiple ROC curves in one overlay panel
# Dependencies: numpy, pandas, matplotlib, scikit-learn
# ================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, FixedLocator
from sklearn.metrics import roc_curve, roc_auc_score


# ================================================================
# Function: roc_auc_ci
# Purpose : Compute ROC AUC and its 95% Confidence Interval
# ================================================================
def roc_auc_ci(y_true=None, y_score=None, help=False, n_bootstrap=2000, random_state=42):
    """
    Compute the ROC AUC value and its 95% confidence interval using bootstrapping.

    Args:
        y_true (array-like): True binary labels (0 or 1).
        y_score (array-like): Predicted continuous scores or probabilities.
        help (bool): If True, print this docstring and return None.
        n_bootstrap (int): Number of bootstrap resamples for CI estimation.
        random_state (int): Random seed for reproducibility.

    Returns:
        dict: {
            "AUC": float,           # Calculated AUC value
            "CI": (lower, mean, upper)
        }

    Example:
        >>> result = roc_auc_ci([0, 1, 1, 0], [0.2, 0.8, 0.7, 0.3])
        >>> print(result["AUC"], result["CI"])
    """
    if help:
        print(roc_auc_ci.__doc__)
        return None

    y_true = np.array(y_true)
    y_score = np.array(y_score)
    auc_val = roc_auc_score(y_true, y_score)

    rng = np.random.RandomState(random_state)
    boot_scores = []

    for _ in range(n_bootstrap):
        indices = rng.randint(0, len(y_score), len(y_score))
        if len(np.unique(y_true[indices])) < 2:
            continue
        boot_auc = roc_auc_score(y_true[indices], y_score[indices])
        boot_scores.append(boot_auc)

    sorted_scores = np.sort(boot_scores)
    ci_lower = np.percentile(sorted_scores, 2.5)
    ci_upper = np.percentile(sorted_scores, 97.5)

    return {"AUC": auc_val, "CI": (ci_lower, auc_val, ci_upper)}


# ================================================================
# Function: plot_ROC_spine
# Purpose : Apply consistent axis/tick/label style for ROC plots
# ================================================================
def plot_ROC_spine(ax, base_font=22, major_len=8, minor_len=5, minor_step=0.05, fixedlocator=True):
    """
    Apply a consistent, publication-style format for ROC plots.

    Features:
        - Label axes with "Sensitivity (%)" and "Specificity (%)"
        - Show ticks from 100→0 (x-axis) and 0→100 (y-axis)
        - Draw outward major/minor ticks
        - Add diagonal reference line

    Args:
        ax (matplotlib.axes): Target axes object.
        base_font (int): Base font size for labels/ticks.
        major_len (int): Major tick length in points.
        minor_len (int): Minor tick length in points.
        minor_step (float): Step for minor ticks if fixed locator is used.
        fixedlocator (bool): If True, use fixed 0–1 minor ticks.
    """
    # Axis labels
    ax.set_ylabel('Sensitivity (%)', fontsize=base_font)
    ax.set_xlabel('Specificity (%)', fontsize=base_font)

    # Major tick labels
    ax.yaxis.set_tick_params(labelsize=base_font-7)
    ax.xaxis.set_tick_params(labelsize=base_font-7)

    # Major ticks: outward style
    ax.tick_params(direction='out', length=major_len, width=1,
                    colors='k', grid_color='none', grid_alpha=0.5)

    # Define major tick positions
    major = np.arange(0, 1.1, 0.2)
    ax.set_xlim([-0.05, 1.05])
    ax.set_ylim([-0.05, 1.05])
    ax.set_xticks(major)
    ax.set_xticklabels([f'{(1-x)*100:.0f}' for x in major])  # 100→0
    ax.set_yticks(major)
    ax.set_yticklabels([f'{y*100:.0f}' for y in major])      # 0→100

    # Optional: fixed minor ticks within [0, 1]
    if fixedlocator:
        minor_ticks = np.arange(0.0, 1.0 + 1e-9, minor_step)
        ax.xaxis.set_minor_locator(FixedLocator(minor_ticks))
        ax.yaxis.set_minor_locator(FixedLocator(minor_ticks))
        ax.tick_params(which='minor', direction='out', length=minor_len, width=1, colors='k')

    # Add diagonal reference line
    ax.plot([-0.05, 1.05], [-0.05, 1.05], color='grey', lw=1.2, linestyle='--')
    return ax


# ================================================================
# Function: plot_roc_overlay_pub
# Purpose : Overlay multiple ROC curves in one figure
# ================================================================
def plot_roc_overlay_pub(
    infer_df,
    datasets,
    truth_col="true",
    score_col="score",
    colors=None,
    title_main="ROC Curve Comparison",
    base_font=22,
    title_font=None,
    line_width=2.5,
    alpha=1.0,
    figsize=(8,8),
    legend_title="AUC",
    legend_font_delta=-7,
    legend_loc=(0.78, 0.20),
    fixedlocator=True,
):
    """
    Plot multiple ROC curves in one overlay figure with consistent styling.

    Args:
        infer_df (pd.DataFrame): Data containing 'Dataset', true, and score columns.
        datasets (list): Names of datasets to include in the overlay.
        truth_col (str): Column name for true labels.
        score_col (str): Column name for predicted scores.
        colors (dict or None): Optional mapping {dataset: color}.
        title_main (str): Main title for the plot.
        base_font (int): Base font size for axes/labels.
        line_width (float): ROC line width.
        alpha (float): Line transparency.
        figsize (tuple): Figure size (width, height).
        legend_title (str): Title for legend block.
        legend_font_delta (int): Relative font size for legend text.
        legend_loc (tuple): Legend position anchor (x, y) in axis coordinates.
        fixedlocator (bool): If True, use fixed minor ticks between 0–1.

    Returns:
        (fig, ax): Matplotlib figure and axis objects.
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Plot each dataset
    for ds in datasets:
        sub = infer_df[infer_df["Dataset"] == ds]
        y_true = sub[truth_col].to_numpy()
        y_score = sub[score_col].to_numpy()
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc_val = roc_auc_score(y_true, y_score)

        color = colors.get(ds, None) if isinstance(colors, dict) else None
        ax.plot(
            fpr, tpr,
            color=color, lw=line_width, alpha=alpha,
            label=f'{ds} (AUC = {auc_val:.2f})'
        )

    # Legend block
    leg = ax.legend(
        frameon=False,
        fontsize=max(6, base_font + legend_font_delta),
        title=legend_title,
        title_fontsize=max(6, base_font + legend_font_delta + 3),
        loc='center',
        bbox_to_anchor=legend_loc
    )
    try:
        leg._legend_box.align = "right"
    except Exception:
        pass

    # Apply unified ROC axis style
    if not fixedlocator:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    plot_ROC_spine(ax, base_font=base_font, fixedlocator=fixedlocator)

    # Reinforce tick visuals
    ax.tick_params(direction='out', length=10, width=1, colors='k', grid_color='grey', grid_alpha=1)
    ax.tick_params(which='minor', length=5, width=1, color='k')

    ax.set_title(title_main, fontsize=title_font or base_font, weight='bold', pad=8)
    fig.canvas.draw_idle()
    return fig, ax


# ================================================================
# Function: plot_roc_panels_pub
# Purpose : Plot multiple ROC curves in separate subplots (faceted layout)
# ================================================================
def plot_roc_panels_pub(
    infer_df,
    datasets=None,
    truth_col="true",
    score_col="score",
    colors=None,
    title_main="ROC Curve Panels",
    base_font=20,
    title_font=None,
    line_width=2.0,
    alpha=1.0,
    ncol=3,
    panel_size=(5, 5),
    legend_title="AUC",
    legend_font_delta=-6,
    fixedlocator=True,
):
    """
    Plot multiple ROC curves in a faceted (multi-panel) layout.

    Each dataset is plotted in its own subplot with consistent
    styling (axes, ticks, legend placement, etc.), suitable for
    figure panels in publications.

    Args:
        infer_df (pd.DataFrame): Data containing [Dataset, truth, score].
        datasets (list or None): Dataset names to plot (default: all).
        truth_col (str): Column name for true labels.
        score_col (str): Column name for predicted scores.
        colors (dict): Optional {dataset: color} mapping.
        title_main (str): Global figure title.
        base_font (int): Font size for labels and titles.
        line_width (float): Width of ROC line.
        alpha (float): Transparency for ROC line.
        ncol (int): Number of subplot columns.
        panel_size (tuple): Each subplot size in inches (width, height).
        legend_title (str): Title for the legend.
        legend_font_delta (int): Relative font size adjustment for legend.
        fixedlocator (bool): Use fixed 0–1 minor tick range.

    Returns:
        (fig, axes): Matplotlib figure and axes array.
    """
    if datasets is None:
        datasets = infer_df["Dataset"].unique().tolist()

    n_datasets = len(datasets)
    nrow = int(np.ceil(n_datasets / ncol))

    fig, axes = plt.subplots(
        nrow, ncol,
        figsize=(panel_size[0] * ncol, panel_size[1] * nrow),
        squeeze=False
    )

    for idx, ds in enumerate(datasets):
        r, c = divmod(idx, ncol)
        ax = axes[r, c]

        sub = infer_df[infer_df["Dataset"] == ds]
        y_true = sub[truth_col].to_numpy()
        y_score = sub[score_col].to_numpy()
        fpr, tpr, _ = roc_curve(y_true, y_score)
        auc_val = roc_auc_score(y_true, y_score)

        color = colors.get(ds, None) if isinstance(colors, dict) else None
        ax.plot(
            fpr, tpr,
            color=color,
            lw=line_width,
            alpha=alpha,
            label=f"AUC = {auc_val:.2f}"
        )

        # Local legend
        leg = ax.legend(
            frameon=False,
            fontsize=max(6, base_font + legend_font_delta),
            title=legend_title,
            title_fontsize=max(6, base_font + legend_font_delta + 2),
            loc='lower right'
        )
        try:
            leg._legend_box.align = "right"
        except Exception:
            pass

        # Apply consistent ROC styling
        plot_ROC_spine(ax, base_font=base_font, fixedlocator=fixedlocator)

        # Reinforce tick visuals
        ax.tick_params(direction='out', length=10, width=1, colors='k', grid_color='grey', grid_alpha=1)
        ax.tick_params(which='minor', length=5, width=1, color='k')

        ax.set_title(ds, fontsize=title_font or base_font, weight='bold', pad=5)

    # Remove empty subplots if any
    total_axes = nrow * ncol
    for j in range(n_datasets, total_axes):
        fig.delaxes(axes.flatten()[j])

    # Global layout & title
    fig.suptitle(title_main, fontsize=title_font or base_font + 4, weight='bold', y=0.98)
    fig.tight_layout(rect=[0.05, 0.05, .95, 0.95])
    fig.canvas.draw_idle()
    return fig, axes


# ================================================================
# Example Section (Demo)
# ================================================================
if __name__ == "__main__":
    np.random.seed(2025)
    n = 300

    # --- Generate demo datasets with varying separability ---
    datasets = {
        "Linear_High": pd.DataFrame({
            "Dataset": "Linear_High",
            "true": np.repeat([0, 1], n // 2),
            "score": np.concatenate([
                np.random.normal(0, 1, n // 2),
                np.random.normal(3, 1, n // 2)
            ])
        }),
        "Linear_Mid": pd.DataFrame({
            "Dataset": "Linear_Mid",
            "true": np.repeat([0, 1], n // 2),
            "score": np.concatenate([
                np.random.normal(0, 1, n // 2),
                np.random.normal(1.5, 1, n // 2)
            ])
        }),
        "Linear_Low": pd.DataFrame({
            "Dataset": "Linear_Low",
            "true": np.repeat([0, 1], n // 2),
            "score": np.concatenate([
                np.random.normal(0, 1, n // 2),
                np.random.normal(0.5, 1, n // 2)
            ])
        })
    }

    demo = pd.concat(datasets.values(), ignore_index=True)

    custom_colors = {
        "Linear_High": "#E64B35",
        "Linear_Mid": "#4DD576",
        "Linear_Low": "#1C97CC"
    }

    # --- Overlay ROC curves (single panel) ---
    fig, ax = plot_roc_overlay_pub(
        infer_df=demo,
        datasets=["Linear_High", "Linear_Mid", "Linear_Low"],
        colors=custom_colors,
        title_main="ROC Curve Demo (High / Mid / Low Separability)",
        base_font=22,
        line_width=2.0,
        figsize=(8, 8),
        legend_loc=(0.7, 0.20)
    )
    plt.show()

    # --- Faceted ROC panels (multi-panel layout) ---
    fig_panels, axes = plot_roc_panels_pub(
        infer_df=demo,
        datasets=["Linear_High", "Linear_Mid", "Linear_Low"],
        colors=custom_colors,
        title_main="ROC Curve Panels (High / Mid / Low)",
        base_font=18,
        ncol=2,
        panel_size=(5, 5)
    )
    plt.show()
    