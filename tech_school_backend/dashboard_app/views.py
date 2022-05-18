from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics, viewsets, status
from django.views.generic import TemplateView
from django.contrib.admin.sites import site
from django.db.models import Avg, Count, Q, Sum
from tech_school_app.models import *

import dash_table
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from datetime import date

grades = Grade.objects.all().values()
groups = Group.objects.all().values()
membership = Membership.objects.all().values()
incp = InCP.objects.all().values()
calplan = CalendarPlan.objects.all().values()
personalinfo = PersonalInfo.objects.all().values()
students = Student.objects.all().values()
_class = Class.objects.all().values()

df_grades = pd.DataFrame(grades)
df_groups = pd.DataFrame(groups)
df_membership = pd.DataFrame(membership)
df_incp = pd.DataFrame(incp)
df_calplan = pd.DataFrame(calplan)
df_class = pd.DataFrame(_class)

df_personalinfo = pd.DataFrame(personalinfo)
df_personalinfo['FullName'] = df_personalinfo['surname'] + ' ' + df_personalinfo['name'] + ' ' + df_personalinfo[
    'patronymic']
df_students = pd.DataFrame(students)

df = pd.merge(df_grades[['grade_type', 'grade', 'attendance', 'student_id', 'class_id_id']],
              df_membership[['group_id', 'student_id']],
              left_on='student_id', right_on='student_id')
df = pd.merge(df, df_class[['id', 'when']], left_on='class_id_id', right_on='id')
df = pd.merge(df, df_groups[['id', 'name', 'program_id']], left_on='group_id', right_on='id')
df = pd.merge(df, df_students[['id', 'personal_info_id', 'personnel_num']], left_on='student_id', right_on='id')
df = pd.merge(df, df_personalinfo[['id', 'FullName']], left_on='personal_info_id', right_on='id')
# print(df)
# df.to_csv('out.csv', index=False)
df['when'] = pd.to_datetime(df['when']).dt.date
students_list = df[['personnel_num', 'group_id', 'FullName']].drop_duplicates(subset=['personnel_num'])
students_list = students_list.rename(columns={"personnel_num": "Табельный номер", "FullName": "ФИО"})

df_g = df[df["grade_type"] == 'g']

fig_grades = px.bar(df_g, x=df_g['grade'].value_counts().index, y=df_g['grade'].value_counts().values.tolist(),
                    title='Оценки')
pie_attendance = px.pie(df[df["grade_type"] == 'a'], names="attendance", title="Процент посещений", hole=0.5)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = DjangoDash('dashboard', external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.Div(children='Выберите группу',
                 style={'display': 'block', 'fontSize': "24px", 'margin-bottom': '5px', 'margin-top': '0px',
                        'color': 'rgb(42, 63, 95)'},
                 className='menu-title'),
        html.Div(
            dcc.Dropdown(
                id='group-filter',
                options=[
                    {'label': group_name, 'value': group}
                    for group in df.group_id.unique()
                    for group_name in df[df['group_id'] == group].name.unique()
                ],
                className='dropdown',
                placeholder='Группа',
            ), style={'width': '100%', 'display': 'block', 'margin-bottom': '5px', 'vertical-align': 'top'}),
        html.Div(
            dcc.DatePickerRange(
                id='my-date-picker-range',
                display_format='DD.MM.YYYY',
                start_date_placeholder_text='Начальная дата',
                end_date_placeholder_text='Конечная дата',
                start_date=date.today(),
                end_date=date.today(),
                first_day_of_week=1,
                show_outside_days=True,
                number_of_months_shown=2,
            ), style={'width': '100%', 'display': 'block', 'margin-bottom': '5px', 'vertical-align': 'top'}),

        html.Div(
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in students_list[['Табельный номер', 'ФИО']]],
                data=students_list.to_dict('records'),
                style_cell_conditional=[
                    {
                        'textAlign': 'left',
                    }
                ],
                style_table={
                    'border': '1px solid white',
                    'borderRadius': '10px',
                    'overflow': 'hidden'
                },
                style_header={
                    'border': '1px solid white',
                    'backgroundColor': 'rgb(75, 113, 171)',
                    'color': 'rgb(19, 29, 44)',
                    'fontWeight': 'bold'
                },
                style_data={
                    'border': '1px solid white',
                    'color': 'rgb(42, 63, 95)',
                    'backgroundColor': 'rgb(229, 236, 246)'
                },
            ), style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='bar_1',
                        figure=fig_grades
                    ), style={'display': 'block'}
                ),
                html.Div(
                    children=dcc.Graph(
                        id='pie_attendance',
                        figure=pie_attendance
                    ), style={'display': 'block'}
                )
            ], style={'width': '70%', 'display': 'inline-block'}
        )
    ]
)


@app.callback(
    Output("bar_1", "figure"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("group-filter", "value"))
def update_charts(start_date, end_date, value):
    start_date_object = pd.to_datetime(start_date)
    end_date_object = pd.to_datetime(end_date)

    filtered_data = df[df["group_id"] == value]
    filtered_data = filtered_data[filtered_data["grade_type"] == 'g']
    filtered_data = filtered_data[
        (filtered_data["when"] > start_date_object) & (filtered_data['when'] < end_date_object)]
    # data = filtered_data['grade'].value_counts()
    # filtered_df = pd.DataFrame(data).reset_index()
    # filtered_df.columns = ['grade', 'amount']

    grade_groups = filtered_data[["FullName", "grade"]].groupby('grade')['FullName'].apply(list)
    df_grade_groups = pd.DataFrame(grade_groups).reset_index()
    if not df_grade_groups['FullName'].empty:
        df_grade_groups['amount'] = df_grade_groups['FullName'].str.len()
    else:
        df_grade_groups['amount'] = 0
    bar = px.bar(
        df_grade_groups,
        x='grade',
        y='amount',
        hover_data=['FullName'],
        orientation='v',
        labels={'FullName': 'Судент(ы)',
                'grade': 'Оценка',
                'amount': 'Количество оценок',
                'student_id': 'ID',
                'personnel_num': 'Табельный номер'},
        title='Оценки',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    bar.update_layout(margin=dict(t=25))
    bar.update_layout(legend=dict(font=dict(size=10)))
    bar.update_traces(marker_line_color='rgb(69, 38, 43)', marker_line_width=1.5)
    bar.update_xaxes(dtick=1)
    bar.update_yaxes(dtick=1)
    return bar


@app.callback(
    Output("pie_attendance", "figure"),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input("group-filter", "value"))
def update_charts(start_date, end_date, value):
    start_date_object = pd.to_datetime(start_date)
    end_date_object = pd.to_datetime(end_date)
    filtered_data = df[df["group_id"] == value]
    filtered_data = filtered_data[filtered_data["grade_type"] == 'a']
    filtered_data = filtered_data[
        (filtered_data["when"] > start_date_object) & (filtered_data['when'] < end_date_object)]
    filtered_data['attendance_viz'] = np.where(filtered_data['attendance'] == '0', 'Пропуск', 'Посещение')

    bar = px.pie(
        filtered_data,
        names='attendance_viz',
        title="Процент посещений",
        hole=0.5,
        labels={'attendance_viz': 'Статус'},
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    bar.update_layout(margin=dict(t=25), showlegend=False)
    bar.update_traces(textinfo='percent+label', marker_line_width=1.5, marker_line_color='rgb(69, 38, 43)')
    return bar


@app.callback(
    Output("table", "data"),
    Input("group-filter", "value"))
def update_graphs(value):
    filtered_data = students_list[students_list["group_id"] == value]
    return filtered_data.to_dict('records')


class DashboardView(TemplateView):
    """
    Представление "Дашборд", расширяющее админ-панель.
    Служит для отображения дашборда.
    """

    template_name = "dashboard.html"
