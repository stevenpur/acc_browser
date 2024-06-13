from flask import Flask, render_template, session, request
import numpy as np
from flask_session import Session
import plotly.graph_objs as go
import plotly
import plotly.express as px
import json
import pandas as pd
import utils
import matplotlib.pyplot as plt
from glob import glob
from scipy.ndimage import median_filter

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
Session(app)

file_dir = "/users/doherty/imh310/eating_detect/data/acc_data/"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/getIndvList')
def get_ind_list():
    files = glob(file_dir + '*.pkl')
    indvs = [f.split('/')[-1].split('_')[0] for f in files]
    return json.dumps(indvs)


@app.route('/load')
def load_data(file, time_window = 30, label_column = 'label'):
    print('load data..')
    # %% read arguments
    data = pd.DataFrame()
    if file.endswith('.pkl'):
        data = pd.read_pickle(file)# check file type
    elif file.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.endswith('.txt') or file.endswith('.tsv'):
        data = pd.read_csv(file, sep='\t')
    if label_column not in data.columns:
        raise ValueError(f'{label_column} not in the data columns')
    X_unsort, Y_unsort, T_unsort = utils.make_windows(data, winsec=time_window, y_column=label_column)
    sort_indices = np.argsort(T_unsort)
    X = X_unsort[sort_indices]
    Y = Y_unsort[sort_indices]
    T = T_unsort[sort_indices]
    
    labels = data[label_column].unique()
    gp = {label: {} for label in labels}
    for label in labels:
        index = [i for i in range(len(Y)) if Y[i] == label]
        gp[label]['X'] = [X[i] for i in index]
        gp[label]['Y'] = [Y[i] for i in index]
        gp[label]['T'] = [T[i] for i in index]
    session['gp'] = gp
    session['X'] = X
    session['Y'] = Y
    session['T'] = T
    session['labels'] = labels

@app.route('/get24hr')
def get_24hr_data():
    indv = request.args.get('param1')
    files = glob(file_dir + indv + '*.pkl')
    # match the indv with the file name
    matching_files = [f for f in files if indv in f]
    if len(matching_files) == 0:
        print(f'No data found for {indv}')
        return 'No data found for this individual'
    elif len(matching_files) > 1:
        print(f'Multiple files found for {indv}')
        return 'Multiple files found for this individual'
    matching_file = matching_files[0]
    load_data(matching_file)
    T = session['T']
    Y = list(session['Y'])
    df = pd.DataFrame({'T': T, 'Y': Y, 'value': 1, 'id': list(range(len(T)))})
    df = df.sort_values(by='T')
    fig = px.bar(df, x='T', y='value', color='Y', labels = {'Y': 'Activity'}, custom_data = 'id')
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_traces(marker_line_width=0)  # Bar width is very narrow
    fig.update_layout(hovermode='closest')
    fig_json = fig.to_json()
    # T_str = [str(t) for t in T]
    # print(T_str)
    return fig_json 


@app.route('/plotAcc')
def plot_data():
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')
    is_smooth = param2 == 'True'
    print(param1)
    index =  int(request.args.get('param1'))
    Y = session['Y']
    print(Y[index])
    T = session['T']
    print(T[index])
    if 'X' not in session:
        load_data()
    X = session['X']
    x = [ entry[0] for entry in X[index] ]
    y = [ entry[1] for entry in X[index] ]
    z = [ entry[2] for entry in X[index] ]
    inds = [i for i in range(len(x))]
    smooth_x = go.Scatter(x=inds, y=median_filter(x, size=101), mode = 'lines', name = 'x')
    traex = go.Scatter(x=inds, y=x, mode = 'lines', name = 'x')
    smooth_y = go.Scatter(x=inds, y=median_filter(y, size=101), mode = 'lines', name = 'y')
    traey = go.Scatter(x=inds, y=y, mode = 'lines', name = 'y')
    smooth_z = go.Scatter(x=inds, y=median_filter(z, size=101), mode = 'lines', name = 'z')
    traez = go.Scatter(x=inds, y=z, mode = 'lines', name = 'z')
    plotly_data = [traex, traey, traez]
    if is_smooth:
        plotly_data = [smooth_x, smooth_y, smooth_z]
    fig = go.Figure(data=plotly_data)

    # Update layout to set y-axis range
    fig.update_layout(
        yaxis=dict(range=[-2, 2])  # Set the y-axis range from -2 to 2
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #return app.response_class(response=graphJSON, content_type='application/json')
    return graphJSON

    
if __name__ == '__main__':
    print('hello2')
    app.run(debug=True)
