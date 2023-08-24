# Import libraries
import os
import glob
import numpy as np
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

    # Assign 0 to 'Value' column where Scenario is 'Higher Receipt' and Year is greater than 2085
    data.loc[(data['Scenario'] == 'Higher Receipt') & (data['Year'] > 2085), 'Value'] = 0

    # Rename years
    # Create a dictionary to map years to their corresponding range values
    year_mapping = {
    2035: "00-05", 2040: "05-10", 2045: "10-15", 2050: "15-20",
    2055: "20-25", 2060: "25-30", 2065: "30-35", 2070: "35-40",
    2075: "40-45", 2080: "45-50", 2085: "50-55", 2090: "55-60",
    2095: "60-65", 2100: "65-70", 2105: "70-75", 2109: "75-80"
    }

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
    data.loc[data['Industry'] == 'TIPU (Transportation, Information, Power and Utilities)', 'Industry'] = 'Transportation, Information, and Utilities'

    # Update industry values to group them
    industry_mapping = {
        'Service': 'Service and Trade',
        'Trade': 'Service and Trade',
        'Mining': 'Mining, Manufacturing, and Agriculture',
        'Manufacturing': 'Mining, Manufacturing, and Agriculture',
        'Agriculture': 'Mining, Manufacturing, and Agriculture'
    }

    # Create a new DataFrame to store the aggregated data
    data2 = data.copy()

    # Replace the industries to aggregate with their combined names
    for industry, combined_name in industry_mapping.items():
        data2.loc[data['Industry'] == industry, 'Industry'] = combined_name

    # Group by 'Industry', 'Year', 'Metric', 'Attribute', and 'Scenario', and then sum the 'Value' column
    data3 = data2.groupby(['Industry', 'Year', 'Metric', 'Attribute', 'Scenario'], as_index=False)['Value'].sum()

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
    data3['Example'] = data3['Industry'].map(industry_descriptions)

    # Round the 'Value' column to the nearest integer
    data3['Value'] = data3['Value'].round(2)        

    # Create lists to hold unique names of Metric, Attribute, and Scenario
    attribute = data3['Attribute'].unique().tolist()
    metric = data3['Metric'].unique().tolist()

    # Set the page title and header
    st.set_page_config(page_title="Economic Effects of Storage Facility", layout="wide")

    col1, col2, col3 = st.columns([0.5, 4, 0.5])

    # Set the page title and header with center-aligned subheader text
    with col2:
        st.markdown(
            """
            <style>
            h4 {
                font-family: 'Karla', sans-serif;
                text-align: center;
                color: #075a78; /* Set your desired color here */
            }
            </style>
            <h4>Potential Economic Effects Across the Life Cycle of an Interim Storage Facility</h4>
            """,
            unsafe_allow_html=True,
        )


    col1, col2, col3 = st.columns([1,0.75,1])

    # Create selection options
    with col2:
        metric_seletion = st.selectbox('Select an Effect',metric, index=1)
        attribute_selection = st.selectbox('Select Scale of Effect',attribute, index=0)

    data3 = data3[data3['Attribute']==attribute_selection]
    data3 = data3[data3['Metric']==metric_seletion]

    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    # Display the base case bar chart in the first column
    with col2:
        base_chart = px.bar(data3,
                            x='Value',
                            y='Industry',
                            color = 'Scenario',
                            barmode = 'group',
                            animation_frame='Year',
                            color_discrete_sequence=['rgb(7, 90, 120)','rgb(243, 110, 33)'],
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

        # Add grid lines to the x-axis and y-axis
        base_chart.update_layout(xaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1),
                                yaxis=dict(gridcolor='rgb(220, 220, 220)', gridwidth=1))
        
        base_chart.update_layout(title={'text': "Comparison between Base Case and Higher Receipt",
                                'y':0.95,
                                'x':0.5,
                                'xanchor': 'center',
                                'yanchor': 'top',})

        base_chart.update_layout(title_font_color='rgb(7, 90, 120)')
        base_chart.update_layout(title_font_size=20)

        # Change label styles
        base_chart.update_layout(xaxis=dict(title=dict(text="<b>Effect</b>",font=dict(color="rgb(7, 90, 120)",size=14))))
        base_chart.update_layout(yaxis=dict(title=dict(text="<b>Industry</b>",font=dict(color="rgb(7, 90, 120)",size=14))))

        # Sort industry names alphabetically
        base_chart.update_layout(yaxis=dict(categoryorder='category ascending'))

        # Adjust axis limits
        base_chart.update(layout_xaxis_range=[data3['Value'].min(), data3['Value'].max() + data3['Value'].max() / 50])

        # base_chart.update_layout(legend=dict(
        # orientation="v",
        # yanchor="bottom",
        # y=0.5,
        # xanchor="right",
        # x=1
        # ))

        # base_chart.update_layout(annotations=[dict(x=0.5, y=-0.32, text="(Values represent annual average impact at every 5-year interval)", font=dict(size=12),showarrow=False, xref='paper', yref='paper')])

        base_chart.update_layout(font_family="Arial", title_font_family = "Arial")
        sliders = [dict(font_size=10,font_family="Arial")]
        
        base_chart.update_layout(sliders=sliders)
        
        st.plotly_chart(base_chart, use_container_width=True)
        
if __name__ == "__main__":
    main()
