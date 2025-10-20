# ================================================================
# File: combine_by_group.R
# Author: Xi HU
# Description:
#   A universal patchwork wrapper to loop over groups/datasets
#   and call a specified plotting function for each subset.
# Dependencies: dplyr, patchwork
# ================================================================

library(dplyr)
library(patchwork)

combine_by_group <- function(
	data,
	group_col = "Dataset",
	group_list = NULL,
	plot_func,         # e.g., plot_roc_panels
	plot_args = list(),# additional arguments passed to plot_func
	ncol = 2,
	title_main = "Combined Plots",
	help=FALSE
) {
if (help) {
	cat("
	Combine and Generate Grouped Subplots
	------------------------------------------------
	
	Description:
	Automatically loops over unique groups in a dataset, calls a specified
	plotting function (e.g., plot_roc_panels) for each group, and combines
	all subplots into a single patchwork layout.
	
	Arguments:
	data        : Data frame containing the full dataset.
	group_col   : Column name (string) specifying the grouping variable.
	group_list  : Optional character vector of groups to include.
				If NULL, all unique values in group_col will be used.
	plot_func   : Plotting function to call for each group (e.g., plot_roc_panels).
	plot_args   : Named list of additional arguments to pass to plot_func.
	ncol        : Number of columns in the combined patchwork layout.
	title_main  : Main title for the combined figure.
	help        : Logical flag. If TRUE, prints this help text and exits.
	
	Returns:
	A patchwork ggplot object combining all generated subplots.
	
	Example:
	p_final <- combine_by_group(
				data       = demo_long,
				group_col  = 'Dataset',
				group_list = c('s100b', 'ndka'),
				plot_func  = plot_roc_panels,
				plot_args  = list(
                    truth_col = 'true',
                    score_col = 'score',
                    base_font = 15
				),
				ncol       = 2,
				title_main = 'ROC Curve Demo (aSAH)'
				)
	print(p_final)
	------------------------------------------------
	")
	return(invisible(NULL))
	}
	
	library(dplyr)
	library(patchwork)

	# 1️⃣ Automatically detect groups if not provided
	if (is.null(group_list)) {
	group_list <- unique(data[[group_col]])
	}
	
	# 2️⃣ Loop over each group and call plot_func()
	plist <- list()
	for (g in group_list) {
	message("Plotting group: ", g)
	sub <- data %>% filter(.data[[group_col]] == g)
	
	# Merge base args with per-group info
	args <- c(list(infer_df = sub, datasets = g, title_main = g), plot_args)
	p <- do.call(plot_func, args)
	plist[[g]] <- p
	}
	
	# 3️⃣ Combine all plots with patchwork
	p_final <- wrap_plots(plist, ncol = ncol) +
	plot_annotation(
		title = title_main,
		theme = theme(
			plot.title = element_text(hjust = 0.5, face = "bold", size = 16)
		)
	)
	
	return(p_final)
}