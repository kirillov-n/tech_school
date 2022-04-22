from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.db.models import Avg, Count, Q, Sum
from tech_school_app.models import *

import dash
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash

class DashboardView(TemplateView):
    """
    Представление "Дашборд", расширяющее админ-панель.
    Служит для отображения дашборда.
    """

    template_name = "dashboard.html"

    df = pd.read_csv(r"C:\Users\kiril\Desktop\pBNN\Data\result_table.csv", delimiter=";").copy()

    df_people = df[['name', 'group']].groupby('group').count().rename(columns={"name": "people"}).reset_index()

    fig = px.pie(df_people, values='people', names='group', title='Количество студентов в группах')

    df_question1 = df[['name', 'stud_1']].groupby('stud_1').count().rename(columns={"name": "people"}).reset_index()

    fig_1 = px.bar(df_question1, x='stud_1', y='people', title='Первый вопрос')

    df_question2 = df[['name', 'stud_2']].groupby('stud_2').count().rename(columns={"name": "people"}).reset_index()

    fig_2 = px.bar(df_question2, x='stud_2', y='people', title='Второй вопрос')

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = DjangoDash('dashboard', external_stylesheets=external_stylesheets)

    app.layout = html.Div(
        children=[
            html.Div(children='group', style={'fontSize': "24px"}, className='menu-title'),
            dcc.Dropdown(
                id='group-filter',
                options=[
                    {'label': group, 'value': group}
                    for group in df.group.unique()
                ],
                value='M-227',
                clearable=False,
                searchable=False,
                className='dropdown', style={'fontSize': "24px", 'textAlign': 'center'},
            ),

            html.Div(
                children=[
                    html.Div(
                        children=dcc.Graph(
                            id='bar_1',
                            figure=fig_1
                        ), style={'width': '50%', 'display': 'inline-block'}
                    ),
                    html.Div(
                        children=dcc.Graph(
                            id='bar_2',
                            figure=fig_2
                        ), style={'width': '50%', 'display': 'inline-block'}
                    )
                ]
            )
        ]
    )


    @app.callback(
        Output("bar_1", "figure"),
        [Input("group-filter", "value")],
    )
    def update_charts(group):
        df = pd.read_csv(r"C:\Users\kiril\Desktop\pBNN\Data\result_table.csv", delimiter=";").copy()
        filtered_data = df[df["group"] == group]
        filtered_data = filtered_data[['name', 'stud_1']].groupby('stud_1').count().rename(columns={"name": "people"}).reset_index()

        bar = px.bar(
            filtered_data,
            x='stud_1',
            y='people',
            title='Первый вопрос',
        )
        return bar

    @app.callback(
        Output("bar_2", "figure"),
        [Input("group-filter", "value")],
    )
    def update_charts(group):
        df = pd.read_csv(r"C:\Users\kiril\Desktop\pBNN\Data\result_table.csv", delimiter=";").copy()
        filtered_data = df[df["group"] == group]
        filtered_data = filtered_data[['name', 'stud_2']].groupby('stud_2').count().rename(
            columns={"name": "people"}).reset_index()

        bar = px.bar(
            filtered_data,
            x='stud_2',
            y='people',
            title='Второй вопрос',
        )
        return bar

