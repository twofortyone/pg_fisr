import numpy as np
import pandas as pd
from plotly.offline import plot, iplot
import plotly.graph_objects as go
from plotly.io import write_html


class Report:

    def __init__(self, url1, url2, data_frame, df2):
        self.plot_url1 = url1
        self.plot_url2 = url2
        self.table = pandas2html(data_frame)
        self.table2 = pandas2html(df2)

    def make_report(self):
        html_string = '''
        <html>
            <head>
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
                <style>body{ margin:0 100; background:white; }</style>
            </head>
            <body>
                <h1>Fault isolation and service restoration's report</h1>
                
                <div class="row">
                    <div class="col-md-6">
                        <h3>Learning plot training</h3>
                        <iframe width="500" height="300" frameborder="0" seamless="seamless" scrolling="no" \
                            src="''' + self.plot_url1 + '''"></iframe>
                        <p>GE had the most predictable stock price in 2014. IBM had the highest mean stock price. \
                            The red lines are kernel density estimations of each stock price - the peak of each red lines \
                            corresponds to its mean stock price for 2014 on the x axis.</p>
                    </div> 
                     <div class="col-md-6">
                        <h3>Learning plot training</h3>
                        <iframe width="500" height="300" frameborder="0" seamless="seamless" scrolling="no" \
                            src="''' + self.plot_url2 + '''"></iframe>
                        <p>GE had the most predictable stock price in 2014. IBM had the highest mean stock price. \
                            The red lines are kernel density estimations of each stock price - the peak of each red lines \
                            corresponds to its mean stock price for 2014 on the x axis.</p>
                    
                    </div> 
                </div>
                
                <h3>Actions taken given a failure</h3>
                ''' + self.table + '''
                
                <h3>Statistics</h3>
                ''' + self.table2 + '''
                
                
            </body>
        </html>'''

        f = open('E:/MININT/SMSOSD/OSDLOGS/github/pg_fisr/code/report/report.html', 'w')
        f.write(html_string)
        f.close()


def pandas2html(data_frame):
    return data_frame.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-bordered">')


def make_figure(x, y, file_name):

    xy_data = go.Scatter(x=x, y=y, mode='lines+markers')
    fig = go.Figure(xy_data)
    fig.show()
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20),
                      paper_bgcolor="white")
    #fig.write_html(file_name)
    write_html(fig, file_name)
    first_plot_url = plot(fig, filename=file_name, auto_open=False)
    return first_plot_url


fn = 'plot.html'
u = np.arange(4)
# k = np.ones(4)
#
# a = np.arange(10)
# a = a.reshape(-1, 2)
# ds = pd.DataFrame(data=a, columns=['hola', 'como'])
#
# ds.insert(2, 'estás', ['uno', 'dos', 'tres', 'cuatro', 'cinco'])
# df = pd.DataFrame(columns=['Nodo fallado', 'Acciones', 'Cantidad acciones'])
#
# reporte = Report(make_figure(u, k, fn), ds)
# reporte.make_report()


