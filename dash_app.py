import itertools

import dash
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, no_update
from dash_iconify import DashIconify

import education_requirement
import pubs
from apartments import Apartment
from buildings import Building
from employers import Employers
from pubs import Pubs
from restaurants import Restaurant

app = Dash(__name__)

bld = Building()
apt = Apartment()
rest = Restaurant()
pubs = Pubs()
empl = Employers()
rest_visitors = pd.read_csv("resources/journals/VisitorsRestaurants.csv")
pub_visitors = pd.read_csv("resources/journals/VisitorsPubs.csv")
resident_data = pd.read_csv("resources/attributes/resident_data.csv")

coord_dict = bld.compute_polygon()
x_bound, y_bound = bld.get_x_y_bounds()
fig = go.Figure(
    layout_xaxis_range=x_bound,
    layout_yaxis_range=y_bound)

# Right Charts
N = 20
random_x = np.linspace(0, 1, N)
random_y0 = np.abs(np.random.randn(N))
fig_right_row_1 = go.Figure()
for day in range(7):
    offset = day * 24
    fig_right_row_1.add_trace(go.Bar(x=list(range(offset, offset + 24)), y=[0] * 24, name="visitor_freq_" + str(day),
                                     showlegend=False, marker=dict(color="#eb4a4a"),
                                     hovertemplate="Ø %{y:.2f}<extra></extra>"))

fig_right_row_1.update_layout(
    xaxis=dict(range=[-1, 168]),
    yaxis=dict(range=[0, 30]),
    transition=dict(
        duration=500,
        easing="cubic-in-out"
    ),
    hovermode="x",
    yaxis_title="Ø visitor count",
    legend=dict(x=0, y=1),
    grid_xgap=0,
    autosize=False,
    width=750,
    height=250,
    margin=dict(l=5, r=5, b=5, t=5, pad=4),
)
fig_right_row_1.update_xaxes(showgrid=False, range=[-1, 168],
                             tickvals=[0, *list(itertools.accumulate(([12] * 14)))],
                             ticktext=["00 AM", *list(["12 PM", "00 AM"] * 14)], ticks="outside")
fig_right_row_1.update_yaxes(showgrid=False, zeroline=False, range=[0, 30], ticks="outside")
for i, day_str in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
    fig_right_row_1.add_vrect(x0=24 * i,
                              x1=24 * i + 24,
                              annotation_text=day_str, annotation_position="top", opacity=0, line_width=0,
                              layer="below")
    fig_right_row_1.add_vline(x=24 * i, line_width=1, line_dash="solid", line_color="#2b2b2b", layer="below",
                              opacity=0.25)
fig_right_row_1.add_vline(x=24 * 7, line_width=1, line_dash="solid", line_color="#2b2b2b", layer="below",
                          opacity=0.25)

fig_right_row_2 = go.Figure()


def reset_fig_right_row_2_traces_by_list(lst: list):
    for j in lst:
        fig_right_row_2.update_traces(patch=dict(
            x=[0.0, 0.1], y=[j, j]
        ), selector=dict(name="line" + str(j)))
        fig_right_row_2.update_traces(patch=dict(
            x=[0.0], y=[j], marker=dict(color="#87939a", size=0.1)
        ), selector=dict(name="marker" + str(j)))


rest.restaurants.sort_values(by=["foodCost"], inplace=True)
pubs.pubs.sort_values(by=["hourlyCost"], inplace=True)
for i in list(range(1, len(rest.restaurants["foodCost"]) + 1)):
    fig_right_row_2.add_trace(go.Scatter(x=[0.0, 0.0], y=[i, i], mode="lines", name="line" + str(i), showlegend=False,
                                         line=dict(color="#87939a", width=0), hoverinfo="skip"))
    fig_right_row_2.add_trace(go.Scatter(x=[0.0], y=[i], mode="markers", name="marker" + str(i),
                                         marker=dict(color="#87939a", size=0),
                                         hovertemplate="%{x:.2f}$<extra></extra>"))
fig_right_row_2.update_layout(
    legend=dict(x=0, y=1),
    grid_xgap=0,
    autosize=False,
    showlegend=False,
    width=250,
    height=350,
    margin=dict(l=55, r=5, b=5, t=5, pad=4)
)
fig_right_row_2.update_xaxes(showgrid=False, zeroline=False, range=[0, 16], ticks="outside", title="select",
                             fixedrange=True)
fig_right_row_2.update_yaxes(showgrid=False, zeroline=False, ticks="outside", fixedrange=True,
                             tickvals=list(range(1, len(rest.restaurants["restaurantId"]) + 1)),
                             ticktext=rest.restaurants["restaurantId"],
                             range=[0.5, len(rest.restaurants["restaurantId"]) + 0.5])


# Create Sankey diagram
def custom_data_node_factory(x_iter):
    return np.stack((["their home", "their workplace", "a pub", "a different restaurant", "school", "anywhere", ""],
                     [*(["of all participants<br>visiting this place<br>are coming from"] * 6),
                      "...they all come<br>from somewhere"],
                     list(map(lambda _x: "{:3.2f}".format(_x * 100), x_iter))),
                    axis=-1)


origin_rest_data = pd.read_csv("resources/attributes/OriginRestaurantVisitors.csv")
origin_pub_data = pd.read_csv("resources/attributes/OriginPubVisitors.csv")
sankey_labels = ["Home", "Employer", "Pub", "Restaurant", "School", "Unknown", "Selected<br>location"]
fig_right_row_3 = go.Figure()
fig_right_row_3.add_trace(go.Sankey(
    name="sankey",
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="#c1c7cf", width=0.5),
        label=sankey_labels,
        customdata=custom_data_node_factory([0.2, 0.2, 0.2, 0.2, 0.1, 0.1, 1.0]),
        hovertemplate="%{customdata[2]}% %{customdata[1]} %{customdata[0]}<extra></extra>",
        color="#c1c7cf"
    ),
    link=dict(
        source=[0, 1, 2, 3, 4, 5],
        target=[6] * 6,
        value=[0.2, 0.2, 0.2, 0.2, 0.1, 0.1],
        customdata=[0.2, 0.2, 0.2, 0.2, 0.1, 0.1],
        hovertemplate="%{customdata}<extra></extra>", )
))

fig_right_row_3.update_layout(
    legend=dict(x=0, y=1),
    grid_xgap=0,
    autosize=False,
    showlegend=False,
    width=460,
    height=350,
    margin=dict(l=5, r=5, b=5, t=5, pad=4)
)

color_dict = bld.get_color_dict()

# Add polygons one by one
exterior_dict, interiors_dict, mapped_coords_dict = bld.polygon_generator(apt)
# Real building exteriors
for bld_type in exterior_dict.keys():
    mapped_coords = mapped_coords_dict[bld_type]
    bld_id_lst = bld.get_building_with_key(bld_type)
    curr_bld_id = bld_id_lst.pop(0)
    fig.add_trace(go.Scatter(x=list(exterior_dict[bld_type][0]), y=list(exterior_dict[bld_type][1]),
                             fill="toself",
                             customdata=np.stack((["B"] * len(mapped_coords),
                                                  list(mapped_coords)),
                                                 axis=-1),
                             name=str(bld_type),
                             line=dict(color=color_dict[bld_type], width=1),
                             hoveron="points",
                             opacity=0.75,
                             hovertemplate="<b>" + str(bld_type) + "</b><br>Id: %{customdata[1]}<extra></extra>"))
    if bld_type == "Residential":
        for bld_id, avg, color in bld.average_rental_cost:
            shell, _ = bld.single_polygon_generator_(bld_id)
            fig.add_trace(go.Scatter(x=shell[0], y=shell[1],
                                     visible=False,
                                     mode="none",
                                     fill="toself",
                                     fillcolor=color,
                                     name="Residential_RentalCost",
                                     line=dict(color="#bcb8b1", width=1),
                                     hoverinfo="skip",
                                     showlegend=False))

# Holes of each building
for bld_type in interiors_dict.keys():
    fig.add_trace(go.Scatter(x=interiors_dict[bld_type][0],
                             y=interiors_dict[bld_type][1],
                             fill="toself",
                             fillcolor="#e5ecf6",
                             hoverinfo="skip",
                             opacity=0.75,
                             showlegend=False,
                             name=str(bld_type),
                             line=dict(color=color_dict[bld_type], width=1)))

# Add empty trace
fig.add_trace(
    go.Scatter(name="clickBuilding",
               x=[],
               y=[],
               hoverinfo="skip",
               showlegend=False,
               line=dict(color="#2b2b2b", width=2),
               mode="lines"))

# Add apartments
id_with_location = apt.get_points()
ids = list(map(lambda tpl: tpl[0], id_with_location))
x = list(map(lambda tpl: tpl[1][0], id_with_location))
y = list(map(lambda tpl: tpl[1][1], id_with_location))
rentalCost = list(map(lambda tpl: tpl[2], id_with_location))
fig.add_trace(
    go.Scatter(name="Apartments",
               visible=False,
               x=x,
               y=y,
               mode="markers",
               opacity=0.9,
               marker=dict(color="#2b2b2b", opacity=0.75),
               customdata=np.stack((["A"] * len(ids),
                                    list(ids),
                                    list(rentalCost)),
                                   axis=-1),
               hovertemplate="<b>🏘 Apartment</b><br>Id: %{customdata[1]} <br>"
                             "Rental cost: %{customdata[2]}$<extra></extra>"))

# Add restaurants
id_with_location = rest.get_points()
ids = list(map(lambda tpl: tpl[0], id_with_location))
x = list(map(lambda tpl: tpl[1][0], id_with_location))
y = list(map(lambda tpl: tpl[1][1], id_with_location))
maxOccupancy = list(map(lambda tpl: tpl[2], id_with_location))
fig.add_trace(
    go.Scatter(name="Restaurants",
               visible=False,
               x=x,
               y=y,
               mode="markers",
               marker=dict(color="#e40d0d",
                           opacity=0.75,
                           line=dict(
                               width=0
                           ),
                           size=[occ * 0.2 for occ in maxOccupancy]),
               customdata=np.stack((["R"] * len(ids),
                                    list(ids),
                                    list(maxOccupancy)), axis=-1),
               hovertemplate="<b>🍴 Restaurant</b><br>Id: %{customdata[1]}<br>"
                             "Seats: %{customdata[2]}<extra></extra>"))

# Add Pubs
id_with_location = pubs.get_points()
ids = list(map(lambda tpl: tpl[0], id_with_location))
x = list(map(lambda tpl: tpl[1][0], id_with_location))
y = list(map(lambda tpl: tpl[1][1], id_with_location))
maxOccupancy = list(map(lambda tpl: tpl[2], id_with_location))
fig.add_trace(
    go.Scatter(name="Pubs",
               visible=False,
               x=x,
               y=y,
               mode="markers",
               marker=dict(color="#804bb6",
                           opacity=0.75,
                           line=dict(
                               width=0
                           ),
                           size=[occ * 0.2 for occ in maxOccupancy]),
               customdata=np.stack((["P"] * len(ids),
                                    list(ids),
                                    list(maxOccupancy)), axis=-1),
               hovertemplate="<b>🍻 Pub</b><br>Id: %{customdata[1]}<br>"
                             "Seats: %{customdata[2]}<extra></extra>"))

# Add Employers
id_with_location = empl.get_points()
ids = list(map(lambda tpl: tpl[0], id_with_location))
x = list(map(lambda tpl: tpl[1][0], id_with_location))
y = list(map(lambda tpl: tpl[1][1], id_with_location))
fig.add_trace(
    go.Scatter(name="Employers",
               visible=False,
               x=x,
               y=y,
               mode="markers",
               marker=dict(color="#2b8a3e",
                           opacity=0.75,
                           line=dict(
                               width=0
                           )),
               customdata=np.stack((["E"] * len(ids),
                                    list(ids),
                                    list(x)), axis=-1),
               hovertemplate="<b>🏢 Employer</b><br>Id: %{customdata[1]}<extra></extra>"))

fig.update_xaxes(showgrid=False, zeroline=False, ticks="", visible=False)
fig.update_yaxes(showgrid=False, zeroline=False, ticks="", visible=False)
fig.update_layout(
    legend=dict(x=0, y=1),
    grid_xgap=0,
    autosize=False,
    width=740 + 125,
    height=700,
    margin=dict(l=5, r=125, b=5, t=5, pad=4)
)

# Age distribution piechart
df_age = pd.read_csv("resources/attributes/Participants.csv")
l = list(set(df_age['age']))
df_age_list = list(df_age['age'])
l.sort()
lab = ['18-22', '23-27', '28-32', '33-37', '38-42', '43-47', '48-52', '53-57', '57-61']
res = [0] * 9

for x in l:
    y = df_age_list.count(x)
    if 18 <= x <= 22:
        res[0] += y
    elif 23 <= x <= 27:
        res[1] += y
    elif 28 <= x <= 32:
        res[2] += y
    elif 33 <= x <= 37:
        res[3] += y
    elif 38 <= x <= 42:
        res[4] += y
    elif 43 <= x <= 47:
        res[5] += y
    elif 48 <= x <= 52:
        res[6] += y
    elif 53 <= x <= 57:
        res[7] += y
    elif 57 <= x <= 61:
        res[8] += y

# age_plot = plt.pie(x=res, labels=lab, autopct='%1.1f%%')
age_plot = go.Figure(data=[go.Pie(labels=lab, values=res, pull=[0, 0, 0, 0])])
# age education pie chart
df_age2 = pd.read_csv("resources/attributes/Participants.csv")
l = list(set(df_age2['age']))
df_age2_list = list(df_age2['age'])
l.sort()
lab = ['18-22', '23-27', '28-32', '33-37', '38-42', '43-47', '48-52', '53-57', '57-61']
res = [0] * 9

df_degree = pd.read_csv('resources/attributes/Participants.csv')
series = df_degree['educationLevel'].value_counts()

df_result = pd.DataFrame(series)
df_result = df_result.reset_index()
df_result.columns = ['education', 'total']
age_education_fig = px.pie(df_result, values='total', names='education')

# Resident data pie chart
resident_data = pd.read_csv("resources/attributes/resident_data.csv")
resident_data['apartmentId'] = resident_data['apartmentId'].astype(str)
resident_data['buildingId'] = resident_data['buildingId'].astype(str)
resident_data['size'] = resident_data['size'].astype(int)
resident_data = resident_data.sort_values('size', ascending=True)
rd_fig = px.pie(resident_data, values='apartmentId', names='size', category_orders={"size": ['1', '2', '3', '4']},
                title="Apartment Occupation based on Household Size")
rd_fig.update_layout(legend_title_text='Houshold Size')
rd_fig.update_traces(hoverinfo='label+value', textfont_size=12)

# joviality violin chart
participant = pd.read_csv("resources/attributes/Participants.csv")
participant = participant.sort_values('age', ascending=True)
jovi_fig = px.violin(participant, y="joviality", box=True, color="haveKids", animation_frame='age', points='all',
                     title="Happiness Level based on Age")
jovi_fig.update_layout(legend_title_text='Have Kids', plot_bgcolor='rgba(0,0,0,0)')

# financial status pie chart
financial_status = pd.read_csv("resources/attributes/participant_financial_status.csv")
fs_fig = px.pie(financial_status, values='participantId', names='financialStatus',
                category_orders={"financialStatus": ['Stable', 'Unstable', 'Others']},
                title="Participant Financial Status")
fs_fig.update_layout(legend_title_text='Financial Status')
fs_fig.update_traces(hoverinfo='percent+label', textfont_size=12)

# job change stack chart
job_change = pd.read_csv("resources/attributes/JobSwitchingData.csv")
job_change = job_change.sort_values('participantId', ascending=True)
job_change['participantId'] = job_change['participantId'].astype(str)
job_change['last_jobId'] = job_change['last_jobId'].astype(str)
job_change['last_change_date'] = job_change["last_change_date"].astype(str)
jc_fig = go.Figure(data=[
    go.Bar(name='Unstable', x=job_change['participantId'], y=job_change['unstable'],
           text='Last JobId: ' + job_change['last_jobId'] + '<br> Last job change' + job_change['last_change_date'],
           textposition='none'),
    go.Bar(name='Stable', x=job_change['participantId'], y=job_change['stable'],
           text='Last JobId: ' + job_change['last_jobId'] + '<br> Last job change' + job_change['last_change_date'],
           textposition='outside'),
])
# Update the bar layout
jc_fig.update_layout(barmode='stack',
                     legend_title_text='Financial Status',
                     yaxis_title='Number of Job',
                     xaxis_title='Participant Id',
                     title='Job Hopper Information',
                     plot_bgcolor='rgba(0,0,0,0)'
                     )

"""
HEADER
"""
header = dmc.Header(
    height=75,
    withBorder=True,
    fixed=True,
    children=[
        dmc.Group(
            position="apart",
            spacing=0,
            children=[
                dmc.Center(
                    style={"height": 75, "width": 200},
                    children=[
                        dmc.Title(
                            "Visual Analytics Project",
                            align="center",
                            order=3
                        ),
                    ]
                ),
                dmc.Group(
                    position="right",
                    spacing=5,
                    children=[
                        dmc.Image(
                            withPlaceholder=True,
                            alt="Image",
                            src=app.get_asset_url("RPTU_Logo.png"),
                            height=50,
                            width=150,
                            fit="contain"
                        ),
                        dmc.Image(
                            withPlaceholder=True,
                            alt="Image",
                            src=app.get_asset_url("VIA-Logo.svg"),
                            height=50,
                            width=150,
                            fit="contain"
                        ),

                    ]
                )
            ])])

"""
ACCORDION
"""
accordion = dmc.Accordion(
    id="accordion_tab_switch",
    value="show_map",
    variant="seperated",
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "City exploration",
                    icon=DashIconify(
                        icon="ic:round-map",
                        color=dmc.theme.DEFAULT_COLORS["blue"][6],
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(
                    children=[
                        dmc.Paper(
                            children=[
                                dmc.Text("Map controls:"),
                                dmc.Space(h=5),
                                dmc.Switch(
                                    id="color_building_types",
                                    size="sm",
                                    onLabel="ON",
                                    offLabel="OFF",
                                    radius="lg",
                                    label="Color buildings",
                                    checked=True
                                ), ],
                            shadow="md",
                            p="md",
                            radius="md"
                        ),
                        dmc.Space(h=10),
                        dmc.Paper(
                            children=[
                                dmc.Text("Choose to display on map:"),
                                dmc.Space(h=5),
                                dmc.ChipGroup(
                                    children=[
                                        dmc.MantineProvider(
                                            theme={"primaryColor": "red"},
                                            children=dmc.Chip(
                                                "Restaurants",
                                                value="Restaurants",
                                                variant="outline",
                                                id="chip_Restaurants")),
                                        dmc.MantineProvider(
                                            theme={"primaryColor": "violet"},
                                            children=dmc.Chip(
                                                "Pubs",
                                                value="Pubs",
                                                variant="outline",
                                                id="chip_Pubs")),
                                        dmc.MantineProvider(
                                            theme={"primaryColor": "green"},
                                            children=dmc.Chip(
                                                "Employers",
                                                value="Employers",
                                                variant="outline",
                                                color="#2b2b2b",
                                                id="chip_Employers")),
                                        dmc.MantineProvider(
                                            theme={"primaryColor": "dark"},
                                            children=dmc.Chip(
                                                "Apartments",
                                                value="Apartments",
                                                variant="outline",
                                                id="chip_Apartments"))],
                                    id="chips_building_types",
                                    persistence=False,
                                    multiple=True,
                                    value=[]
                                )
                            ],
                            shadow="md",
                            p="md",
                            radius="md"
                        ),
                        dmc.Space(h=10),
                        dmc.Paper(
                            children=[
                                html.Div(id="alert_apartment"),
                                dmc.Space(h=5),
                                dmc.Select(
                                    id="select_apartment",
                                    data=["Rental costs", "Occupancy", "Average monthly Spending"],
                                    label="Select hue attribute for apartments:",
                                    clearable=True
                                )
                            ],
                            shadow="md",
                            p="md",
                            radius="md"
                        ),
                    ]
                ),
            ],
            value="show_map",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Overview",
                    icon=DashIconify(
                        icon="grommet-icons:overview",
                        color=dmc.theme.DEFAULT_COLORS["blue"][6],
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(),
            ],
            value="show_another",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    "Age & Education",
                    icon=DashIconify(
                        icon="mdi:education-outline",
                        color=dmc.theme.DEFAULT_COLORS["blue"][6],
                        width=20,
                    ),
                ),
                dmc.AccordionPanel(),
            ],
            value="show_something",
        ),
    ],
)

"""
NAVBAR
"""
navbar = dmc.Navbar(
    p="md",
    ml=0,
    mr=0,
    width={"base": 290},
    fixed=True,
    children=[
        accordion,
    ],
),

app.layout = dmc.NotificationsProvider(
    position="top-right",
    children=[html.Div([
        header,
        dmc.Space(h=75),
        navbar[0],
        dmc.Group(
            position="left",
            spacing=0,
            children=[
                html.Div(
                    id="show_map",
                    hidden=False,
                    children=[
                        dmc.Group(
                            position="left",
                            align="start",
                            spacing=5,
                            children=[
                                dmc.Space(w=290),
                                dmc.Paper(
                                    children=dmc.LoadingOverlay(
                                        id="city_map_loading_overlay",
                                        loaderProps={"variant": "oval", "color": "#2b2b2b", "size": "md"},
                                        children=[dcc.Graph(
                                            id="city_map",
                                            config=dict({"scrollZoom": True,
                                                         "modeBarButtonsToRemove": ["zoom", "autoscale"],
                                                         "displaylogo": False}),
                                            figure=fig)]
                                    ),
                                    shadow="md",
                                    p="md",
                                    radius="md"
                                ),
                                dmc.Space(h=5),
                                dmc.Stack(
                                    justify="flex-start",
                                    align="flex-start",
                                    spacing=5,
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Group(
                                                    position="left",
                                                    align="start",
                                                    grow=True,
                                                    spacing=5,
                                                    children=[
                                                        dmc.Text(
                                                            children="Click to analyze pub or "
                                                                     "restaurant",
                                                            id="text_field_caption")])
                                            ],
                                            shadow="md",
                                            p="md",
                                            radius="md"
                                        ),
                                        dmc.Paper(
                                            children=[
                                                dcc.Graph(
                                                    id="right_row_1",
                                                    config=dict({"scrollZoom": True,
                                                                 "modeBarButtonsToRemove": ["zoom",
                                                                                            "autoscale"],
                                                                 "displaylogo": False}),
                                                    figure=fig_right_row_1)],
                                            shadow="md",
                                            p="md",
                                            radius="md"
                                        ),
                                        dmc.Group(
                                            position="left",
                                            spacing=5,
                                            children=[
                                                dmc.Paper(
                                                    shadow="md",
                                                    p="md",
                                                    radius="md",
                                                    children=[
                                                        dmc.LoadingOverlay(
                                                            id="fig_row_2_loading_overlay",
                                                            loaderProps={"variant": "oval",
                                                                         "color": "#2b2b2b",
                                                                         "size": "md"},
                                                            children=[
                                                                dcc.Graph(
                                                                    id="right_row_2",
                                                                    config=dict(
                                                                        {"scrollZoom": False,
                                                                         "displayModeBar": False}),
                                                                    figure=fig_right_row_2),
                                                            ])]
                                                ),
                                                dmc.Paper(
                                                    shadow="md",
                                                    p="md",
                                                    radius="md",
                                                    children=[
                                                        dmc.LoadingOverlay(
                                                            id="fig_row_3_loading_overlay",
                                                            loaderProps={"variant": "oval",
                                                                         "color": "#2b2b2b",
                                                                         "size": "md"},
                                                            children=[
                                                                dcc.Graph(
                                                                    id="right_row_3",
                                                                    config=dict(
                                                                        {"scrollZoom": False,
                                                                         "displayModeBar": False}),
                                                                    figure=fig_right_row_3),
                                                            ])]
                                                )
                                            ],
                                        ),
                                    ]
                                ),
                                dcc.Store(id="id_states", data=dict(
                                    Restaurants=None,
                                    Pubs=None,
                                )),
                                dcc.Store(id="id_employer", data=dict(
                                    Employer=None,
                                )),
                                dcc.Store(id="states", data=dict(
                                    Restaurants=False,
                                    Pubs=False,
                                    Apartments=False,
                                    Employers=False)),
                                dcc.Store(id="is_restaurant",
                                          data=dict(wasRestaurant=False)),
                            ]
                        )
                    ],
                ),
                html.Div(
                    id="show_something",
                    hidden=True,
                    children=[
                        dmc.Group(
                            position="left",
                            align="start",
                            spacing=5,
                            children=[
                                dmc.Space(w=290),
                                dmc.Paper(
                                    shadow="md",
                                    p="md",
                                    radius="md",
                                    children=[
                                        dmc.Title("Age and Education Overview", order=4),
                                        dmc.Text(
                                            children="Click on map to analyze employer",
                                            id="text_field_employer"),
                                        dcc.Graph(
                                            id="id_educational_employer_requirement",
                                            config=dict({"scrollZoom": False, "displayModeBar": False}),
                                            figure=education_requirement.fig),
                                        dmc.Title("Age Overview", order=4),
                                        dmc.Container(
                                            children=dmc.Grid(
                                                children=[
                                                    dmc.Col(
                                                        children=[
                                                            dmc.Text("Total number of participants: 1011 ", size="md"),
                                                            dcc.Graph(id='age_distribution', figure=age_plot),
                                                            dcc.Graph(id='age_education', figure=age_education_fig)
                                                        ])
                                                ]
                                            )
                                        )

                                    ]
                                )
                            ])
                    ]
                ),
                html.Div(
                    id="show_another",
                    hidden=True,
                    children=[
                        dmc.Space(w=290),
                        dmc.Group(
                            position="left",
                            align="start",
                            spacing=5,
                            children=[
                                dmc.Space(w=290),
                                dmc.Paper(
                                    children=dmc.LoadingOverlay(
                                        dmc.Stack(
                                            id="info-graph",
                                            children=[
                                                dmc.Title("Information Overview", order=4),
                                                dmc.Container(
                                                    children=dmc.Grid(
                                                        children=[
                                                            dmc.Col(
                                                                children=[
                                                                    dmc.Space(h=20),
                                                                    dmc.Text("According to Vast-2022 data record: ",
                                                                             size="md"),
                                                                    dmc.Space(h=10),
                                                                    dmc.List([
                                                                        dmc.ListItem(
                                                                            "Data periode: '2022-03-01 00:00:00' - '2023-05-24 04:30:00'."),
                                                                        dmc.ListItem(
                                                                            "Location: The city of Engagement, Ohio, USA."),
                                                                        dmc.ListItem(
                                                                            "Total participants: 1011 citizens"),
                                                                        dmc.ListItem(
                                                                            "Total building: 1042, divided into residental (526), schools (4), and commersial (512)"),
                                                                        dmc.ListItem(
                                                                            "Total apartment: 1.517 (845 apartments are occupied)"),
                                                                        dmc.ListItem(
                                                                            "808 apartments are occupied with a single tenant. The rest is occupied by 2-4 persons in an apartment."),
                                                                    ])
                                                                ], span=6),
                                                            dmc.Col(dcc.Graph(id='rd', figure=rd_fig), span=6),
                                                            dmc.Col(dcc.Graph(id='jov', figure=jovi_fig)),
                                                            dmc.Col(dcc.Graph(id='fs', figure=fs_fig), span=6),
                                                            dmc.Col(
                                                                children=[
                                                                    dmc.Space(h=100),
                                                                    dmc.Text(
                                                                        "Most citizens stay in the same job throughout the survey period, either with stable or unstable financial status."
                                                                        "However, several citizens have multiple jobs daily and keep switching jobs several times.",
                                                                        size="md"),
                                                                    dmc.Space(h=10),
                                                                    dmc.Text(
                                                                        "Other financial status: Participants who detected alternation in financial status (from unstable to stable) or had several jobs.",
                                                                        size="md")
                                                                ],
                                                                span=6,
                                                            ),
                                                            dmc.Col(dcc.Graph(id='jc', figure=jc_fig))

                                                        ]
                                                    )
                                                ),
                                            ]
                                        )
                                    ),
                                    shadow="md",
                                    p="md",
                                    radius="md"
                                )
                            ]
                        )
                    ],
                )

            ],
        ),
        dmc.Footer(
            height=60,
            fixed=True,
            withBorder=False,
            children=[
                dmc.Paper(
                    children=[
                        dmc.Stack(
                            align="center",
                            justify="center",
                            spacing="xs",
                            children=[
                                dmc.Group(
                                    children=[
                                        dmc.Button("About",
                                                   id="about_button",
                                                   variant="outline",
                                                   radius=8,
                                                   leftIcon=DashIconify(icon="material-symbols:info-outline")),
                                        dmc.Button("Feedback",
                                                   id="feedback_button",
                                                   variant="outline",
                                                   disabled=True,
                                                   radius=8,
                                                   leftIcon=DashIconify(icon="ic:outline-feedback")),
                                    ]
                                ),
                            ]
                        ),

                        dmc.Stack(
                            align="center",
                            justify="center",
                            spacing="xs",
                            children=[
                                dmc.Modal(
                                    title="Feedback",
                                    id="modal_feedback",
                                    size="lg",
                                    transition="scale-y",
                                    children=[
                                        dmc.Stack(
                                            children=[
                                                dmc.Textarea(
                                                    label="",
                                                    description="Your feedback is important to us, tell us what you think",
                                                    placeholder="Enter to start typing amazing feedback...",
                                                    required=False,
                                                    minRows=5,
                                                    maxRows=5
                                                ),
                                                dmc.Group(
                                                    position="center",
                                                    spacing=5,
                                                    grow=True,
                                                    children=[
                                                        dmc.ActionIcon(
                                                            DashIconify(icon="lucide:thumbs-up", width=20),
                                                            size="lg",
                                                            variant="filled",
                                                            id="action_like",
                                                            n_clicks=0,
                                                            mb=10,
                                                            color="lime"
                                                        ),
                                                        dmc.ActionIcon(
                                                            DashIconify(icon="lucide:thumbs-up", rotate=2,
                                                                        width=20),
                                                            size="lg",
                                                            variant="filled",
                                                            id="action_dislike",
                                                            n_clicks=0,
                                                            mb=10,
                                                            color="red"
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),

                                    ],
                                ),
                                dmc.Modal(
                                    title="About Section",
                                    id="modal_about",
                                    size="lg",
                                    transition="scale-y",
                                    centered=True,
                                    children=[
                                        dmc.Paper(
                                            children=[
                                                dmc.Text("This is a project in which we as "
                                                         "students program and prepare a dashboard for data."),
                                            ],
                                            shadow="md",
                                            p="md",
                                            radius="md"
                                        ),
                                        dmc.Space(h=10),
                                        dmc.Paper(
                                            children=[
                                                dmc.Text("Helpful resources (links open in same tab):"),
                                                dmc.List(
                                                    [
                                                        dmc.ListItem(dmc.Anchor(
                                                            "VAST Challenge 2022",
                                                            href="https://vast-challenge.github.io/2022/index.html",
                                                        )),
                                                        dmc.ListItem(dmc.Anchor(
                                                            "Data files",
                                                            href="https://seafile.rlp.net/d/881af5fb3e40479fa394/",
                                                        )),
                                                        dmc.ListItem(dmc.Anchor(
                                                            "OLAT Link",
                                                            href="https://olat.vcrp.de/auth/RepositoryEntry/"
                                                                 "3872260104/CourseNode/104428096509648",
                                                        )),
                                                        dmc.ListItem(dmc.Anchor(
                                                            "Visual Information Analysis",
                                                            href="https://vis.uni-kl.de/",
                                                        )),
                                                    ]
                                                ),
                                            ],
                                            shadow="md",
                                            p="md",
                                            radius="md"
                                        ),
                                        dmc.Space(h=10),
                                        dmc.Paper(
                                            children=[
                                                dmc.Text("Have fun using our dashboard, but always keep in mind:"),
                                                dmc.Stack(align="center",
                                                          justify="center",
                                                          children=[
                                                              dmc.Image(
                                                                  src="/assets/cockroach.gif",
                                                                  alt="cockroach",
                                                                  caption="There might be bugs",
                                                                  width=200
                                                              )]
                                                          )
                                            ],
                                            shadow="md",
                                            p="md",
                                            radius="md"
                                        )],
                                ),
                            ]
                        )
                    ],
                    shadow="md",
                    p="md",
                    radius="md"
                )]
        ),
    ])])

click_states = dict({"hover_bld_id": -1})


def keep_current_axis_range(layout_data):
    if layout_data is not None:
        fig.update_xaxes(range=[layout_data["xaxis.range[0]"],
                                layout_data["xaxis.range[1]"]])
        fig.update_yaxes(range=[layout_data["yaxis.range[0]"],
                                layout_data["yaxis.range[1]"]])


@app.callback(
    Output("city_map", "figure"),
    Output("city_map_loading_overlay", "children"),
    Output("id_states", "data"),
    Output("is_restaurant", "data"),
    Output("id_employer", "data"),
    Input("color_building_types", "checked"),
    Input("chips_building_types", "value"),
    Input("city_map", "clickData"),
    Input("select_apartment", "value"),
    State("city_map", "relayoutData"),
    State("states", "data"),
    State("id_states", "data"),
    State("is_restaurant", "data"),
    State("id_employer", "data")
)
def update_value(checked, value, click_data, apartment_selection_data, layout_data,
                 _states, _id_states, rest_state, _employer_state):
    if dash.callback_context.triggered_id == "color_building_types":
        for trace in fig.select_traces():
            name = trace["name"]
            if name in color_dict.keys():
                if not checked:
                    fig.layout["showlegend"] = False
                    _color = "#bcb8b1"
                else:
                    fig.layout["showlegend"] = True
                    _color = color_dict[name]
                trace["line"]["color"] = _color
    elif dash.callback_context.triggered_id == "chips_building_types":
        update_map(value, _states, apartment_selection_data)
    elif dash.callback_context.triggered_id == "select_apartment":
        match apartment_selection_data:
            case "Rental costs":
                fig.update_traces(
                    selector=dict(name="Apartments"),
                    patch=dict(
                        marker=dict(
                            color=rentalCost,
                            colorbar=dict(thickness=15,
                                          outlinewidth=0,
                                          title="Rental cost",
                                          lenmode="fraction",
                                          len=0.5),
                            colorscale="Viridis",
                            opacity=0.75
                        )
                    ),
                    overwrite=True)
                if _states["Apartments"]:
                    fig.update_traces(patch=dict(visible=True), selector=dict(name="Residential_RentalCost"))
            case None:
                fig.update_traces(selector=dict(name="Apartments"),
                                  patch=dict(
                                      marker=dict(color="#2b2b2b", opacity=0.75),
                                  ),
                                  overwrite=True)
                fig.update_traces(patch=dict(visible=False), selector=dict(name="Residential_RentalCost"))
    elif dash.callback_context.triggered_id == "city_map":
        if click_data is not None:
            custom_data = click_data["points"][0]["customdata"]
            if str(custom_data[0]) == "B":
                _bld_id = custom_data[1]
                if click_states["hover_bld_id"] != _bld_id:
                    click_states["hover_bld_id"] = _bld_id
                    _shell, _ = bld.single_polygon_generator_(_bld_id)
                    fig.update_traces(selector={"name": "clickBuilding"},
                                      patch=dict(x=list(_shell[0]),
                                                 y=list(_shell[1])))
            elif str(custom_data[0]) == "R":
                rest_id = custom_data[1]
                _id_states["Restaurants"] = rest_id
                rest_state["wasRestaurant"] = True
                return no_update, no_update, _id_states, rest_state, no_update
            elif str(custom_data[0]) == "P":
                pub_id = custom_data[1]
                _id_states["Pubs"] = pub_id
                rest_state["wasRestaurant"] = False
                return no_update, no_update, _id_states, rest_state, no_update
            elif str(custom_data[0]) == "E":
                employer_id = custom_data[1]
                _employer_state["Employer"] = employer_id
                return no_update, no_update, no_update, no_update, _employer_state
        else:
            return no_update, no_update, no_update, no_update, no_update
    keep_current_axis_range(layout_data)
    return fig, no_update, no_update, no_update, no_update


def handle_event_on(_state_key):
    fig.update_traces(selector=dict(name=_state_key), patch=dict(visible=True))


def handle_event_off(_state_key):
    fig.update_traces(selector=dict(name=_state_key), patch=dict(visible=False))
    if _state_key == "Apartments":
        fig.update_traces(patch=dict(visible=False), selector=dict(name="Residential_RentalCost"))


def update_map(value, _states, _apartment_selection_data):
    for state_key in _states.keys():
        if state_key in value:
            if not _states[state_key]:
                # Change toggle on
                handle_event_on(state_key)
                if state_key == "Apartments" and _apartment_selection_data == "Rental costs":
                    fig.update_traces(patch=dict(visible=True), selector=dict(name="Residential_RentalCost"))
                if len(value) == 1:
                    fig.update_traces(patch=dict(line=dict(color="#bcb8b1")),
                                      selector=lambda graph_object: graph_object.name in (exterior_dict.keys()))
        else:
            if _states[state_key]:
                # Change toggle off
                handle_event_off(state_key)
                if len(value) == 0:
                    for trace in color_dict.keys():
                        fig.update_traces(patch=dict(line=dict(color=color_dict[trace])), selector=dict(name=trace))


@app.callback(
    Output("modal_about", "opened"),
    Input("about_button", "n_clicks"),
    State("modal_about", "opened"),
    prevent_initial_call=True,
)
def toggle_modal(n_clicks, opened):
    return not opened


@app.callback(
    Output("modal_feedback", "opened"),
    Input("feedback_button", "n_clicks"),
    State("modal_feedback", "opened"),
    prevent_initial_call=True,
)
def toggle_modal_feedback(n_clicks, opened):
    return not opened


@app.callback(
    Output("states", "data"),
    Input("chips_building_types", "value"),
    Input("states", "data")
)
def update_states(value, _states):
    for state_key in _states.keys():
        if state_key in value:
            if not _states[state_key]:
                # Change toggle on
                _states[state_key] = True
        else:
            if _states[state_key]:
                # Change toggle off
                _states[state_key] = False
    return _states


@app.callback(
    Output("alert_apartment", "children"),
    Input("select_apartment", "value"),
    State("states", "data"),
    prevent_initial_call=True,
)
def alert_auto(value, data):
    if value is not None and dash.callback_context.triggered_id == "select_apartment":
        if not data["Apartments"]:
            return dmc.Notification(
                title="Warning!",
                id="simple-notify",
                action="show",
                radius="md",
                color="yellow",
                message="Select apartments (right above) to see this selection in effect.",
                icon=DashIconify(icon="mdi:warning-circle-outline")
            )


@app.callback(
    Output("text_field_caption", "children"),
    Input("id_states", "data"),
    State("is_restaurant", "data"),
    prevent_initial_call=True,
)
def write_text_field(data, rest_data):
    rest_id = data["Restaurants"]
    pub_id = data["Pubs"]
    if rest_data["wasRestaurant"]:
        if rest_id is not None:
            return f"🍴 Analyzing restaurant: {str(rest_id)}"
    else:
        if pub_id is not None:
            return f"🍻 Analyzing pub: {str(pub_id)}"
    return no_update


@app.callback(
    Output("text_field_employer", "children"),
    Output("id_educational_employer_requirement", "figure"),
    Input("id_employer", "data"),
    prevent_initial_call=True,
)
def write_text_field_employer(data):
    employer_id = data["Employer"]
    if employer_id is not None:
        val_list = ['LowCount', 'HighSchoolOrCollegeCount', 'BachelorsCount', 'GraduateCount']
        df_new = education_requirement.get_dataframe_employer_education()
        df_employer_id = df_new[df_new.employerId == int(employer_id)]
        _fig = go.Figure([go.Bar(x=['LowCount', 'HighSchoolOrCollegeCount', 'BachelorsCount', 'GraduateCount'],
                                 y=list(map(lambda elem: df_employer_id[elem].iloc[0], val_list)))])
        return f"🏢 Analyzing employer: {str(employer_id)}", _fig
    return no_update, no_update


@app.callback(
    Output("right_row_1", "figure"),
    Input("id_states", "data"),
    State("is_restaurant", "data"),
    prevent_initial_call=True,
)
def display_right_row_1(data, rest_data):
    _rest_id = data["Restaurants"]
    pub_id = data["Pubs"]
    if rest_data["wasRestaurant"]:
        if _rest_id is not None:
            temp = rest_visitors.query("venueId == " + str(_rest_id), inplace=False)
            for day_i in range(7):
                df = temp.query("day ==" + str(day_i), inplace=False)
                hours = set(range(24))
                missing_values = hours.difference(df["24hour"])
                fig_right_row_1.update_traces(
                    patch=dict(x=day_i * 24 + pd.concat([df["24hour"], pd.Series(list(missing_values))],
                                                        ignore_index=True),
                               y=[*df["mean"].tolist(), *(len(missing_values) * [0.0])],
                               marker=dict(color="#eb4a4a")),
                    selector=dict(name="visitor_freq_" + str(day_i)))
    else:
        if pub_id is not None:
            temp = pub_visitors.query("venueId == " + str(pub_id), inplace=False)
            for day_i in range(7):
                df = temp.query("day ==" + str(day_i), inplace=False)
                hours = set(range(24))
                missing_values = hours.difference(df["24hour"])
                fig_right_row_1.update_traces(
                    patch=dict(x=day_i * 24 + pd.concat([df["24hour"], pd.Series(list(missing_values))],
                                                        ignore_index=True),
                               y=[*df["mean"].tolist(), *(len(missing_values) * [0.0])],
                               marker=dict(color="#a078c8")),
                    selector=dict(name="visitor_freq_" + str(day_i)))
    return fig_right_row_1


@app.callback(
    Output("right_row_2", "figure"),
    Output("fig_row_2_loading_overlay", "children"),
    Input("id_states", "data"),
    State("is_restaurant", "data"),
    prevent_initial_call=True,
)
def display_right_row_2(data, rest_data):
    upper_len_rest = len(rest.restaurants["restaurantId"])
    upper_len_pub = len(pubs.pubs["pubId"])
    _rest_id = data["Restaurants"]
    _pub_id = data["Pubs"]
    if rest_data["wasRestaurant"]:
        for temp_rest_id, temp_food_cost, j in zip(rest.restaurants["restaurantId"], rest.restaurants["foodCost"],
                                                   list(range(1, len(rest.restaurants["foodCost"]) + 1))):
            if temp_rest_id == int(_rest_id):
                width = 2
                _color = "#eb4a4a"
            else:
                width = 1
                _color = "#87939a"
            fig_right_row_2.update_traces(patch=dict(
                x=[0, temp_food_cost], y=[j, j], line=dict(width=width, color=_color)
            ), selector=dict(name="line" + str(j)))
            fig_right_row_2.update_traces(patch=dict(
                x=[temp_food_cost], y=[j], marker=dict(color="#eb4a4a", size=10)
            ), selector=dict(name="marker" + str(j)))
        fig_right_row_2.update_yaxes(showgrid=False, zeroline=False, ticks="outside",
                                     tickvals=list(range(1, upper_len_rest + 1)),
                                     ticktext=rest.restaurants["restaurantId"],
                                     range=[0.5, upper_len_rest + 0.5])
        fig_right_row_2.update_xaxes(patch=dict(title="food cost", range=[0, 7]))
    else:
        last_trace = -1
        for temp_pub_id, temp_fix_price, j in zip(pubs.pubs["pubId"], pubs.pubs["hourlyCost"],
                                                  list(range(1, len(pubs.pubs["hourlyCost"]) + 1))):
            if temp_pub_id == int(_pub_id):
                width = 2
                _color = "#a078c8"
            else:
                width = 1
                _color = "#87939a"
            fig_right_row_2.update_traces(patch=dict(
                x=[0, temp_fix_price], y=[j, j], line=dict(width=width, color=_color)
            ), selector=dict(name="line" + str(j)))
            fig_right_row_2.update_traces(patch=dict(
                x=[temp_fix_price], y=[j], marker=dict(color="#a078c8", size=10)
            ), selector=dict(name="marker" + str(j)))
            last_trace = j
        if last_trace != -1:
            reset_fig_right_row_2_traces_by_list(list(range(last_trace + 1, upper_len_rest + 1)))
        fig_right_row_2.update_yaxes(showgrid=False, zeroline=False, ticks="outside",
                                     tickvals=list(range(1, upper_len_pub + 1)),
                                     ticktext=pubs.pubs["pubId"],
                                     range=[0.5, upper_len_pub + 0.5])
        fig_right_row_2.update_xaxes(patch=dict(title="hourly cost", range=[0, 16]))
    return fig_right_row_2, no_update


@app.callback(
    Output("right_row_3", "figure"),
    Output("fig_row_3_loading_overlay", "children"),
    Input("id_states", "data"),
    State("is_restaurant", "data"),
    prevent_initial_call=True,
)
def display_right_row_3(data, rest_data):
    _rest_id = data["Restaurants"]
    _pub_id = data["Pubs"]
    if rest_data["wasRestaurant"]:
        _color = "#eb4a4a"
        rest_series = origin_rest_data.loc[origin_rest_data["restaurantId"] == int(_rest_id)]
        value = []
        for label in sankey_labels[0:-1]:
            value.append(round(rest_series[label].iloc[0], 2))
        fig_right_row_3.update_traces(patch=dict(
            link=dict(
                value=value,
                customdata=value
            ),
            node=dict(
                color=_color,
                customdata=custom_data_node_factory([*value, np.sum(value)])
            )), selector=dict(name="sankey"))
    else:
        _color = "#a078c8"
        pub_series = origin_pub_data.loc[origin_pub_data["pubId"] == int(_pub_id)]
        value = []
        for label in sankey_labels[0:-1]:
            value.append(round(pub_series[label].iloc[0], 2))
        fig_right_row_3.update_traces(patch=dict(
            link=dict(
                value=value,
                customdata=value),
            node=dict(
                color=_color,
                customdata=custom_data_node_factory([*value, np.sum(value)])
            )), selector=dict(name="sankey"))
    return fig_right_row_3, no_update


@app.callback(
    Output("show_map", "hidden"),
    Output("show_something", "hidden"),
    Output("show_another", "hidden"),
    Input("accordion_tab_switch", "value")
)
def switch_tab(value):
    if value == "show_map":
        return False, True, True
    elif value == "show_something":
        return True, False, True
    elif value == "show_another":
        return True, True, False
    else:
        return no_update, no_update, no_update


if __name__ == "__main__":
    app.run_server(debug=True, port=8080, host="localhost")
