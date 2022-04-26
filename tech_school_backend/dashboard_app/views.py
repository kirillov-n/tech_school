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
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash

queryset = Grade.objects.all().values()
groups = Group.objects.all().values()
membership = Membership.objects.all().values()
incp = InCP.objects.all().values()
calplan = CalendarPlan.objects.all().values()

df_grades = pd.DataFrame(queryset)
df_groups = pd.DataFrame(groups)
df_membership = pd.DataFrame(membership)
df_incp = pd.DataFrame(incp)
df_calplan = pd.DataFrame(calplan)

df = pd.merge(df_grades[['grade_type', 'grade', 'attendance', 'student_id']], df_membership[['group_id', 'student_id']], left_on='student_id', right_on='student_id')
df = pd.merge(df, df_groups[['id', 'name', 'program_id']], left_on='group_id', right_on='id')
df_ = pd.merge(df_incp[['calendarplan_id', 'program_id']], df_calplan[['id', 'year']], left_on='calendarplan_id', right_on='id')
df = pd.merge(df, df_, left_on='program_id', right_on='program_id')


class DashboardView(TemplateView):
    """
    Представление "Дашборд", расширяющее админ-панель.
    Служит для отображения дашборда.
    """

    template_name = "dashboard.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context.update(site.each_context(self.request))
    #
    #     context["headings1"] = [  # таблица средних баллов
    #         'студент',
    #         'предмет',
    #         'средний балл',
    #     ]
    #
    #     context["headings2"] = [  # таблица посещаемости
    #         'студент',
    #         'предмет',
    #         'present',
    #         'absent',
    #         '% present',
    #     ]
    #
    #     context["headings3"] = [  # таблица totals
    #         'студент',
    #         'часов посетил',
    #         'всего часов',
    #         '% часов',
    #         'средние оценки',
    #         'среднее по всем оценкам'
    #     ]
    #
    #     date = self.request.GET.get("date")
    #     group = self.request.GET.get("group")
    #
    #     groups = Group.objects.all()  # все группы
    #     context["groups"] = groups
    #
    #     queryset = Grade.objects.all()  # queryset: все оценки

    # queryset = Grade.objects.all().values()
    # groups = Group.objects.all().values()
    # membership = Membership.objects.all().values()
    #
    # df_grades = pd.DataFrame(queryset)
    # df_groups = pd.DataFrame(groups)
    # df_membership = pd.DataFrame(membership)
    #
    # df = pd.merge(df_grades, df_membership, left_on='student_id', right_on='student_id')
    # df = pd.merge(df, df_groups, left_on='group_id', right_on='id')

    def generate_table(dataframe, max_rows=10):
        return html.Table(
            # Header
            [html.Tr([html.Th(col) for col in dataframe.columns])] +

            # Body
            [html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))]
        )

    # df = pd.read_csv(r"C:\Users\kiril\Desktop\pBNN\Data\result_table.csv", delimiter=";").copy()

    # df_people = df[['name', 'group']].groupby('group').count().rename(columns={"name": "people"}).reset_index()
    #
    # fig = px.pie(df_people, values='people', names='group', title='Количество студентов в группах')

    # df_question1 = df[['name', 'stud_1']].groupby('stud_1').count().rename(columns={"name": "people"}).reset_index()
    #
    # fig_1 = px.bar(df_question1, x='stud_1', y='people', title='Первый вопрос')
    #
    # df_question2 = df[['name', 'stud_2']].groupby('stud_2').count().rename(columns={"name": "people"}).reset_index()
    #
    # fig_2 = px.bar(df_question2, x='stud_2', y='people', title='Второй вопрос')

    fig_grades = px.bar(df[df["grade_type"] == 'g'], x='grade', y='student_id', title='Оценки')

    # table = go.Figure(data=[go.Table(header=dict(values=list(df.columns),
    #                                              fill_color='paleturquoise',
    #                                              align='left'),
    #                                  cells=dict(values=[df.Rank, df.State, df.Postal, df.Population],
    #                                             fill_color='lavender',
    #                                             align='left'))])

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = DjangoDash('dashboard', external_stylesheets=external_stylesheets)

    app.layout = html.Div(
        children=[
            html.Div(children='group', style={'fontSize': "24px"}, className='menu-title'),
            dcc.Dropdown(
                id='group-filter',
                options=[
                    {'label': group, 'value': group}
                    for group in df.name.unique()
                ],
                # multi=True,
                value='M-227',
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
                        children=generate_table(df)
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
        filtered_data = df[df["name"] == group]

        bar = px.bar(
            filtered_data,
            x='grade',
            y='student_id',
            title='Оценки',
        )
        return bar
    #
    # @app.callback(
    #     Output("bar_2", "figure"),
    #     [Input("group-filter", "value")],
    # )
    # def update_charts(group):
    #     df = pd.read_csv(r"C:\Users\kiril\Desktop\pBNN\Data\result_table.csv", delimiter=";").copy()
    #     filtered_data = df[df["group"] == group]
    #     filtered_data = filtered_data[['name', 'stud_2']].groupby('stud_2').count().rename(
    #         columns={"name": "people"}).reset_index()
    #
    #     bar = px.bar(
    #         filtered_data,
    #         x='stud_2',
    #         y='people',
    #         title='Второй вопрос',
    #     )
    #     return bar
