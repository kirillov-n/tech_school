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
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash

queryset = Grade.objects.all().values()
groups = Group.objects.all().values()
membership = Membership.objects.all().values()
incp = InCP.objects.all().values()
calplan = CalendarPlan.objects.all().values()
personalinfo = PersonalInfo.objects.all().values()
students = Student.objects.all().values()

df_grades = pd.DataFrame(queryset)
df_groups = pd.DataFrame(groups)
df_membership = pd.DataFrame(membership)
df_incp = pd.DataFrame(incp)
df_calplan = pd.DataFrame(calplan)
df_personalinfo = pd.DataFrame(personalinfo)
df_personalinfo['FullName'] = df_personalinfo['surname'] + ' ' + df_personalinfo['name'] + ' ' + df_personalinfo['patronymic']
df_students = pd.DataFrame(students)

df = pd.merge(df_grades[['grade_type', 'grade', 'attendance', 'student_id']], df_membership[['group_id', 'student_id']],
              left_on='student_id', right_on='student_id')
df = pd.merge(df, df_groups[['id', 'name', 'program_id']], left_on='group_id', right_on='id')
df_ = pd.merge(df_incp[['calendarplan_id', 'program_id']], df_calplan[['id', 'year']], left_on='calendarplan_id',
               right_on='id')
df = pd.merge(df, df_, left_on='program_id', right_on='program_id')
df = pd.merge(df, df_students[['id', 'personal_info_id', 'personnel_num']], left_on='student_id', right_on='id')
df = pd.merge(df, df_personalinfo[['id', 'FullName']], left_on='personal_info_id', right_on='id')


def generate_table(dataframe, max_rows=20):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


fig_grades = px.bar(df[df["grade_type"] == 'g'], x='grade', y='student_id', title='Оценки')
pie_attendance = px.pie(df[df["grade_type"] == 'a'], names="attendance", title="Процент посещений", hole=0.5)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('dashboard', external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.Div(children='year', style={'fontSize': "24px"}, className='menu-title'),
        dcc.Dropdown(
            id='year-filter',
            options=[
                {'label': year, 'value': year}
                for year in df.year.unique()
            ],
            className='dropdown'
        ),
        html.Div(children='group', style={'fontSize': "24px"}, className='menu-title'),
        dcc.Dropdown(
            id='group-filter',
            className='dropdown'
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='bar_1',
                        figure=fig_grades
                    ), style={'width': '50%', 'display': 'inline-block'}
                ),
                html.Div(
                    children=dcc.Graph(
                        id='pie_attendance',
                        figure=pie_attendance
                    ), style={'width': '50%', 'display': 'inline-block'}
                ),
                html.Div(
                    children=generate_table(df)
                )
            ]
        )
    ]
)


@app.callback(
    [Output("group-filter", "options")],
    [Input("year-filter", "value")]
)
def update_options(value):
    options = [
                  {'label': group_name, 'value': group}
                  for group in df[df['year'] == value].group_id.unique()
                  for group_name in df[df['group_id'] == group].name.unique()
              ],
    return options


@app.callback(
    Output("bar_1", "figure"),
    [Input("group-filter", "value")],
)
def update_charts(group):
    filtered_data = df[df["group_id"] == group]
    filtered_data = filtered_data[filtered_data["grade_type"] == 'g']

    bar = px.bar(
        filtered_data,
        x='grade',
        y='student_id',
        color='FullName',
        hover_data=['personnel_num'],
        orientation='v',
        labels={'FullName': 'ФИО студента',
                'grade': 'Оценка',
                'student_id': 'ID студента',
                'personnel_num': 'Табельный номер'},
        title='Оценки',
    )
    return bar


@app.callback(
    Output("pie_attendance", "figure"),
    [Input("group-filter", "value")],
)
def update_charts(group):
    filtered_data = df[df["group_id"] == group]
    filtered_data = filtered_data[filtered_data["grade_type"] == 'a']
    filtered_data['attendance_viz'] = np.where(filtered_data['attendance'] == '0', 'Пропуск', 'Посещение')

    bar = px.pie(
        filtered_data,
        names='attendance_viz',
        title="Процент посещений",
        hole=0.5,
        labels={'attendance_viz': 'Статус'}
    )
    return bar


class DashboardView(TemplateView):
    """
    Представление "Дашборд", расширяющее админ-панель.
    Служит для отображения дашборда.
    """

    template_name = "dashboard.html"
