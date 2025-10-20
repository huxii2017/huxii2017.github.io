# ================================================================
# File: roc_utils.R
# Author: Xi HU
# Description:
#   Utility functions for ROC analysis:
#   (1) Compute ROC AUC and 95% Confidence Interval.
#   (2) Plot ROC curves for multiple datasets in one panel.
#   (3) Plot multiple ROC curves in a single panel (with AUC legend).
# Dependencies: pROC, ggplot2, dplyr, tidyr, scales
# ================================================================

library(pROC)
library(ggplot2)
library(dplyr)
library(scales)

# ================================================================
# Function: roc_auc_ci
# Purpose : Compute ROC AUC and its 95% Confidence Interval
# ================================================================
roc_auc_ci <- function(y_true=NULL, y_score=NULL, help=FALSE) {
	if (help) {
		cat("
	Compute ROC AUC and its 95% Confidence Interval
	------------------------------------------------
	
	Description:
        Calculates the area under the ROC curve (AUC) and its 95% confidence interval
        using the `pROC` package.
	
	Arguments:
        y_true  : Numeric vector of true binary labels (0 or 1).
        y_score : Numeric vector of predicted scores or probabilities.
        help    : Logical flag. If TRUE, prints this help text and exits.
	
	Returns:
        A list containing:
        $AUC : numeric, area under the ROC curve.
        $CI  : numeric vector (lower, mean, upper) for the 95% CI.
	
	Example:
        result <- roc_auc_ci(c(0,1,1,0), c(0.2,0.8,0.7,0.3))
        result$AUC
        result$CI
	
	------------------------------------------------
	")
	return(invisible(NULL))
	}
	
	library(pROC)
	
	roc_obj <- roc(y_true, y_score, quiet = TRUE)
	auc_val <- auc(roc_obj)
	ci_val <- ci.auc(roc_obj)
	return(list(AUC = auc_val, CI = ci_val))
}

# ================================================================
# Function: plot_roc_panels
# Purpose : Plot ROC Curves for Multiple Datasets
# ================================================================
plot_roc_panels <- function(
	infer_df,
	datasets = c("Cohort 01", "Cohort 02"),
	truth_col = "true",
	score_col = "score",
	colors = c("#F8766D"),
	line_width = 1.2,
	line_alpha = 0.9,
	title_main = "ROC Curve Analysis",
	x_label = "Specificity",
	y_label = "Sensitivity",
	show_auc_label = TRUE,
	auc_pos = c(0.35, 0.18),
	auc_digits = 3,
	ncol = 2,
	base_font = 16,
	help=FALSE
) {
	if (help) {
	cat("
		Plot ROC Curves for Multiple Datasets
		------------------------------------------------
		
		Description:
            Generates faceted ROC plots for one or more datasets using ggplot2.
            It computes ROC curves, AUC, and 95% CI for each dataset, and can
            annotate AUC values directly on the plot.
        
        Arguments:
            infer_df       : Data frame containing true labels, scores, and dataset IDs.
            datasets       : Character vector specifying which dataset names to plot.
            truth_col      : Column name for true binary labels (0/1).
            score_col      : Column name for predicted scores or probabilities.
            colors         : Vector of colors for ROC curves.
            line_width     : Numeric, width of the ROC curve line.
            line_alpha     : Numeric between 0–1, transparency level.
            title_main     : Main title of the plot.
            x_label        : Label for x-axis (default = 'Specificity').
            y_label        : Label for y-axis (default = 'Sensitivity').
            show_auc_label : Logical, whether to display AUC text on plot.
            auc_pos        : Numeric vector (x, y) for AUC label position.
            auc_digits     : Integer, number of decimals for AUC and CI.
            ncol           : Number of facet columns.
            base_font      : Base font size for ggplot theme.
            help           : Logical flag. If TRUE, prints this help text and exits.
		
		Returns:
            A ggplot object showing ROC curves (one facet per dataset).
		
		Example:
            data(pROC::aSAH)
            demo <- aSAH %>%
            dplyr::mutate(true = ifelse(outcome == 'Poor', 1, 0)) %>%
            dplyr::select(true, s100b, ndka)
		
            demo_long <- demo %>%
            tidyr::pivot_longer(cols = c(s100b, ndka),
                                names_to = 'Dataset',
                                values_to = 'score')
		
        demo_long$Dataset <- factor(demo_long$Dataset, levels = c('s100b', 'ndka'))
		
        p <- plot_roc_panels(
                infer_df   = demo_long,
                datasets   = c('s100b','ndka'),
                truth_col  = 'true',
                score_col  = 'score',
                title_main = 'ROC Curve Demo (aSAH)',
                base_font  = 15
            )
        print(p)
		------------------------------------------------
		")
	return(invisible(NULL))
	}
	
	library(ggplot2)
	library(dplyr)
	library(pROC)
	
	roc_list <- lapply(datasets, function(ds) {
	idf <- infer_df %>% filter(.data$Dataset == ds)
	roc_obj <- pROC::roc(
		response = idf[[truth_col]],
		predictor = idf[[score_col]],
		quiet = TRUE
	)
	data.frame(
        Dataset = ds,
        Specificity = as.numeric(roc_obj$specificities),
        Sensitivity = as.numeric(roc_obj$sensitivities),
        AUC = as.numeric(pROC::auc(roc_obj)),
        CI_low = as.numeric(pROC::ci.auc(roc_obj))[1],
        CI_high = as.numeric(pROC::ci.auc(roc_obj))[3]
	)
	})
	
	roc_df <- do.call(rbind, roc_list)
	
	ann_df <- roc_df %>%
	group_by(Dataset) %>%
	summarise(AUC = first(AUC), CI_low = first(CI_low),
			CI_high = first(CI_high), .groups = "drop") %>%
	mutate(
	x = auc_pos[1],
	y = auc_pos[2],
	label = sprintf("AUC = %.3f\n95%% CI: [%.3f, %.3f]",
                    round(AUC, auc_digits),
                    round(CI_low, auc_digits),
                    round(CI_high, auc_digits))
	)
	
	p <- ggplot(roc_df, aes(x = Specificity, y = Sensitivity)) +
	geom_path(
        color = colors[1],
        linewidth = line_width,
        alpha = line_alpha,
        lineend = "round"
	) +
	annotate("segment",
                x = 1, y = 0, xend = 0, yend = 1,
                linetype = "dashed", color = "grey70") +
	scale_x_reverse(limits = c(1, 0), breaks = seq(1, 0, by = -0.2)) +
	scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.2)) +
	coord_fixed(ratio = 1) +
	facet_wrap(~ Dataset, ncol = ncol, scales = "fixed") +
	labs(title = title_main, x = x_label, y = y_label) +
	theme_bw(base_size = base_font) +
	theme(
        plot.title = element_text(hjust = 0.5, face = "bold", size = base_font + 2),
        panel.grid = element_blank(),
        axis.title = element_text(size = base_font),
        axis.text = element_text(size = base_font - 2),
        strip.background = element_rect(fill = "grey85", color = NA),
        strip.text = element_text(size = base_font - 2)
	)
	
	if (show_auc_label) {
	p <- p + geom_text(
        data = ann_df,
        aes(x = x, y = y, label = label),
        inherit.aes = FALSE,
        size = base_font / 3.5
	)
	}
	
	return(p)
}

# ================================================================
# Function: plot_roc_overlay
# Purpose : Plot multiple ROC curves in a single panel (with AUC legend)
# ================================================================
plot_roc_overlay <- function(
	infer_df = NULL,
	datasets = NULL,
	truth_col = "true",
	score_col = "score",
	colors = NULL,
	line_width = 1.2,
	line_alpha = 0.9,
	title_main = "ROC Curve Comparison",
	x_label = "Specificity",
	y_label = "Sensitivity",
	base_font = 16,
	legend_position='right',
	help = FALSE
	) {
	if (help) {
	cat("
		Plot Multiple ROC Curves in One Panel
		------------------------------------------------
		
		Description:
            Plots ROC curves from multiple datasets (or groups) together
            in a single panel using ggplot2. Each curve is labeled in the
            legend as 'Dataset (AUC = 0.xx)'.
        
        Arguments:
            infer_df    : Data frame containing true labels, scores, and dataset IDs.
            datasets    : Character vector specifying dataset names to include.
                        If NULL, all unique values of 'Dataset' column are used.
            truth_col   : Column name for true binary labels (0/1).
            score_col   : Column name for predicted scores or probabilities.
            colors      : Vector of colors for each dataset. If NULL, ggplot default palette used.
            line_width  : Numeric, width of ROC lines.
            line_alpha  : Numeric between 0–1, transparency of ROC lines.
            title_main  : Main title of the plot.
            x_label, y_label : Axis labels.
            base_font   : Base font size for ggplot theme.
            help        : Logical flag. If TRUE, prints this help text and exits.
		
		Returns:
            A ggplot object showing all ROC curves overlaid in one figure.
        
        Example:
            data(pROC::aSAH)
            demo <- aSAH %>%
            dplyr::mutate(true = ifelse(outcome == 'Poor', 1, 0)) %>%
            dplyr::select(true, s100b, ndka)
        
            demo_long <- demo %>%
            tidyr::pivot_longer(
                cols = c(s100b, ndka),
                names_to = 'Dataset',
                values_to = 'score'
            )
        
            plot_roc_overlay(
            infer_df   = demo_long,
            datasets   = c('s100b', 'ndka'),
            truth_col  = 'true',
            score_col  = 'score',
            title_main = 'ROC Comparison: s100b vs ndka'
            )
		------------------------------------------------
		")
	return(invisible(NULL))
	}

	library(pROC)
	library(ggplot2)
	library(dplyr)
	library(scales)

	# Automatically detect datasets if not specified
	if (is.null(datasets)) {
	datasets <- unique(infer_df$Dataset)
	}
	
	# Compute ROC for each dataset
	roc_list <- lapply(datasets, function(ds) {
	idf <- infer_df %>% dplyr::filter(.data$Dataset == ds)
	roc_obj <- pROC::roc(idf[[truth_col]], idf[[score_col]], quiet = TRUE)
	data.frame(
        Dataset = ds,
        Specificity = as.numeric(roc_obj$specificities),
        Sensitivity = as.numeric(roc_obj$sensitivities),
        AUC = as.numeric(pROC::auc(roc_obj))
	)
	})
	
	# Combine results
    roc_df <- do.call(rbind, roc_list) %>%
        dplyr::mutate(label = sprintf("%s (AUC = %.2f)", Dataset, AUC)) %>%
        dplyr::mutate(label = factor(label, 
                                levels = unique(label[order(-AUC)])))
	
	# Color palette
	if (is.null(colors)) {
	colors <- scales::hue_pal()(length(datasets))
	}
	
	# Plot all ROC curves together
	p <- ggplot(roc_df, aes(x = Specificity, y = Sensitivity, color = label)) +
	geom_path(linewidth = line_width, alpha = line_alpha, lineend = "round") +
	annotate("segment", x = 1, y = 0, xend = 0, yend = 1,
                linetype = "dashed", color = "grey60") +
	scale_x_reverse(limits = c(1, 0), breaks = seq(1, 0, by = -0.2)) +
	scale_y_continuous(limits = c(0, 1), breaks = seq(0, 1, by = 0.2)) +
	coord_fixed(ratio = 1) +
	labs(
        title = title_main,
        x = x_label,
        y = y_label,
        color = "Groups"
	) +
	theme_bw(base_size = base_font) +
	theme(
		plot.title = element_text(hjust = 0.5, face = "bold", size = base_font + 2),
		panel.grid = element_blank(),
		axis.title = element_text(size = base_font),
		axis.text = element_text(size = base_font - 2),
		legend.title = element_text(size = base_font - 1, face = "bold"),
		legend.text = element_text(size = base_font - 2),
		legend.position=legend_position,
	)
	
	return(p)
}
