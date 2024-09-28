import mysql.connector
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np
import requests
from PIL import Image
from io import BytesIO

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="ananth",
    password="ananth@2000",
    database="phoneplus_db"
)
mycursor = mydb.cursor(buffered=True)

# Fetch data from database and creating as a data frame
mycursor.execute("SELECT * FROM aggregated_transaction")
Table_1 = mycursor.fetchall()
Agg_Trans = pd.DataFrame(Table_1, columns=["States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"])

mycursor.execute("SELECT * FROM aggregated_user")
Table_2 = mycursor.fetchall()
Agg_Users = pd.DataFrame(Table_2, columns=["States", "Years", "Quarter", "Brands", "Transaction_count", "Percentage"])

mycursor.execute("SELECT * FROM map_transaction")
Table_3 = mycursor.fetchall()
Map_Trans = pd.DataFrame(Table_3, columns=["States", "Years", "Quarter", "District", "Transaction_count", "Transaction_amount"])

mycursor.execute("SELECT * FROM map_user")
Table_4 = mycursor.fetchall()
Map_Users = pd.DataFrame(Table_4, columns=["States", "Years", "Quarter", "District", "Registered_Users", "App_Opens"])

mycursor.execute("SELECT * FROM top_transaction")
Table_5 = mycursor.fetchall()
Top_Trans = pd.DataFrame(Table_5, columns=["States", "Years", "Quarter", "Pincode", "Transaction_count", "Transaction_amount"])

mycursor.execute("SELECT * FROM top_users")
Table_6 = mycursor.fetchall()
Top_Users = pd.DataFrame(Table_6, columns=["States", "Years", "Quarter", "Pincode", "Registered_Users"])

# Define function for transaction amount analysis
def trans_amount_year(Agg_Trans, Year):

    # Filter transactions for the specified year
    trans = Agg_Trans[Agg_Trans["Years"] == Year]
    trans.reset_index(drop=True,inplace=True)

    # Group by state and calculate the sum of transaction count and amount
    trans_count_df = trans.groupby("States")[["Transaction_count", "Transaction_amount"]].sum()
    trans_count_df.reset_index(inplace=True)

    # Create bar chart for transaction amounts
    fig_a = px.bar(trans_count_df, x='States', y='Transaction_amount',
                   hover_data=['Transaction_amount'], color='States',
                   labels={'States': 'States', 'Transaction_amount': 'Transaction Amount'}, height=500)
    fig_a.update_layout(title={'text': f'{Year} Transaction Amount Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_a)

    # Create bar chart for transaction counts
    fig_c = px.bar(trans_count_df, x='States', y='Transaction_count',
                   hover_data=['Transaction_count'], color='States',
                   labels={'States': 'States', 'Transaction_count': 'Transaction Count'}, height=500)
    fig_c.update_layout(title={'text': f'{Year} Transaction Count Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_c)

    col1 ,col2 = st.columns(2)

    with col1:

        # Fetch the GeoJSON data for Indian states
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data = response.json()
        state_name_list = [i['properties']['ST_NM'] for i in data['features']]
        state_name_list.sort()

        # Create a choropleth map for transaction amounts
        fig_map_a = px.choropleth(
            trans_count_df,
            geojson=data,
            color="Transaction_amount",
            color_continuous_scale="Oranges",
            locations="States",
            featureidkey="properties.ST_NM",
            range_color=(trans_count_df['Transaction_amount'].min(), trans_count_df['Transaction_amount'].max()),
            hover_name="States",
            title=f'{Year} Transaction Amount',
            fitbounds="locations",
            height=600
            
        )
        fig_map_a.update_geos(fitbounds="locations", visible=False)
        fig_map_a.update_layout(title={'text': f'{Year} Transaction Amount', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_map_a)

    with col2:

        # Create a choropleth map for transaction count
        fig_map_c = px.choropleth(
            trans_count_df,
            geojson=data,
            color="Transaction_count",
            color_continuous_scale="Greens",
            locations="States",
            featureidkey="properties.ST_NM",
            range_color=(trans_count_df['Transaction_count'].min(), trans_count_df['Transaction_count'].max()),
            hover_name="States",
            title=f'{Year} Transaction Count',
            fitbounds="locations",
            height=600
            
        )
        fig_map_c.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
        fig_map_c.update_layout(title={'text': f'{Year} Transaction Count', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_map_c)

        return trans
    

def agg_transaction_type(df, state):
    # Filter the dataframe to include only the rows where the "States" column matches the selected state
    transa_p_state = df[df["States"] == state]
    transa_p_state.reset_index(drop=True, inplace=True)

     # Group the data by 'Transaction_type' and calculate the sum of 'Transaction_count' and 'Transaction_amount' for each type
    trans_type_df = transa_p_state.groupby("Transaction_type")[["Transaction_count", "Transaction_amount"]].sum()
    trans_type_df.reset_index(inplace=True)

    # Create two columns in the Streamlit app layout for side-by-side display
    col1, col2 = st.columns(2)

    # In the first column, create a pie chart for 'Transaction_amount' distribution by 'Transaction_type'
    with col1:
        fig_pie_a = px.pie(trans_type_df, values='Transaction_amount', names='Transaction_type', color='Transaction_type',height=500,width=500,
                           color_discrete_map={'Peer-to-peer payments': 'darkblue',
                                               'Recharge & bill payments': 'cyan',
                                               'Merchant payments': 'royalblue',
                                               "Others": "black",
                                               'Financial Services': 'darkblue'})
        fig_pie_a.update_layout(title={'text': f'{state} Transaction Amount Distribution', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_pie_a)

     # In the second column, create a pie chart for 'Transaction_count' distribution by 'Transaction_type'
    with col2:
        fig_pie_c = px.pie(trans_type_df, values='Transaction_count', names='Transaction_type', color='Transaction_type',height=500,width=500,
                           color_discrete_map={'Peer-to-peer payments': 'darkblue', # Assign specific colors to each transaction type
                                               'Recharge & bill payments': 'cyan',
                                               'Merchant payments': 'royalblue',
                                               "Others": "black",
                                               'Financial Services': 'darkblue'})
        fig_pie_c.update_layout(title={'text': f'{state} Transaction Count Distribution', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_pie_c)



def trans_amount_year_quarter(Agg_Trans, Quarter):
    # Filter the data to include transactions for the selected quarter
    trans_q = Agg_Trans[Agg_Trans["Quarter"] == Quarter]
    trans_q.reset_index(drop=True,inplace=True)

    # Group by state and calculate the sum of transaction count and amount
    trans_quarter_df = trans_q.groupby("States")[["Transaction_count", "Transaction_amount"]].sum()
    trans_quarter_df.reset_index(inplace=True)

    col_1, col_2 = st.columns(2)

    with col_1:

        # Create bar chart for transaction amounts
        fig_a = px.bar(trans_quarter_df, x='States', y='Transaction_amount',
                    hover_data=['Transaction_amount'], color='States',
                    labels={'States': 'States', 'Transaction_amount': 'Transaction Amount'}, height=500)
        fig_a.update_layout(title={'text': f'{trans_q["Years"].min()} Year{Quarter} Quarter Transaction Amount Analysis', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_a)

    with col_2:
        # Create bar chart for transaction counts
        fig_c = px.bar(trans_quarter_df, x='States', y='Transaction_count',
                    hover_data=['Transaction_count'], color='States',
                    labels={'States': 'States', 'Transaction_count': 'Transaction Count'}, height=500)
        fig_c.update_layout(title={'text': f'{trans_q["Years"].min()} Year{Quarter} Quarter Transaction Count Analysis', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_c)

    col_1 , col_2 = st.columns(2)

    with col_1:

        # Fetch the GeoJSON data for Indian states
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data = response.json()

        # Create a choropleth map for transaction amounts
        fig_map_a = px.choropleth(
            trans_quarter_df,
            geojson=data,
            color="Transaction_amount",
            color_continuous_scale="Oranges",
            locations="States",
            featureidkey="properties.ST_NM",
            range_color=(trans_quarter_df['Transaction_amount'].min(), trans_quarter_df['Transaction_amount'].max()),
            hover_name="States",
            title=f'{Quarter} Transaction Amount',
            fitbounds="locations",
            height=500
        )
        fig_map_a.update_geos(fitbounds="locations", visible=False)
        fig_map_a.update_layout(title={'text': f'{trans_q["Years"].min()} Year{Quarter} Quarter Transaction Amount', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_map_a)

    with col_2:
        # Create a choropleth map for transaction Count
        fig_map_c = px.choropleth(
            trans_quarter_df,
            geojson=data,
            color="Transaction_count",
            color_continuous_scale="Greens",
            locations="States",
            featureidkey="properties.ST_NM",
            range_color=(trans_quarter_df['Transaction_count'].min(), trans_quarter_df['Transaction_count'].max()),
            hover_name="States",
            title=f'{Quarter} Transaction Count',
            fitbounds="locations",
            height=500
        )
        fig_map_c.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
        fig_map_c.update_layout(title={'text': f'{trans_q['Years'].min()} Year{Quarter} Quarter Transaction Count', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_map_c)

    

def agg_users_Analysis_plot(df, year):
    # Filter DataFrame for the specified year
    agg_user_df_1 = df[df["Years"] == year].reset_index(drop=True)

    # Grouping  by Brands and sum of Transaction_count
    agg_user_df_2 = pd.DataFrame(agg_user_df_1.groupby("Brands")["Transaction_count"].sum())
    agg_user_df_2.reset_index(inplace=True)

    # Create scatter plot
    fig = px.scatter(agg_user_df_2, y="Transaction_count", x="Brands", color="Brands", symbol="Brands")
    fig.update_traces(marker_size=13)
    fig.update_layout(
        title=({'text': f'{year} Brands Transaction Analysis', 'x': 0.5, 'xanchor': 'center'}),
        plot_bgcolor='rgba(164, 64, 242, 1)',  # Transparent plot background
        paper_bgcolor='rgba(255, 255, 255, 1)',  # White paper background
    )
    st.plotly_chart(fig)

    return agg_user_df_1


def agg_user_state_Analysis_plot(df, state):

    # Filter the DataFrame to include only rows where the 'States' column matches the selected state
    agg_user_st = df[df["States"] == state]
    agg_user_st.reset_index(drop=True, inplace=True)

    # Create a bar chart using Plotly Express:
    fig = px.bar(agg_user_st, x='Brands', y='Transaction_count', hover_data=['Percentage'], color='Brands', height=500)
    fig.update_layout(title={'text': f"{state} state Brands Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig)


def agg_user_Analysis_plot_q(df, Quarter):
    
    # Filter data for the specified quarter
    agg_user_q = df[df["Quarter"] == Quarter]
    agg_user_q.reset_index(drop=True, inplace=True)

    agg_user_q_df = pd.DataFrame(agg_user_q.groupby("Brands")[["Transaction_count", "Percentage"]].sum())
    agg_user_q_df.reset_index(inplace=True)

    # Create a treemap figure
    fig = px.treemap(
        agg_user_q_df,
        path=[px.Constant("Brands"), 'Brands', 'Transaction_count'],  # Define the hierarchy of the tree
        values='Transaction_count',  # Size of the rectangles
        color='Brands',  # Color by Brands
        hover_data=['Brands'],  # Additional data to show on hover
        color_continuous_scale='RdBu',  # Color scale
        color_continuous_midpoint=np.average(df['Transaction_count'])  # Midpoint for the color scale
    )
    
    # Update the layout with specified margins
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        title={'text': f"{Quarter} Quarter Brands Analysis", 'x': 0.5, 'xanchor': 'center'}
    )  
    st.plotly_chart(fig)

def map_trans_states_to_dist(df, state):

    # Filter the DataFrame to include only rows where 'States' column matches the selected state
    transa_p_state = df[df["States"] == state]
    transa_p_state.reset_index(inplace=True)

    # Group the filtered data by 'District' and sum up both 'Transaction_count' and 'Transaction_amount' for each district
    trans_type_df = transa_p_state.groupby("District")[["Transaction_count", "Transaction_amount"]].sum()
    trans_type_df.reset_index(inplace=True)

    # Create the first bar chart (horizontal) for 'Transaction_amount':
    fig_pie_a = px.bar(trans_type_df, x="Transaction_amount", y="District", color='District', orientation='h', hover_data=["District"], height=600)
    fig_pie_a.update_layout(title={'text': f'{state} Districts Transaction_amount', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_pie_a)
    
    # Create the second bar chart (horizontal) for 'Transaction_count':
    fig_pie_c = px.bar(trans_type_df, x="Transaction_count", y="District", color='District', orientation='h', hover_data=["District"], height=600)
    fig_pie_c.update_layout(title={'text': f'{state} Districts Transaction_count', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_pie_c)


def map_users_Analysis_1(df, year):

    # Filter the DataFrame to include only rows where the 'Years' column matches the selected year
    Map_Users_df_1 = df[df["Years"] == year]
    Map_Users_df_1.reset_index(drop=True, inplace=True)

    # Group the filtered data by 'States' and sum the 'Registered_Users' and 'App_Opens' columns for each state
    Map_Users_df_2 = Map_Users_df_1.groupby("States")[["Registered_Users", "App_Opens"]].sum()
    Map_Users_df_2.reset_index(inplace=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create and display the sunburst chart for Registered Users
        fig_1 = px.sunburst(Map_Users_df_2, path=['States', 'Registered_Users'], values='Registered_Users')
        fig_1.update_layout(title={'text': f'{year} Map Registered_Users', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_1)
    
    with col2:
        # Create and display the sunburst chart for App Opens
        fig_2 = px.sunburst(Map_Users_df_2, path=['States', 'App_Opens'], values='App_Opens')
        fig_2.update_layout(title={'text': f'{year} Map App_Opens', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_2)
    
    return Map_Users_df_1

def map_user_states_to_dist(df, state):

    # Filter the dataframe for the specified state
    transa_p_state = df[df["States"] == state]
    transa_p_state.reset_index(inplace=True)
    
    # Group by district and sum the registered users and app opens
    trans_type_df = transa_p_state.groupby("District")[["Registered_Users", "App_Opens"]].sum()
    trans_type_df.reset_index(inplace=True)
    
    # create and display the bar chart for registered user
    fig1 = px.bar(trans_type_df, x="Registered_Users", y="District", color='District', orientation='h',hover_data=["District"], height=600)
    fig1.update_layout(title={'text': f'{state} Districts Registered Users Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig1)
    
    # create and display the bar chart for App open 
    fig2 = px.bar(trans_type_df, x="App_Opens", y="District", color='District', orientation='h',hover_data=["District"], height=600)
    fig2.update_layout(title={'text': f'{state} Districts App Opens Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig2)


def map_user_q(df, quarter):

    # Filter the dataframe for the specified quarter
    map_user_q = df[df["Quarter"] == quarter]
    map_user_q.reset_index(drop=True, inplace=True)

    # Group by States and sum the registered users and app opens
    Map_Users_df_2 = map_user_q.groupby("States")[["Registered_Users", "App_Opens"]].sum()
    Map_Users_df_2.reset_index(inplace=True)

    # Create two separate bar plots for Registered_Users and App_Opens
    fig = px.bar(Map_Users_df_2, x="States", y="Registered_Users", color="States", hover_data=["States"], height=600)
    fig.update_layout(title={'text': f'{map_user_q['Years'].min()} Year {quarter} Quarter Registered_Users Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig)

    fig = px.bar(Map_Users_df_2, x="States", y="App_Opens", color="States", hover_data=["States"], height=600)
    fig.update_layout(title={'text': f'{map_user_q['Years'].min()} Year {quarter} Quarter App_Opens Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig)


def top_trans_qp(df,state):
    # Filter the dataframe for the selected state
    transa_p_state = df[df["States"] == state]
    transa_p_state.reset_index(inplace=True)

    col_1 , col_2 = st.columns(2)
    # First column: display a bar chart for transaction amounts
    with col_1:
        fig = px.bar(transa_p_state, x="Quarter", y="Transaction_amount", color="Pincode",width=600,height=600)
        fig.update_layout(title={'text': f'{state} Transaction_amount analysis', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig)

    # Second column: display a bar chart for transaction counts
    with col_2:
        fig = px.bar(transa_p_state, x='Quarter', y='Transaction_count',hover_data="Pincode", color='Pincode',height=600,width=600)
        fig.update_layout(title={'text': f'{state} Transaction_count analysis', 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig)

def top_user_analysis(df, years):

    # Filter the DataFrame for the specific year
    top_user_df1 = df[df["Years"] == years]
    top_user_df1.reset_index(drop=True, inplace=True)

    # Group by 'States' and 'Quarter' and sum the 'Registered_Users'
    top_user_df2 = pd.DataFrame(top_user_df1.groupby(["States", "Quarter"])[["Registered_Users"]].sum())
    top_user_df2.reset_index(inplace=True)

    # Create a bar plot using Plotly Express
    fig = px.bar(top_user_df2, x='States', y='Registered_Users', hover_data=["States"], color='Quarter', height=600)
    fig.update_layout(title={'text': f'{years} Registered_Users analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig)

    return top_user_df1


def top_user_qp(df, state):

     # Filter the dataframe for the selected state
    top_user_s_df = df[df["States"] == state]
    top_user_s_df.reset_index(inplace=True)
    
    # Create a bar chart showing 'Registered_Users' by 'Quarter', with color based on 'Registered_Users'
    fig = px.bar(top_user_s_df, x="Quarter", y="Registered_Users", color="Registered_Users", color_continuous_scale="Turbo", hover_data=["Pincode"])
    fig.update_layout(title={'text': f'{state} Quarters Registered_Users Analysis', 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig)

def top_chart_transaction_amount(table_n):

    # Connecting to the MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="ananth",
        password="ananth@2000",
        database="phoneplus_db"
    )

    # Creating a cursor object with buffering enabled
    mycursor = mydb.cursor(buffered=True)

    # Debugging: Print the table name
    print("Table Name:", table_n)

    # Executing the SQL query for top transactions
    query_1 = f'''SELECT States, SUM(Transaction_amount) AS Transaction_amount 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_amount DESC 
                  LIMIT 10'''
    print("Query 1:", query_1)  # Debugging: Print the query
    mycursor.execute(query_1)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_1 = pd.DataFrame(datas, columns=["States", "Transaction_amount"])

    column_1 , column_2 = st.columns(2)
    with column_1:

        # Creating a bar chart using Plotly Express
        fig_0 = px.bar(df_1, x='States', y='Transaction_amount',
                    hover_data=['Transaction_amount'], color='States',
                    labels={'States': 'States', 'Transaction_amount': 'Transaction Amount'},height=500,width=500)
        fig_0.update_layout(title={'text': " Top 10 Transaction Amount", 'x': 0.5, 'xanchor': 'center'})

        # Displaying the figure
        st.plotly_chart(fig_0)

    # Executing the SQL query for bottom transactions
    query_2 = f'''SELECT States, SUM(Transaction_amount) AS Transaction_amount 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_amount 
                  LIMIT 10'''
    print("Query 2:", query_2)  # Debugging: Print the query
    mycursor.execute(query_2)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_2 = pd.DataFrame(datas, columns=["States", "Transaction_amount"])

    with column_2:

        # Creating a bar chart using Plotly Express
        fig_1 = px.bar(df_2, x='States', y='Transaction_amount',
                    hover_data=['Transaction_amount'], color='States',
                    labels={'States': 'States', 'Transaction_amount': 'Transaction Amount'},height=550,width=700)
        fig_1.update_layout(title={'text': "Last 10 Transaction Amount ", 'x': 0.5, 'xanchor': 'center'})

        # Displaying the figure
        st.plotly_chart(fig_1)

    # Executing the SQL query for average transactions
    query_3 = f'''SELECT States, AVG(Transaction_amount) AS Transaction_amount 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_amount DESC'''
    print("Query 3:", query_3)  # Debugging: Print the query
    mycursor.execute(query_3)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_3 = pd.DataFrame(datas, columns=["States", "Transaction_amount"])

    # Creating a bar chart using Plotly Express
    fig_2 = px.bar(df_3, x='Transaction_amount', y='States', orientation="h",
                   hover_data=['Transaction_amount'], color='States',
                   labels={'States': 'States', 'Transaction_amount': 'Transaction Amount'},height=800,width=1500)
    fig_2.update_layout(title={'text': "Average Transaction Amount ", 'x': 0.5, 'xanchor': 'center'})

    # Displaying the figure
    st.plotly_chart(fig_2)

def top_chart_transaction_count(table_n):

    # Connecting to the MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="ananth",
        password="ananth@2000",
        database="phoneplus_db"
    )

    # Creating a cursor object with buffering enabled
    mycursor = mydb.cursor(buffered=True)

    # Debugging: Print the table name
    print("Table Name:", table_n)

    # Executing the SQL query for top transactions
    query_1 = f'''SELECT States, SUM(Transaction_count) AS Transaction_count 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_count DESC 
                  LIMIT 10'''
    print("Query 1:", query_1)  # Debugging: Print the query
    mycursor.execute(query_1)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_1 = pd.DataFrame(datas, columns=["States", "Transaction_count"])

    column_1 , column_2 = st.columns(2)
    with column_1:

        # Creating a bar chart using Plotly Express
        fig_0 = px.bar(df_1, x='States', y='Transaction_count',
                    hover_data=['Transaction_count'], color='States',
                    labels={'States': 'States', 'Transaction_count': 'Transaction Count'},height=500,width=500)
        fig_0.update_layout(title={'text': " Top 10 Transaction Count ", 'x': 0.5, 'xanchor': 'center'})

        # Displaying the figure
        st.plotly_chart(fig_0)

    # Executing the SQL query for bottom transactions
    query_2 = f'''SELECT States, SUM(Transaction_count) AS Transaction_count 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_count 
                  LIMIT 10'''
    print("Query 2:", query_2)  # Debugging: Print the query
    mycursor.execute(query_2)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_2 = pd.DataFrame(datas, columns=["States", "Transaction_count"])

    with column_2:

        # Creating a bar chart using Plotly Express
        fig_1 = px.bar(df_2, x='States', y='Transaction_count',
                    hover_data=['Transaction_count'], color='States',
                    labels={'States': 'States', 'Transaction_count': 'Transaction Count'},height=550,width=700)
        fig_1.update_layout(title={'text': "Last 10 Transaction Count ", 'x': 0.5, 'xanchor': 'center'})

        # Displaying the figure
        st.plotly_chart(fig_1)

    # Executing the SQL query for average transactions
    query_3 = f'''SELECT States, AVG(Transaction_count) AS Transaction_count 
                  FROM {table_n} 
                  GROUP BY States 
                  ORDER BY Transaction_count DESC'''
    print("Query 3:", query_3)  # Debugging: Print the query
    mycursor.execute(query_3)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_3 = pd.DataFrame(datas, columns=["States", "Transaction_count"])

    # Creating a bar chart using Plotly Express
    fig_2 = px.bar(df_3, x='Transaction_count', y='States', orientation="h",
                   hover_data=['Transaction_count'], color='States',
                   labels={'States': 'States', 'Transaction_count': 'Transaction Count'},height=800,width=1500)
    fig_2.update_layout(title={'text': "Average Transaction Count", 'x': 0.5, 'xanchor': 'center'})

    # Displaying the figure
    st.plotly_chart(fig_2)

def map_Registered_Users(table_name,States):

    # Connecting to the MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="ananth",
        password="ananth@2000",
        database="phoneplus_db"
    )

    # Creating a cursor object with buffering enabled
    mycursor = mydb.cursor(buffered=True)

    # Executing the SQL query for top transactions
    query_1 = f'''SELECT District, SUM(Registered_Users) FROM {table_name} WHERE States = '{States}' GROUP BY District ORDER BY Registered_Users DESC limit 10;'''
    mycursor.execute(query_1)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_1 = pd.DataFrame(datas, columns=["District", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_0 = px.bar(df_1, x='District', y='Registered_Users',
                   hover_data=['Registered_Users'], color='District',
                   labels={'District': 'District', 'Registered_Users': 'Registered_Users'})
    fig_0.update_layout(title={'text': " Top 10 Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_0)
    

    # Executing the SQL query for bottom transactions
    query_2 = f'''SELECT District, SUM(Registered_Users) FROM {table_name} WHERE States = '{States}' GROUP BY District ORDER BY Registered_Users  limit 10;'''
    mycursor.execute(query_2)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_2 = pd.DataFrame(datas, columns=["District", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_1 = px.bar(df_2, x='District', y='Registered_Users',
                   hover_data=['Registered_Users'], color='District',
                   labels={'District': 'District', 'Registered_Users': 'Registered_Users'})
    fig_1.update_layout(title={'text': " Last 10 Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_1)
   


    # Executing the SQL query for average transactions
    query_3 = f'''SELECT District, AVG(Registered_Users) FROM {table_name} WHERE States = '{States}' GROUP BY District ORDER BY Registered_Users DESC;'''
    mycursor.execute(query_3)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_3 = pd.DataFrame(datas, columns=["District", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_2 = px.bar(df_3, x='Registered_Users', y='District', orientation="h",
                   hover_data=['Registered_Users'], color='District',
                   labels={'District': 'District', 'Registered_Users': 'Registered_Users'})
    fig_2.update_layout(title={'text': "Average Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_2)

def map_App_opens(table_name,States):

        # Connecting to the MySQL database
        mydb = mysql.connector.connect(
            host="localhost",
            user="ananth",
            password="ananth@2000",
            database="phoneplus_db"
        )

        # Creating a cursor object with buffering enabled
        mycursor = mydb.cursor(buffered=True)

        # Executing the SQL query for top transactions
        query_1 = query_3 = f'''SELECT District, SUM(App_Opens) as Total_App_Opens 
                FROM {table_name} 
                WHERE States = '{States}' 
                GROUP BY District 
                ORDER BY Total_App_Opens DESC 
                LIMIT 10;'''
        
        mycursor.execute(query_1)
        datas = mycursor.fetchall()

        # Creating a DataFrame from the fetched data
        df_1 = pd.DataFrame(datas, columns=["District", "App_Opens"])

        # Creating a bar chart using Plotly Express
        fig_0 = px.bar(df_1, x='District', y='App_Opens',
                    hover_data=['App_Opens'], color='District',
                    labels={'District': 'District', 'App_Opens': 'App_Opens'})
        fig_0.update_layout(title={'text': " Top 10 App_Opens Analysis", 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_0)

        # Executing the SQL query for bottom transactions
        query_2 = query_3 = f'''SELECT District, SUM(App_Opens) as Total_App_Opens 
                FROM {table_name} 
                WHERE States = '{States}' 
                GROUP BY District 
                ORDER BY Total_App_Opens 
                LIMIT 10;'''

        mycursor.execute(query_2)
        datas = mycursor.fetchall()

        # Creating a DataFrame from the fetched data
        df_2 = pd.DataFrame(datas, columns=["District", "App_Opens"])

        # Creating a bar chart using Plotly Express
        fig_1 = px.bar(df_2, x='District', y='App_Opens',
                    hover_data=['App_Opens'], color='District',
                    labels={'District': 'District', 'App_Opens': 'App_Opens'})
        fig_1.update_layout(title={'text': " Last 10 App_Opens Analysis", 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_1)

        # Executing the SQL query for average transactions
        query_3 = query_3 = f'''SELECT District, AVG(App_Opens) as Average_App_Opens 
                FROM {table_name} 
                WHERE States = '{States}' 
                GROUP BY District 
                ORDER BY Average_App_Opens DESC;'''

        mycursor.execute(query_3)
        datas = mycursor.fetchall()

        # Creating a DataFrame from the fetched data
        df_3 = pd.DataFrame(datas, columns=["District", "App_Opens"])

        # Creating a bar chart using Plotly Express
        fig_2 = px.bar(df_3, x='App_Opens', y='District', orientation="h",
                    hover_data=['App_Opens'], color='District',
                    labels={'District': 'District', 'App_Opens': 'App_Opens'},height=800,width=1500)
        fig_2.update_layout(title={'text': "Average App_Opens Analysis", 'x': 0.5, 'xanchor': 'center'})
        st.plotly_chart(fig_2)
 

def top_user_Registered(table_name):

    # Connecting to the MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="ananth",
        password="ananth@2000",
        database="phoneplus_db"
    )

    # Creating a cursor object with buffering enabled
    mycursor = mydb.cursor(buffered=True)

    # Executing the SQL query for top transactions
    query_1 = f'''SELECT States, SUM(Registered_Users) AS Total_Registered_Users
                FROM {table_name}
                GROUP BY States
                ORDER BY Total_Registered_Users DESC
                limit 10;'''
    
    mycursor.execute(query_1)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_1 = pd.DataFrame(datas, columns=["States", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_0 = px.bar(df_1, x='States', y='Registered_Users',
                   hover_data=['Registered_Users'], color='States',
                   labels={'States': 'States', 'Registered_Users': 'Registered_Users'})
    fig_0.update_layout(title={'text': " Top 10 Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_0)

    # Executing the SQL query for bottom transactions
    query_2 =  f'''SELECT States, SUM(Registered_Users) AS Total_Registered_Users
                FROM {table_name}
                GROUP BY States
                ORDER BY Total_Registered_Users
                limit 10;
                '''
    
    mycursor.execute(query_2)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_2 = pd.DataFrame(datas, columns=["States", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_1 = px.bar(df_2, x='States', y='Registered_Users',
                   hover_data=['Registered_Users'], color='States',
                   labels={'States': 'States', 'Registered_Users': 'Registered_Users'})
    fig_1.update_layout(title={'text': " Last 10 Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_1)

    # Executing the SQL query for average transactions
    query_3 = f'''SELECT States, AVG(Registered_Users) AS Avg_Registered_Users
                FROM {table_name}
                GROUP BY States
                ORDER BY Avg_Registered_Users DESC;
                '''
    
    mycursor.execute(query_3)
    datas = mycursor.fetchall()

    # Creating a DataFrame from the fetched data
    df_3 = pd.DataFrame(datas, columns=["States", "Registered_Users"])

    # Creating a bar chart using Plotly Express
    fig_2 = px.bar(df_3, x='Registered_Users', y='States', orientation="h",
                   hover_data=['Registered_Users'], color='States',
                   labels={'States': 'States', 'Registered_Users': 'Registered_Users'},height=800,width=1500)
    fig_2.update_layout(title={'text': "Average Registered_Users Analysis", 'x': 0.5, 'xanchor': 'center'})
    st.plotly_chart(fig_2)



# Streamlit configuration
st.set_page_config(layout='wide')

st.title("Phone Plus Data Exploration and Visualization")

# Sidebar configuration
with st.sidebar:
    st.image("D:/Data Science/phonepe_mainbanner2.jpg", use_column_width=True)
    st.title("Phonepe")
    menu_options = ["Home", "Data Exploration", "Top Charts", "About"]
    menu_icons = ["🏠", "🔍", "📊", "ℹ️"]
    selection = st.radio("Go to", menu_options, index=0, format_func=lambda x: f"{menu_icons[menu_options.index(x)]} {x}")

# Page content based on selection
if selection == "Home":
    st.write("Welcome to the Home page!")

    col1, col2 = st.columns(2)

    with col1:
        # Display the first set of details about the phonepe payments platform.
        st.write("""
            - **Digital Payments Platform**: Allows users to make payments, transfer money, and pay bills.
            - **Founded**: 2015
            - **Headquarters**: Bangalore, India
            - **Popular Services**: Mobile recharges, bill payments, ticket bookings.
            - **Security**: Uses advanced security features like encryption and multi-factor authentication.
            """)
            # Display the second set of details about the platform's user base, platforms, and rewards.
        st.write("""
            - **User Base**: Over 300 million users.
            - **Supported Platforms**: Available on both Android and iOS.
            - **Integration**: Integrates with various banks and financial institutions.
            - **Rewards**: Offers cashback and rewards for transactions.
            - **Customer Support**: 24/7 customer service available through the app.
            """)

    with col2:

        st.subheader("PhonePe Logo")
        st.image("D:/Project_2/1674675789998.jpeg", width=500)  # Placeholder image URL, replace with actual URL

    col_1 , col_2 = st.columns(2)

    with col_1:
    
        st.subheader("PhonePe Overview Video")# PhonePe Video
        video_url = "https://www.youtube.com/embed/6V7WbsZ9bz4"  # Embed URL format
        st.markdown(f'<iframe width="560" height="315" src="{video_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)


elif selection == "Data Exploration":
    st.write("Here you can explore data.")
    tab1, tab2, tab3 = st.tabs(["Aggregated analysis", "Map analysis", "Top analysis"])

    # First Tab: Aggregated analysis
    with tab1:

        # Dropdown to select the method, either "Aggregated Transaction" or "Aggregated usersr"
        options = st.selectbox("Select the method", ["Aggregated Transaction", "Aggregated users"], index=None, placeholder="Select contact method...")

        if options == "Aggregated Transaction":
            st.write("Aggregated Transaction selected.")

            # Dropdown for selecting year
            year_selected = st.selectbox("Select the year", Agg_Trans["Years"].unique(), index=None, placeholder="Select the year")
            agg_trans_fun = trans_amount_year(Agg_Trans, year_selected) # Function call to process data based on selected year

            column_1, column_2 = st.columns(2)

            with column_1:
                # Dropdown for selecting state
                states_1 = st.selectbox("Select the State",agg_trans_fun["States"].unique(),index=None, placeholder="Select the State")
            agg_transaction_type(agg_trans_fun,states_1) # Function to process and display transaction data based on the selected state

            column_1, column_2 = st.columns(2)

            with column_1:
                # Dropdown to select a quarter analysis
                Quarter_s = st.selectbox("Select the particular State",agg_trans_fun["Quarter"].unique(),index=None, placeholder="Select the State")
            trans_amount_year_quarter(agg_trans_fun, Quarter_s)# Function to process and display transaction data based on the selected quarter
                
        elif options == "Aggregated users":
            st.write("Aggregated users selected.")
            # Dropdown for selecting the year
            year_select = st.selectbox("Select the year", Agg_Users["Years"].unique(), index=None, placeholder="Select the year")
            Agg_user_fun = agg_users_Analysis_plot(Agg_Users,year_select) # Function call to process data for aggregated users based on selected year

            column_1 , column_2 = st.columns(2)
            with column_1:
                # Dropdown for selecting the state
              states_1 = st.selectbox("Select the State",Agg_user_fun["States"].unique(),index=None, placeholder="Select the State")
            agg_user_state_Analysis_plot(Agg_user_fun,states_1) # Function call to process data for aggregated users based on selected state


            column_1 , column_2 = st.columns(2)

            with column_1:
               # Dropdown to select a quarter for more detailed analysis
               Quarter_s = st.selectbox("Select the particular State",Agg_user_fun["Quarter"].unique(),index=None, placeholder="Select the State")
            agg_user_quart = agg_user_Analysis_plot_q(Agg_user_fun,Quarter_s) # Function call to process data for aggregated users based on selected Quarter
            

    with tab2:

        # Dropdown to select the method, either "Map Transaction" or "Map User"
        options2 = st.selectbox("Select the method", ["Map Transaction", "Map user"], index=None, placeholder="Select contact method...")

        if options2 == "Map Transaction":
            st.write("Map Transaction selected.")

            # Dropdown to select the year from the 'Map_Trans' dataframe
            year_select = st.selectbox("Select the year m_t", Map_Trans["Years"].unique(), index=None, placeholder="Select the year")
            map_trans_fun = trans_amount_year(Map_Trans, year_select)  # Function to filter data by the selected year

            column_one , column_two = st.columns(2)

            with column_one:
                # Dropdown to select a state based on the filtered transaction data
                states_1 = st.selectbox("Select the m_State",map_trans_fun["States"].unique(),index=None, placeholder="Select the State")
            map_trans_states_to_dist(map_trans_fun, states_1) # Call function to map transactions from states to districts based on selected state

            col_1 , col2 = st.columns(2)

            with col_1:
                # Dropdown to select a quarter from the filtered transaction data
                 Quarter_s = st.selectbox("Select the q_State",map_trans_fun["Quarter"].unique(),index=None, placeholder="Select the State")
            trans_amount_year_quarter(map_trans_fun, Quarter_s)  # Call function to map transactions for the selected quarter

            
        elif options2 == "Map user":
            st.write("Map User selected.")
            # Dropdown to select the year from the 'Map_Users' dataframe
            year_select = st.selectbox("Select the year_map_user", Map_Users["Years"].unique(), index=None, placeholder="Select the year")
            map_user_ret_fun  = map_users_Analysis_1(Map_Users,year_select) # Function to filter user data by the selected year

            col1 , col2 = st.columns(2)

            with col1:
                 # Dropdown to select a state based on the filtered user data
                states_1 = st.selectbox("Select the m_State",map_user_ret_fun["States"].unique(),index=None, placeholder="Select the State")
            map_user_states_to_dist(map_user_ret_fun, states_1) # Call function to map users from states to districts based on selected state

            col_1 , col2 = st.columns(2)

            with col_1:
                # Dropdown to select a quarter from the filtered user data
                 Quarter_s = st.selectbox("Select the q_State",map_user_ret_fun["Quarter"].unique(),index=None, placeholder="Select the State")
            map_user_q(map_user_ret_fun, Quarter_s)  # Call function to map users for the selected quarter


    with tab3:
        # Creating a dropdown (selectbox) for method selection with options "Top Transaction" and "Top user"
        options3 = st.selectbox("Select the method", ["Top Transaction", "Top user"], index=None, placeholder="Select contact method...")

        if options3 == "Top Transaction":
            st.write("Top Transaction selected")

            # Creating a selectbox to select a year for top transactions from the 'Years' column of Top_Trans dataframe
            year_select = st.selectbox("Select the year top_t", Top_Trans["Years"].unique(), index=None, placeholder="Select the year")
            top_trans_fun = trans_amount_year(Top_Trans, year_select)  # Calling the function trans_amount_year to filter Top_Trans by the selected year

            col1 , col2 = st.columns(2)

            with col1:
                # Creating a selectbox in the first column to select a state from the filtered top transaction data
                states_1 = st.selectbox("Select the t_State",top_trans_fun["States"].unique(),index=None, placeholder="Select the State")
            top_trans_qp(top_trans_fun,states_1)  # Calling a function top_trans_qp to perform analysis or visualization based on the selected state
            
        elif options3 == "Top user":
            st.write("Top user selected")
            year = st.selectbox("Select the year top_u", Top_Users["Years"].unique(), index=None, placeholder="Select the year")
            top_user_ret_fun = top_user_analysis(Top_Users, year) # Calling the function top_user_analysis to filter Top_Users by the selected year

            col_1 , col_2 = st.columns(2)

            with col_1:
                states = st.selectbox("Select the t_State",top_user_ret_fun["States"].unique(),index=None, placeholder="Select the State")
            top_user_qp(top_user_ret_fun,states)  # Calling a function top_user_qp to perform analysis or visualization based on the selected state
           

elif selection == "Top Charts":
    st.write("Top Charts page content here.")

    # Dropdown menu for selecting a question about transaction analysis
    Question = st.selectbox("Select the Question",["1. Transaction Amount and Count of Aggregated Transaction",
                                                    "2. Transaction Amount and Count of Map Transaction",
                                                    "3. Transaction Amount and Count of Top Transaction",
                                                    "4. Transaction Count of Aggregated User",
                                                    "5. Registered users of Map User",
                                                    "6. App opens of Map User",
                                                    "7. Registered users of Top User",
                                                    ],index=None, placeholder="Select the Question")
    

    if Question == "1. Transaction Amount and Count of Aggregated Transaction":

        st.subheader("Transation Amount analysis")
        top_chart_transaction_amount("aggregated_transaction")

        st.subheader("Transation Count analysis")
        top_chart_transaction_count("aggregated_transaction")

    elif Question == "2. Transaction Amount and Count of Map Transaction":

        st.subheader("Transation Amount analysis")
        top_chart_transaction_amount("map_transaction")

        st.subheader("Transation Count analysis")
        top_chart_transaction_count("map_transaction") 

    elif Question == "3. Transaction Amount and Count of Top Transaction":

        st.subheader("Transation Amount analysis")
        top_chart_transaction_amount("top_transaction")

        st.subheader("Transation Count analysis")
        top_chart_transaction_count("top_transaction") 
   
    elif Question == "4. Transaction Count of Aggregated User":
        st.subheader("Transation Count analysis")
        top_chart_transaction_count("aggregated_user") 

    elif Question == "5. Registered users of Map User":

        st.subheader("Registered users")
        states =st.selectbox("Select the state",Map_Users["States"].unique()) 
        map_Registered_Users("map_user",states)

    elif Question == "6. App opens of Map User":

        st.subheader("App users")
        states =st.selectbox("Select the state",Map_Users["States"].unique())
        map_App_opens("map_user",states)

    elif Question == "7. Registered users of Top User":

        st.subheader("Registered Top Users")
        top_user_Registered("top_users")


elif selection == "About":

    # # Display the title with custom font and color
    st.markdown("<h1 style='text-align: center; color: #4B0082;'>About This Project</h1>", unsafe_allow_html=True)

    # Introductory text with styled markdown
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px;">
        <p style="font-size: 18px;">
            This project focuses on visualizing and exploring data from the Phonepe Pulse repository.
            By using <b>Python</b>, <b>Streamlit</b>, and <b>Plotly</b>, it provides an interactive dashboard to gain insights
            into various metrics and statistics related to financial transactions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Using columns for better layout and icons for each technology
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🐍 Python")
        st.markdown("""
        - Data extraction, processing, and analysis.
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 🐼 Pandas")
        st.markdown("""
        - Handling and manipulating data efficiently.
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("### 🗃️ MySQL")
        st.markdown("""
        - Storing and retrieving data efficiently.
        """, unsafe_allow_html=True)

    col4, col5 = st.columns(2)

    with col4:
        st.markdown("### 📊 Plotly")
        st.markdown("""
        - Creating rich, interactive visualizations.
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("### 🌐 Streamlit")
        st.markdown("""
        - Building interactive dashboards and web apps.
        """, unsafe_allow_html=True)

    # Adding a concluding statement with custom font styling
    st.markdown("<br><p style='text-align: center; color: #4B0082; font-size: 16px;'>Enhancing data exploration and visualization for better insights.</p>", unsafe_allow_html=True)

