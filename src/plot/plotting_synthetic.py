import pandas as pd
import ast
from statistics import mean
import matplotlib.pyplot as plt
import math
from short_names import algorithm_short_names, remove_alg_prefix

def read_log(filename):
    df = pd.read_csv(filename)
    df['graph_generator'] = df['graph_generator'].apply(lambda stringdict: ast.literal_eval(stringdict))
    df['f_score'] = df['f_score'].apply(lambda array: mean(ast.literal_eval(array)))
    df['number_of_clusters'] = df['number_of_clusters'].apply(lambda array: mean(ast.literal_eval(array)))
    df['graph_generator_name'] = df['graph_generator'].apply(lambda att_dict: att_dict.get('name', None))
    attributes = set()
    for row in df['graph_generator']:
        attributes.update(row['arguments'].keys())
    for attribute in attributes:
        df[f'graph_generator_arg_{attribute}'] = df['graph_generator'].apply(lambda att_dict: att_dict['arguments'].get(attribute, None))
    return df

def plot_synthetic(df):
    plot_axis = [('graph_generator_arg_p', None),('graph_generator_arg_k', None),('graph_generator_arg_f', None)]
    
    fig = plt.figure(figsize=(20, 8), constrained_layout=False)
    gs = fig.add_gridspec(2, 3)
    axs = [fig.add_subplot(gs[i//3, i%3]) for i in range(6)]
    for ax in axs:
        ax.set_prop_cycle(color = ['#000000','#d55e00','#56b4e9','#0072b2','#E69F00','#cc79a7','#009e73','#f0e442'],
            marker = ['+', '+','x', '+','+', '+','+', '+'],
            linestyle = ['solid', 'solid','dotted', 'dotted','dotted', 'dotted','dashed', 'dashed']
            )
    for i,yaxis in enumerate(['mean_error', 'f_score']):
        for j, plot_params in enumerate(plot_axis):
            xaxis, ylim = plot_params 
            if yaxis == 'f_score': 
                ylim = (0.0, 1.05)
            plot_performance_graph(axs[i*3+j],df, xaxis, yaxis, ylim,[], i == 1, j==0)
    s = fig.subplotpars
    bb = [s.left, s.top+0.07, s.right-s.left, 0.05]

    handles,labels = axs[0].get_legend_handles_labels()
    print(handles)
    legend_order = [2, 3, 4, 5, 6, 7, 0, 1]
    handles = [handles[i] for i in legend_order]
    labels = [labels[i] for i in legend_order]
    
    s = fig.subplotpars
    bb = [s.left, s.top, s.right-s.left, 0.1]
    ax.legend(handles, labels, ncol = 8, fancybox = False, shadow = False, bbox_to_anchor = bb, mode = "expand",  bbox_transform = fig.transFigure)
    fig.subplots_adjust(hspace = 0.12, wspace=0.3)
    plt.savefig(f"synthetic.pdf", bbox_inches='tight')


def sort_precedence(long_name):
    desired = ['GER','GE','Pivot', 'RC','CB','DC','Vote','RMM']
    short_name = algorithm_short_names.get(remove_alg_prefix(long_name), 'zzz')
    if short_name == 'zzz':
        return 42
    return desired.index(short_name)

def plot_performance_graph(axs, df,xaxis, yaxis, ylim = None, ignored_algorithms = [], named_xaxis = True,named_yaxis = True):    
    defaults = {'graph_generator_arg_k':100, 'graph_generator_arg_f':20,'graph_generator_arg_p':0.1, 'graph_generator_arg_n':1000}
    data_selector = df[xaxis].apply(lambda x: True)
    for argument, default_value in defaults.items():
        if argument == xaxis: continue
        data_selector = data_selector & (df[argument] == default_value)
    data = df[data_selector]
    algorithms = sorted(list(set(data['algorithm'])), key=sort_precedence)

    for alg in algorithms:
        name = remove_alg_prefix(alg)
        if (name not in algorithm_short_names) or (algorithm_short_names[name] in ignored_algorithms):
            continue
        alg_df = data[data['algorithm'] == alg].sort_values(xaxis)
        axs.plot(alg_df[xaxis], alg_df[yaxis], marker = 'o', label = algorithm_short_names[name])
    axs.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axis_names = {'f_score':'F-Score', 'mean_error': 'Mean Error', 'graph_generator_arg_p': 'p', 'graph_generator_arg_k': 'k', 'graph_generator_arg_f': '|L|'}
    if named_xaxis:
        axs.set_xlabel(axis_names[xaxis])
    if named_yaxis:
        axs.set_ylabel(axis_names[yaxis])
    if ylim:
        axs.set_ylim(ylim[0], ylim[1])


df = read_log("./measurements/synthetic_log.csv")
plt.rcParams.update({
    'font.size': 16,
    'lines.markersize': 4,
   })

plot_synthetic(df)