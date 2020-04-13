from plotly.offline import plot, iplot
import plotly.graph_objects as go


class Report:

    def __init__(self, actions, stats):
        self.tb_actions = pandas2html(actions)
        self.tb_stats = pandas2html(stats)

    def make_report(self):

        html_string = '''
        <html> 
            <head>
              <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
                integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
              <style>
                body {
                  margin: 0 100;
                  background: white;
                }
              </style>
            </head>
            
            <body>
              <div class="my-3 py-3">
                <h1>Fault isolation and service restoration's report</h1>
              </div>
            
              <ul class="nav nav-tabs">
                <li class="nav-item"><a class="nav-link active" data-toggle="tab" href="#pro">Production</a></li>
                </li>
              </ul>
            
              <div class="tab-content">
                <div class="tab-pane fade" id="pro">
                  <div class="row my-3 pt-4">
                    <div class="col-2">
                      <div class="nav flex-column nav-pills"  role="tablist" aria-orientation="vertical">
                        <a class="nav-link active" data-toggle="pill" href="#actions-pill" aria-selected="true">Actions</a>
                        <a class="nav-link" data-toggle="pill" href="#statistics-pill" >Statistics</a>
                      </div>
                    </div>
                    <div class="col-10">
                      <div class="tab-content">
                        <div class="tab-pane fade show active" id="actions-pill" >
                            ''' + self.tb_actions + '''
                        </div>
                        <div class="tab-pane fade" id="statistics-pill">
                            ''' + self.tb_stats + '''
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            
            
              <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js"
                integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n"
                crossorigin="anonymous"></script>
              <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"
                integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo"
                crossorigin="anonymous"></script>
              <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"
                integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6"
                crossorigin="anonymous"></script>
            </body>
            
            </html>'''

        f = open('E:/MININT/SMSOSD/OSDLOGS/github/pg_fisr/code/report/pro_report.html', 'w')
        f.write(html_string)
        f.close()


def pandas2html(data_frame):
    first = data_frame.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-responsive w-auto">')
    return first.replace('<tr style="text-align: right;">', '<tr style="text-align: left;">')


def make_figure(x, y, file_name):
    xy_data = go.Scatter(x=x, y=y, mode='lines+markers')
    fig = go.Figure(xy_data)
    fig.show()
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="white")
    first_plot_url = plot(fig, filename=file_name, auto_open=False)
    return first_plot_url
