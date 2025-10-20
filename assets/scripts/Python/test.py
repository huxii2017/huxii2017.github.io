from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn import metrics
from math import sqrt
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import os,time,sys
from scipy import stats

#import logomaker

from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

def roc_auc_ci(y_true, y_score):
	AUC = roc_auc_score(y_true, y_score)
	N1 = y_true.count(1)
	N2 = y_true.count(0)
	Q1 = AUC / (2 - AUC)
	Q2 = 2*AUC**2 / (1 + AUC)
	SE_AUC = sqrt((AUC*(1 - AUC) + (N1 - 1)*(Q1 - AUC**2) + (N2 - 1)*(Q2 - AUC**2)) / (N1*N2))
	lower = AUC - 1.96*SE_AUC
	upper = AUC + 1.96*SE_AUC
	if lower < 0:
		lower = 0
	if upper > 1:
		upper = 1
	return (lower, upper),SE_AUC
def call_ROC_value(idata,col,pos): #pos ~ positive label #"factor" ~ label column name
	scores=idata[col] # for ROC curve
	y_true=idata['factor'].tolist()
	fpr,tpr,thresholds=metrics.roc_curve(idata['factor'],scores,pos_label=pos)
	optimal_idx = np.argmax(tpr - fpr)
	optimal_threshold = thresholds[optimal_idx]
	auc=metrics.auc(fpr,tpr)
	ci=roc_auc_ci(y_true, scores)
	return fpr,tpr,auc,ci,thresholds,optimal_threshold
def plot_ROC_spine(fig,ax):
	ax.set_ylabel('Sensitivity (%)',fontsize=22);ax.set_xlabel('Specificity (%)',fontsize=22)
	ax.yaxis.set_tick_params(labelsize=15);ax.xaxis.set_tick_params(labelsize=15)
	ax.tick_params(direction='out', length=8, width=1, colors='k',grid_color='none', grid_alpha=0.5)
	ax.set_xlim([-0.05, 1.05]);ax.set_xticks(np.arange(0,1.1,step=.2));ax.set_xticklabels([f'{(1-x)*100:.0f}' for x in np.arange(0,1.1,step=.2)])
	ax.set_ylim([-0.05, 1.05]);ax.set_yticks(np.arange(0,1.1,step=.2));ax.set_yticklabels([f'{x*100:.0f}' for x in np.arange(0,1.1,step=.2)])
	ax.plot([-0.05, 1.05], [-0.05, 1.05], color='grey', lw=1.2, linestyle='--')
	return fig,ax

np.random.seed(2025)
n = 300

datasets = {
    "Linear_High": pd.DataFrame({
        "Dataset": "Linear_High",
        "true": np.repeat([0, 1], n//2),
        "score": np.concatenate([np.random.normal(0, 1, n//2),
                                 np.random.normal(3, 1, n//2)])
    }),
    "Linear_Mid": pd.DataFrame({
        "Dataset": "Linear_Mid",
        "true": np.repeat([0, 1], n//2),
        "score": np.concatenate([np.random.normal(0, 1, n//2),
                                 np.random.normal(1.5, 1, n//2)])
    }),
    "Linear_Low": pd.DataFrame({
        "Dataset": "Linear_Low",
        "true": np.repeat([0, 1], n//2),
        "score": np.concatenate([np.random.normal(0, 1, n//2),
                                 np.random.normal(0.5, 1, n//2)])
    })
}

demo = pd.concat(datasets.values())

custom_colors = {
    "Linear_High": "#E64B35",
    "Linear_Mid": "#4DD576",
    "Linear_Low": "#1C97CC"
}

def savefig(fig,ax,out):
	plt.savefig(out,bbox_inches = 'tight')
	plt.clf()
	plt.close(fig)

fig,ax=plt.subplots(figsize=(8,8))
#for tag,label,coo in zip(Tag,Label,Cmp):
#	idata=pd.read_csv(f'data/fig2a/{tag}.predicted.data.ROC.PR.tsv',sep='\t')
#	fpr,tpr,auc,ci,_,_=call_ROC_value(idata,col,pos)
#	ax.plot(fpr,tpr,color=coo,lw=2.5,linestyle='-',label=f'{label}: {auc:.2f}')
from sklearn.metrics import roc_curve, roc_auc_score
auc_dict = {}
infer_df=demo
truth_col="true"
score_col="score"
line_width=1
alpha=1
colors=custom_colors
for ds in datasets:
    df_sub = infer_df[infer_df["Dataset"] == ds]
    y_true, y_score = df_sub[truth_col], df_sub[score_col]
    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc_val = roc_auc_score(y_true, y_score)
    auc_dict[ds] = auc_val

    # Select color from dict or default
    color = colors.get(ds, None) if isinstance(colors, dict) else None

    ax.plot(
        fpr, tpr,
        lw=line_width,
        alpha=alpha,
        label=f"{ds} (AUC = {auc_val:.2f})",
        color=color
    )
legend=ax.legend(frameon=False,fontsize=15,title='AUC',title_fontsize=18)
legend._legend_box.align = "right"
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.xaxis.set_minor_locator(AutoMinorLocator())
plot_ROC_spine(fig,ax)
ax.tick_params(direction='out', length=10, width=1, colors='k',grid_color='grey', grid_alpha=1)
ax.tick_params(which='minor', length=5, width=1, color='k')
out=f'test.png'
plt.show()
#savefig(fig,ax,out)