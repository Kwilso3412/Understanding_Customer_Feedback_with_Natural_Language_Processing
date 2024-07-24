from shiny import reactive, render, req
from shiny.express import input, render, ui
from shinyswatch import theme
from shinywidgets import render_widget
from faicons import icon_svg as icon
import pyarrow.feather as feather
import sys
import pathlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# load data
complaints_dir = pathlib.Path(__file__).parent/"datasets"/ "complaints"
review_dir = pathlib.Path(__file__).parent/"datasets" / "reviews"
image_dir = pathlib.Path(__file__).parent/ "images"
ui.page_opts(title="NLP Dashboard", fillable=True, id="page",bg = "79bde9")
theme.cyborg()
with ui.sidebar(id="sidebar_left"):
    ui.tags.link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css")
    with ui.panel_conditional("input.page == 'Time Series'"):
        ui.input_radio_buttons("time_all", "Select Category", {'num_com_top':'Number of Complaints','rev_rat_top':"Review Ratings"})
        with ui.panel_conditional("input.time_all == 'num_com_top'"):
            ui.input_select("select_complaint", "", {'num_com': 'Number of Complaints', 'serv_type':'Service Types'})
            with ui.panel_conditional("input.select_complaint == 'serv_type'"):
                ui.input_radio_buttons("select_year_serv", "", {'2024': '2024' , '2023' : '2023','2022': '2022','2021':'2021'})
        with ui.panel_conditional("input.time_all == 'rev_rat_top'"):
            ui.input_select("select_review", "", {'review_yearly': 'Overall Number of Reviews','review_monthly':'Ratings Over Time'})
            with ui.panel_conditional("input.select_review == 'review_monthly'"):
                ui.input_radio_buttons("select_year_rev", "", {'2024': '2024' , '2023' : '2023','2022': '2022','2021':'2021'})
    with ui.panel_conditional("input.page == 'Natural Language Processor'"):
        ui.input_radio_buttons("nlp_all", "Select Category", {'key_cloud':"Keyword Cloud",'rev_sent':"Review Sentiment Analysis"})
        with ui.panel_conditional("input.nlp_all == 'key_cloud'"):
            ui.input_select("keyword_cloud", "", ['Complaints', 'Reviews'],)
        with ui.panel_conditional("input.nlp_all == 'rev_sent'"):
            ui.input_select("nlp_sentiment", "Select Category", {'ovr_cent':"Overall",'by_year':"Year"})
            with ui.panel_conditional("input.nlp_sentiment == 'by_year'"):
                ui.input_radio_buttons("select_year", "", {'2024': '2024' , '2023' : '2023','2022': '2022','2021':'2021'})
def nav_content(title, body_id):
    with ui.div(class_="container mx-auto p-4", id = body_id):
        sys.displayhook(ui.h1(title, class_="text-3xl font-bold text-yellow-400 mb-4"))
time_title = "Time Series Analysis"
time_id =  "time"
with ui.nav_panel("Time Series"):
    nav_content(time_title, time_id)
    def load_complaints_count():
        return pd.read_feather(complaints_dir/"complaints_count.feather")
    complaints_count = load_complaints_count()
    with ui.panel_conditional("input.time_all == 'num_com_top'"):
        with ui.panel_conditional("input.select_complaint == 'num_com'"):
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                def number_of_complaints():
                    only_yr = complaints_count[['year','count']]
                    only_yr = only_yr.groupby(['year']).sum().reset_index()
                    fig = px.line(only_yr, x='year', y='count',
                        title='Complaints Received Over the Years',
                        labels={'year':'Year', 'count':'Number of Complaints'},
                        line_shape='linear',
                        render_mode='svg'
                        )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Year',
                        yaxis_title ='Number of Complaints',
                        font=dict(size=12),
                        xaxis=dict(showgrid=False,dtick="Y1",tickformat="%Y"),
                        yaxis=dict(showgrid=False),
                    )
                    return fig
        with ui.panel_conditional("input.select_complaint == 'serv_type'"):
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                @reactive.event(input.select_year_serv)
                def service_type_graph():
                    complaints_count['year'] = pd.to_datetime(complaints_count['year'].astype(str))
                    selected_year = input.select_year_serv()
                    year_data = complaints_count[complaints_count['year'].dt.year == int(selected_year)]
                    year_data = year_data.groupby('complaint_type')['count'].sum().reset_index().sort_values('count')
                    fig = px.bar(year_data, x='complaint_type', y='count', color='complaint_type',
                        title=f'Complaints by Service Type for {selected_year}',
                        labels={'count':'Number of Complaints', 'complaint_type':'Complaint Type'},
                        text=year_data['count'],
                        )
                    fig.update_traces(
                            texttemplate='%{text}', 
                            textposition='inside',  
                            insidetextfont=dict(color='white')  
                        )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Complaint Type',
                        yaxis_title ='Number of Complaints',
                        font=dict(size=12),
                        xaxis=dict(title='Complaint Type', showgrid=False),
                        yaxis=dict(title='Count', showgrid=False),
                        hovermode='closest',
                    )
                    return fig
    with ui.panel_conditional("input.time_all == 'rev_rat_top'"):
        def load_review_count():
            data = feather.read_feather(review_dir/"reviews_count.feather")
            dataframe = pd.DataFrame(data)
            return  dataframe       
        with ui.panel_conditional("input.select_review == 'review_yearly'"):
            review_count = load_review_count()
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                def overall_number_of_reviews():
                    overall_rev = review_count[['year','count']]
                    overall_rev = overall_rev.groupby(['year']).sum().reset_index()
                    fig = px.line(overall_rev, x='year', y='count',
                    title=f'Number of Reviews over time',
                    labels={'year':'Year', 'count':'Number of Reviews'},
                    line_shape='linear',
                    render_mode='svg'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Year',
                        yaxis_title ='Number of Reviews',
                        font=dict(size=12),
                        xaxis=dict(showgrid=False,dtick="Y1",tickformat="%Y"),
                            yaxis=dict(showgrid=False),
                        hovermode ='x unified'
                    )
                    return fig
        with ui.panel_conditional("input.select_review == 'review_monthly'"):
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                @reactive.event(input.select_year_rev)
                def number_of_reviews_by_month():
                    review_count['year'] = pd.to_datetime(review_count['year'].astype(str))
                    year = int(input.select_year_rev())
                    monthly_rev = review_count[review_count['year'].dt.year == year]
                    fig = px.line(monthly_rev, x='date', y='count',
                        title=f'Reviews for the year {year}',
                        labels={'date':'Date', 'count':'Number of Reviews'},
                        line_shape='linear',
                        render_mode='svg'
                        )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Month',
                        yaxis_title ='Number of Reviews',
                        font=dict(size=12),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False),
                        hovermode ='x unified'
                    )
                    return fig
nlp_title = "Natural Language Processing Analysis"
nlp_id  =  "nlp"
with ui.nav_panel("Natural Language Processor"):
    nav_content(nlp_title, nlp_id)
    with ui.panel_conditional("input.nlp_all == 'key_cloud'"):
        def load_complaints_keyphrases():
            return pd.read_feather(complaints_dir/"complaints_keyphrases.feather")
        #Complaints
        with ui.panel_conditional("input.keyword_cloud == 'Complaints'"):
            complaints_keyphrases = load_complaints_keyphrases()
            with ui.div(class_="pb-8 flex justify-start"):
                with ui.card(class_='bg-black text-gray-400'):
                    ui.card_header("Top 50 Key Phrases from Complaints Page", class_="text-4xl bg-black text-gray-200")
                    @render.data_frame
                    def complaints_data():
                        return render.DataGrid(complaints_keyphrases, width= 800, height=200,)
            with ui.div(class_="w-full h-full flex justify-start"):
                with ui.card(class_='bg-black text-gray-400'):
                    ui.card_header("Top 500 Keywords from Complaints Page", class_="text-4xl text-gray-200")
                    com_file = image_dir/"complaints_keyword_wordcloud.svg"
                    @render.image
                    def complaints_wordcloud():
                        svg_image = com_file
                        img = {'src': str(svg_image), 'contentType': 'image/svg+xml', "class": "w-full h-full object-contain"}
                        return img
        #Reviews
        with ui.panel_conditional("input.keyword_cloud == 'Reviews'"):
            def load_review_keyphrases():
                return pd.read_feather(review_dir/"review_keyphrases.feather")
            review_phrases = load_review_keyphrases()
            with ui.div(class_="pb-8  flex justify-start"):
                with ui.card(class_='bg-black text-gray-400'):
                    ui.card_header("Top 50 Key Phrases from Review Page", class_="text-4xl bg-black text-gray-200")
                    @render.data_frame
                    def reveiw_data():
                        return render.DataGrid(review_phrases, width= 800, height=200,)
            with ui.div(class_="w-full h-full flex justify-start"):
                with ui.card(class_='bg-black text-gray-400'):
                    ui.card_header("Top 500 Keywords from Review Page", class_="text-4xl text-gray-200")
                    rev_file = image_dir/"reviews_keyword_wordcloud.svg"
                    @render.image
                    def reviews_wordcloud():
                        svg_image = rev_file
                        img = {'src': str(svg_image), 'contentType': 'image/svg+xml', "class": "w-full h-full object-contain"}
                        return img
    with ui.panel_conditional("input.nlp_all == 'rev_sent'"):
        def load_prediction_totals():
            return pd.read_feather(review_dir/"prediction_totals.feather")
        prediction_totals = load_prediction_totals()
        with ui.layout_columns():
            with ui.value_box(showcase=icon("face-smile-beam", "regular"), class_='bg-white text-black'):
                "Positive"
                ui.p(f"{prediction_totals['total'][2]}")
            with ui.value_box(showcase=icon("face-meh", "regular"), class_='bg-white text-black'):
                "Neutral"
                ui.p(f"{prediction_totals['total'][1]}")
            with ui.value_box(showcase=icon("face-frown", "regular"), class_='bg-white text-black'):
                "Negative"
                ui.p(f"{prediction_totals['total'][0]}")
        with ui.panel_conditional("input.nlp_sentiment == 'ovr_cent'"):
            def load_sentiment_analysis():
                return pd.read_feather(review_dir/"sentiment_analysis_yr_mth.feather")
            sentiment_ana_db = load_sentiment_analysis()
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                def sentiment_time_series():
                    fig = px.line(sentiment_ana_db, x='year_month', y='count', color='predicted_class',
                        title='Time series of Predicted Classes',
                        labels={'year_month':'Month', 'count':'Number of Reviews', 'predicted_class':'Review Sentiment'},
                        line_shape='linear',
                        render_mode='svg'
                        )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Month and Year',
                        yaxis_title ='Count',
                        legend_title='Predicted Class',
                        font=dict(size=12),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False),
                        hovermode ='x unified'
                    )
                    return fig
        with ui.panel_conditional("input.nlp_sentiment == 'by_year'"):
            with ui.card(class_='bg-white text-gray-400'):
                @render_widget
                @reactive.event(input.select_year)
                def sentiment_time_series_by_year():
                    sentiment_ana_db['year'] = pd.to_datetime(sentiment_ana_db['year'].astype(str))
                    year = input.select_year()
                    data = sentiment_ana_db[sentiment_ana_db['year'].dt.year == int(year)]
                    fig = px.line(data, x='date', y='count', color='predicted_class',
                        title=f'Time Series for the year {year}',
                        labels={'date':'Date', 'count':'Number of Reviews', 'predicted_class':'Review Sentiment'},
                        line_shape='linear',
                        render_mode='svg'
                        )
                    fig.update_layout(
                        plot_bgcolor='rgba(240,240,240,1)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title ='Month',
                        yaxis_title ='Number of Reviews',
                        legend_title='Review Sentiment',
                        font=dict(size=12),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=False),
                        hovermode ='x unified'
                    )
                    return fig
ui.nav_spacer()