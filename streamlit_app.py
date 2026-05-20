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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
 
# Convert the Snowpark Dataframe to a Pandas Dataframe
pd_df = my_dataframe.to_pandas()
 
# Multiselect using the FRUIT_NAME column from our Pandas Dataframe
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)
 
# Insert Order and API Loop
if ingredients_list:
    ingredients_string = ''
 
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        # Look up the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )
 
    my_insert_stmt = f"""
    insert into smoothies.public.orders
    (ingredients, name_on_order)
    values
    ('{ingredients_string}', '{name_on_order}')
    """
 
    time_to_insert = st.button('Submit Order')
 
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")




    
# # Import python packages.
# import streamlit as st
# import requests

# from snowflake.snowpark.functions import col

# # Write directly to the app.
# cnx = st.connection("snowflake")

# st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

# st.write("Choose the fruits you want in your smoothie")

# session = cnx.session()

# name_on_order = st.text_input('Name on Smoothie:')

# st.write('The name on the smoothie will be:', name_on_order)

# my_dataframe = (
#     session.table("smoothies.public.fruit_options")
#     .select(col('FRUIT_NAME'),col('SEARCH_ON'))
# )

# fruit_rows = my_dataframe.collect()

# fruit_options = {
#     row["FRUIT_NAME"]: row["SEARCH_ON"]
#     for row in fruit_rows
# }

# fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# ingredients_list = st.multiselect(
#     "Choose upto 5 ingredients",
#     #fruit_list,
#     list(fruit_options.keys()),
#     max_selections=5,
# )

# if ingredients_list:

#     ingredients_string = ''

#     for fruit_chosen in ingredients_list:

#         ingredients_string += fruit_chosen + ' '

#         st.subheader(fruit_chosen + ' Nutrition Information')

#         search_on = fruit_options[fruit_chosen]

#         smoothiefroot_response = requests.get(
#             "https://www.smoothiefroot.com/api/fruit/" + search_on
#         )

#         st.text(smoothiefroot_response.text)

#         st.dataframe(
#             data=smoothiefroot_response.json(),
#             use_container_width=True
#         )

#     my_insert_stmt = f"""
#         insert into smoothies.public.orders
#         (ingredients, name_on_order)
#         values
#         ('{ingredients_string}', '{name_on_order}')
#     """

#     time_to_insert = st.button('Submit Order')

#     if time_to_insert:

#         session.sql(my_insert_stmt).collect()

#         st.success(
#             f'Your Smoothie is ordered! {name_on_order}!',
#             icon="✅"
#         )