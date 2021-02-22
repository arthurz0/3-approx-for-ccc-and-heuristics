import pandas as pd
from scipy.stats import mannwhitneyu
from random import random
import ast
from short_names import algorithm_short_names, dataset_short_names
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import math


def read_log(filename, dataset_name):
    df = pd.read_csv(filename)
    df['approx_errors'] = df['approx_errors'].apply(lambda array: ast.literal_eval(array))
    errors = {}
    for _, row in df.loc[df['dataset'] == dataset_name].iterrows():
        alg = row['algorithm']
        if alg not in algorithm_short_names: continue
        alg_name = algorithm_short_names[alg]
        if alg_name in errors:
            raise Exception(f'Watch out! Multiple entries with name {alg} on {dataset_name}')
        errors[alg_name] = row['approx_errors']
    return errors

def plot_distribution(filename, dataset_name, ax, pdf):
    algorithms = ['Vote', 'RMM', 'GER', 'GE']
    errors = read_log(filename, dataset_name)
    height = 1/len(algorithms)
    for i, alg in enumerate(algorithms):
        vals = errors[alg]
        ax.scatter(vals, [1 - i*height - random()*0.8*height for _ in vals], marker='x', label=alg)
        u_test = mannwhitneyu(errors[alg], errors['GE'],alternative='greater')
        print(f'{dataset_name}:\t{alg}, \tvs GE: {u_test.pvalue}')
    ax.set_title(f'{dataset_short_names[dataset_name]}')
    ax.set_ylim(0,1)
    ax.ticklabel_format(axis='x', style='sci', scilimits=(0,0))
    ax.set_yticks([])
    #plt.show()

plt.rcParams.update({
    'font.size': 12,
    })

filename = './main_logs/real_world_log.csv'
datasets = ['facebook', 'dawn', 'microsoft_academic', 'elgrabli_string_min_degree_10', 'twitter', 'cooking', 'elgrabli_dblp_min_degree_10', 'dblp', 'string']
datasets_multi = [name + '_multilabel' for name in ['facebook', 'dawn', 'microsoft_academic', '', 'twitter', 'cooking', '', 'dblp', 'string']]

to_plot = datasets
#to_plot = datasets_multi
pdf = PdfPages('./distribution_single.pdf')
fig = plt.figure(figsize=(20, 4), constrained_layout=False)
gs = fig.add_gridspec(math.ceil(len(to_plot)/3), 3)
for i, dataset_name in enumerate(to_plot):
    if dataset_name == '_multilabel': continue
    ax = fig.add_subplot(gs[i//3, i%3])
    ax.set_prop_cycle(color = ['#009e73','#f0e442','#000000','#d55e00'],
            )
    plot_distribution(filename, dataset_name, ax, pdf)
s = fig.subplotpars
bb = [s.left, s.top, s.right-s.left, 0.17]
handles,labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, ncol = 8, fancybox = False, shadow = False, bbox_to_anchor = bb, mode = "expand",  bbox_transform = fig.transFigure)
fig.subplots_adjust(hspace = 0.9, wspace=0.1)
pdf.savefig(fig, bbox_inches='tight')
pdf.close()