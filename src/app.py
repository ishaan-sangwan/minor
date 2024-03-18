import pathlib

from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import os
cwd = os.getcwd()
fibre = os.path.join(cwd,"Fiber 10")
files = os.listdir(fibre)
# file_path = os.path.join(fibre, files[0])
# import matplotlib.pyplot as plt

PATH = pathlib.Path(__file__).parent
app = Dash(__name__)
server = app.server
def analyisis(file_path):
    file = os.path.join(fibre,file_path)
    df = pd.read_excel(file)
    experiment = df.iloc[2:,:3]
    renaming = df.iloc[:1,:3].T.to_dict()
    experiment.rename(columns=renaming[0])
    consts = df.iloc[:,4:6].dropna().T.to_dict(orient="records")
    const = pd.DataFrame(columns=consts[0].values(), data=[consts[1].values()])
    experiment.rename(columns=renaming[0],inplace=True)
    experiment.rename(columns={"Standard force": 'Force'},inplace=True)


    def slope(x_init, y_init, x_final, y_final):
        if (x_final - x_init != 0):
            return (y_final - y_init)/(x_final - x_init)
        else:
            return float('inf')

    slopes = []
    for i in range(len(experiment.Strain)-1):
        slopes.append(slope(experiment.Strain.iloc[i],experiment.Force.iloc[i],
                            experiment.Strain.iloc[i+1], experiment.Force.iloc[i+1]))


    ratios = []
    for index, sl in enumerate(slopes):
        if index > 4:
            ratio = abs((slopes[index+1] - sl)/sl)
            # print(f"{ratio} ---- {index}/{len(slopes)}")
            if ratio < 0.5 or ratio > 1.5:
                ratios.append(ratio)
            else:
                break
    pt_Strain = experiment.iloc[index]["Strain"]
    pt_Force = experiment.iloc[index]["Force"]
    pt = []

    config = {'displayModeBar': False}
    # fig, ax = plt.subplots()
    # ax.plot([1, 2, 3], [1, 4, 9], "o")
    # ax.plot(experiment.Strain, experiment.Force)
    # ax.xlabel("Strain")
    # ax.ylabel("Force")
    # ax.title("Strain vs Force")
    # ax.axline((experiment.Strain.iloc[0], experiment.Force.iloc[0]),(pt_Strain, pt_Force), color="red")
    # plt.show()
    x = [experiment.Force.iloc[0], pt_Force]
    y = [experiment.Strain.iloc[0], pt_Strain]
    fig = go.Figure(data=[go.Scatter(x=experiment.Force, y=experiment.Strain)])
    fig.add_trace(go.Line(x=x, y=y, name='first point'))
    sec_y = [experiment.Strain.iloc[0],experiment.Strain.max()]
    sec_x = [experiment.Force.iloc[0], experiment[experiment["Strain"] == experiment.Strain.max()].Force.iloc[0]]
    print(sec_x)
    fig.add_trace(go.Line(x=sec_x, y=sec_y, name='third point'))
    return fig


app.layout = html.Div([
    dcc.Dropdown(os.listdir(cwd),id='fibre',),
    dcc.Dropdown(files,files[0],id="file"),
    dcc.Graph(id="graph")
])

@app.callback(
    [Output("graph", "figure"), Output("file",'options')],
    [Input("file","value"), Input("fibre", 'value')],
    # [State("fibre", 'value')]
)
def update(file,fibre_choice):
    global fibre
    global files
    fig = analyisis(file)
    fig.update_layout(width=1500, height=700)
    fibre = os.path.join(cwd,fibre_choice)
    print(fibre_choice)
    files = os.listdir(fibre)
    return (fig, files)
app.run_server(debug=True,port=8000)


