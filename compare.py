from dash import Dash, Input, Output, html, dcc
import dash_mantine_components as dmc
from dash import Output, Input, html, callback

app = Dash(__name__)

app.layout = html.Div([
    dcc.ConfirmDialog(
        id='confirm-danger',
        message='Danger danger! Are you sure you want to continue?',
    ),
    html.Div(
        [
            dmc.Group(
                align='left',
                children=[
                    dmc.Select(
                        id="framework-select",
                        value="ng",
                        data=[
                            {"value": "react", "label": "React"},
                            {"value": "ng", "label": "Angular"},
                            {"value": "svelte", "label": "Svelte"},
                            {"value": "vue", "label": "Vue"},
                        ],
                        style={"width": 200, "marginBottom": 10},
                    ),
                    html.Div(
                        [dcc.Dropdown(['React', 'Angular', 'Svelte', 'Vue'], id='dropdown-danger')],
                        style={"width": 200, "marginBottom": 10},
                    )
                ]
            ),
            html.Div(
                [
                    dmc.Checkbox(id="checkbox-simple", label="New York City", mb=10),
                    dmc.Checkbox(id="checkbox-simple", label="Montréal", mb=10),
                    dmc.Checkbox(id="checkbox-simple", label="San Francisco", mb=10),
                ]
            )
        ]
    ),

])

if __name__ == '__main__':
    app.run_server(debug=True)
