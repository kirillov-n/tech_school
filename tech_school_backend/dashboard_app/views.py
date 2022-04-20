from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.db.models import Avg, Count, Q, Sum
from tech_school_app.models import *

import dash
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

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)

    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    # df = pd.DataFrame({
    #     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    #     "Amount": [4, 1, 2, 2, 4, 5],
    #     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    # })

    df_groups = df.groupby('group').count()
    df_groups['group'] = df_groups.index
    fig = px.pie(df_groups, values='name', names='group', title='Количество студентов в группах')

    app.layout = html.Div(children=[

        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ],
        style={
            'position': 'static',
        }
    )
