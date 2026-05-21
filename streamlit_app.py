import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Name Input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get Fruit Data (including the new SEARCH_ON column)
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(
        "Snowflake query failed. Please verify your Streamlit Snowflake connection and that the table `smoothies.public.fruit_options` exists and is accessible."
    )
    st.exception(e)
    st.stop()

if pd_df.empty:
    st.warning("No fruit options were returned from Snowflake.")
    st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothiefroot_response.ok:
            st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.error(f"Nutrition API request failed for {fruit_chosen} ({search_on}).")

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        my_insert_stmt = f"""
        insert into smoothies.public.orders
        (ingredients, name_on_order)
        values
        ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
