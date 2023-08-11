# Import libraries
import os
import glob
import pandas as pd
import plotly.express as px
import streamlit as st

def main():
    # Locate the files in the appropriate directory
    path = './Adrienne_Data/'
    files = glob.glob(path+'/*.csv')

    # Load the data and join them
    data = []
    for file in files:
        df = pd.read_csv(file,index_col=None,header=0)
        data.append(df)
    data = pd.concat(data,axis=0,ignore_index=True)

    # Clean the data
    data.drop(['Unnamed: 0'],axis=1,inplace=True) # Redundant column

    # Filter rows where 'Attribute' is either 'Direct' or 'Total'
    data = data[data['Attribute'].isin(['Direct', 'Total'])]

    # Rename years
    # Create a dictionary to map years to their corresponding values
    # Create a dictionary to map years to their corresponding range values
    year_mapping = {
    2035: "0-05", 2040: "05-10", 2045: "10-15", 2050: "15-20",
    2055: "20-25", 2060: "25-30", 2065: "30-35", 2070: "35-40",
    2075: "40-45", 2080: "45-50", 2085: "50-55", 2090: "55-60",
    2095: "60-65", 2100: "65-70", 2105: "70-75", 2109: "75-80"
    }

    # year_mapping = {
    #     2035: 0, 2040: 5, 2045: 10, 2050: 15,
    #     2055: 20, 2060: 25, 2065: 30, 2070: 35,
    #     2075: 40, 2080: 45, 2085: 50, 2090: 55,
    #     2095: 60, 2100: 65, 2105: 70, 2109: 75
    # }

    # Apply the year mapping using the replace method
    data["Year"] = data["Year"].replace(year_mapping)

    # Remove the numbers from the metrics column
    data['Metric'] = data['Metric'].str.slice(start=2)

    # Rename and select metrics
    data['Metric'] = data['Metric'].replace({'Employment': 'Number of Jobs',
                                            'LaborIncome':'Labor Income ($)',
                                            'Output':'Total Production Value ($)'})
    data = data[data["Metric"].isin(["Number of Jobs", "Labor Income ($)", "Total Production Value ($)"])]

    # Rename industries
    data['Industry'] = data['Industry'].replace({'TIPU (Transportation, Information, Power and Utilities)':'Transportation, Information, and Utilities'})

    # Update industry values to group them
    industry_mapping = {
        'Service': 'Service and Trade',
        'Trade': 'Service and Trade',
        'Mining': 'Mining, Manufacturing, and Agriculture',
        'Manufacturing': 'Mining, Manufacturing, and Agriculture',
        'Agriculture': 'Mining, Manufacturing, and Agriculture'
    }

    # Apply the industry mapping using the replace method
    data['Industry'] = data['Industry'].replace(industry_mapping)

    # Group by 'Industry', 'Year', 'Metric', 'Attribute', and 'Scenario', and then sum the 'Value' column
    data = data.groupby(['Industry', 'Year', 'Metric', 'Attribute', 'Scenario'])['Value'].sum().reset_index()

    # Group the data by the "Scenario" column
    grouped_data = data.groupby('Scenario')

    # Create a dictionary to store the separate DataFrames
    dataframes_by_scenario = {}

    # Iterate through the groups and create separate DataFrames
    for scenario, group in grouped_data:
        dataframes_by_scenario[scenario] = group.copy()

    # Access the separate DataFrames using the keys "Base Case" and "Higher Receipt"
    base_case = dataframes_by_scenario['Base Case']
    higher_receipt = dataframes_by_scenario['Higher Receipt']

    # Create a dictionary to store industry descriptions
    industry_descriptions = {
        'Transportation, Information, and Utilities':
                'Example: Air and ground transportation, internet service,<br>telephone and satellite communications, publishing, power<br>generation and distribution, water treatment and distribution',
        'Service and Trade':
                'Example: Health care, performing arts, professional<br>services, retail and wholesale businesses',
        'Mining, Manufacturing, and Agriculture':
                'Example: Coal and metals mining, oil and gas production,<br>materials and goods manufacturing, beverage production,<br>bakeries, farming, forestry',
        'Government':
                'Example: Federal, local, and state government agencies,<br>including education, military, transit, and public health',
        'Construction':
                'Example: Commercial and residential structures,<br>road construction and maintenance, power and<br>communication structures'
    }
    # Update 'Description' column for base_case DataFrame
    base_case['Example'] = base_case['Industry'].map(industry_descriptions)

    # Update 'Description' column for higher_receipt DataFrame
    higher_receipt['Example'] = higher_receipt['Industry'].map(industry_descriptions)

    # Round the 'Value' column to the nearest integer
    base_case['Value'] = base_case['Value'].round(2)        
    higher_receipt['Value'] = higher_receipt['Value'].round(2)

    # Create lists to hold unique names of Metric, Attribute, and Scenario
    attribute = base_case['Attribute'].unique().tolist()
    metric = base_case['Metric'].unique().tolist()

    # Set the page title and header
    st.set_page_config(page_title="Economic Effects of Storage Facility", layout="wide")

    col1, col2, col3 = st.columns([1, 2, 1])

    # Set the page title and header with center-aligned subheader text
    with col2:
        st.markdown(
            """
            <style>
            h3 {
                font-family: 'Karla', sans-serif;
                text-align: center;
            }
            </style>
            <h3>Potential Economic Effects across the Life Cycle of a Storage Facility</h3>
            """,
            unsafe_allow_html=True,
        )


    col1, col2, col3 = st.columns([2,1,2])

    # Create selection options
    with col2:
        metric_seletion = st.selectbox('Select an Effect',metric)
        attribute_selection = st.selectbox('Select Scale of Effect',attribute)

    base_case = base_case[base_case['Attribute']==attribute_selection]
    base_case = base_case[base_case['Metric']==metric_seletion]

    higher_receipt = higher_receipt[higher_receipt['Attribute']==attribute_selection]
    higher_receipt = higher_receipt[higher_receipt['Metric']==metric_seletion]

    # Create two columns for the plots
    col1, col2, col3, col4, col5 = st.columns([0.25,3,0.15,3,0.5],gap='small')
    # col1, col2 = st.columns(2,gap='large')

    # Display the higher receipt bar chart in the second column
    with col4:
        higher_chart = px.bar(higher_receipt,
                            x='Value',
                            y='Industry',
                            animation_frame='Year',
                            color_discrete_sequence=['rgb(14, 166, 223)'],
                            # 14, 166, 223; 7, 90, 120; 0, 127, 113; 122, 197, 67; 247, 227, 208; 243, 110, 33; 156, 28, 74
                            orientation='h',
                            template="seaborn",
                            height=400,
                            width=500,
                            # hover_data= ['Example'],
                            hover_name= 'Example'
                            )

        higher_chart.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=10,
                font_family="Arial",
            )
        )

        # # Customize hover template to control shape and appearance of the hover box
        # hover_template = (
        #     "<b>Example</b>: %{customdata[0]}<extra></extra>")
        # higher_chart.update_traces(hovertemplate=hover_template)

        # Add grid lines to the x-axis and y-axis
        higher_chart.update_layout(
            xaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1),
            yaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1)
        )

        # Add grid lines to the x-axis and y-axis
        higher_chart.update_layout(xaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1),
                                yaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1))
        
        higher_chart.update_layout(title={'text': "Higher Receipt Rate",
                                'y':0.95,
                                'x':0.55,
                                'xanchor': 'center',
                                'yanchor': 'top',})

        higher_chart.update_layout(title_font_color='rgb(7, 90, 120)')
        higher_chart.update_layout(title_font_size=20)

        # Change label styles
        higher_chart.update_layout(xaxis=dict(title=dict(text="<b>Value</b>",font=dict(color="rgb(14, 166, 223)",size=12))))
        higher_chart.update_layout(yaxis=dict(title=dict(text="<b>Industry</b>",font=dict(color="rgb(14, 166, 223)",size=12))))

        # Sort industry names alphabetically
        higher_chart.update_layout(yaxis=dict(categoryorder='category ascending'))

        # Adjust axis limits
        higher_chart.update(layout_xaxis_range=[higher_receipt['Value'].min(), higher_receipt['Value'].max() + higher_receipt['Value'].max() / 20])

        # higher_chart.update_layout(annotations=[dict(x=0.5, y=-0.32, text="(Values represent annual average impact at every 5-year interval)", font=dict(size=12),showarrow=False, xref='paper', yref='paper')])

        higher_chart.update_layout(font_family="Arial", title_font_family = "Arial")

        st.plotly_chart(higher_chart, use_container_width=True)

    # Display the base case bar chart in the first column
    with col2:
        base_chart = px.bar(base_case,
                            x='Value',
                            y='Industry',
                            animation_frame='Year',
                            color_discrete_sequence=['rgb(14, 166, 223)'],
                            # 14, 166, 223; 7, 90, 120; 0, 127, 113; 122, 197, 67; 247, 227, 208; 243, 110, 33; 156, 28, 74
                            orientation='h',
                            template="seaborn",
                            height=400,
                            width=500,
                            hover_name= 'Example',
                            )

        base_chart.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=10,
                font_family="Arial"
            )
        )
        # # Customize hover template to control shape and appearance of the hover box
        # hover_template = (
        #     "<b>Example</b>: %{customdata[0]}<extra></extra>")
        # base_chart.update_traces(hovertemplate=hover_template)

        # Add grid lines to the x-axis and y-axis
        base_chart.update_layout(xaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1),
                                yaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1))
        
        base_chart.update_layout(title={'text': "Base Case",
                                'y':0.95,
                                'x':0.55,
                                'xanchor': 'center',
                                'yanchor': 'top',})

        base_chart.update_layout(title_font_color='rgb(7, 90, 120)')
        base_chart.update_layout(title_font_size=20)

        # Change label styles
        base_chart.update_layout(xaxis=dict(title=dict(text="<b>Value</b>",font=dict(color="rgb(14, 166, 223)",size=12))))
        base_chart.update_layout(yaxis=dict(title=dict(text="<b>Industry</b>",font=dict(color="rgb(14, 166, 223)",size=12))))

        # Sort industry names alphabetically
        base_chart.update_layout(yaxis=dict(categoryorder='category ascending'))

        # Adjust axis limits
        base_chart.update(layout_xaxis_range=[higher_receipt['Value'].min(), higher_receipt['Value'].max() + higher_receipt['Value'].max() / 20])

        # base_chart.update_layout(annotations=[dict(x=0.5, y=-0.32, text="(Values represent annual average impact at every 5-year interval)", font=dict(size=12),showarrow=False, xref='paper', yref='paper')])

        base_chart.update_layout(font_family="Arial", title_font_family = "Arial")

        st.plotly_chart(base_chart, use_container_width=True)

if __name__ == "__main__":
    main()
