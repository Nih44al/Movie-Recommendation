import streamlit as st
import pandas as pd
import os
from PIL import Image

# Load the dataset with error handling
try:
    movies = pd.read_excel('movies_dataset.xlsx')
    required_columns = {'Title', 'Description', 'Language', 'Genre', 'Year', 'Rating'}
    optional_poster_columns = ['Image_Path', 'Poster', 'Poster_Path', 'Poster_URL']
    
    # Find the actual poster column name in the dataset
    poster_column = next((col for col in optional_poster_columns if col in movies.columns), None)
    if poster_column:
        movies.rename(columns={poster_column: 'Poster_Path'}, inplace=True)
    else:
        movies['Poster_Path'] = None  # If no poster column exists, create an empty one

    if not required_columns.issubset(movies.columns):
        st.error("Dataset is missing required columns!")
        st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Filter dataset to only include movies between 2014 and 2024
movies = movies[(movies['Year'] >= 2014) & (movies['Year'] <= 2024)]

# Standardize Language and Genre to remove redundancies
movies['Language'] = movies['Language'].str.strip().str.title()
movies['Genre'] = movies['Genre'].str.strip().str.title()

# Remove duplicates while keeping only necessary columns for filtering
movies = movies.drop_duplicates(subset=['Title', 'Language', 'Genre', 'Year', 'Rating'])

# Get unique values for Language and Genre dropdowns after standardization
language_options = sorted(movies['Language'].dropna().unique())
genre_options = sorted(movies['Genre'].dropna().unique())

# Set Streamlit page config
st.set_page_config(page_title="Movie Recommendation", layout="wide")

# Sidebar filters with collapsible section
with st.sidebar.expander("🔍 **Adjust Filters (Click to Expand)**", expanded=True):
    language_filter = st.selectbox('Select Language', language_options)
    genre_filter = st.selectbox('Select Genre', genre_options)
    year_filter = st.selectbox('Select Year', sorted(movies['Year'].dropna().unique()))
    rating_filter = st.slider('Select Maximum Rating', 0.0, 10.0, 10.0)

# Filter dataset based on selections
filtered_movies = movies[
    (movies['Language'] == language_filter) &
    (movies['Genre'] == genre_filter) &
    (movies['Year'] == year_filter) &
    (movies['Rating'] <= rating_filter)
]

if filtered_movies.empty:
    st.write("No movies found based on the selected filters. Try adjusting your filters.")
    st.stop()

# Function to resolve the full poster path
def get_poster_path(poster_path):
    if pd.notna(poster_path):
        corrected_path = poster_path.replace('poster/', 'posters/')  # Fix incorrect folder name
        full_path = os.path.join(os.getcwd(), corrected_path)  # Resolve relative to script location
        if os.path.exists(full_path):
            return full_path
    return None

# Function to display recommendations
def show_recommendations(selected_movie):
    st.subheader("Selected Movie:")
    st.write(f"**{selected_movie['Title']}**")
    st.write(selected_movie['Description'])
    
    # Load and display the selected movie's poster
    poster_path = get_poster_path(selected_movie['Poster_Path'])
    if poster_path:
        st.image(Image.open(poster_path), caption=selected_movie['Title'], width=200)
    else:
        st.write("No poster available.")

    # Display recommended movies
    st.subheader("Recommended Movies:")
    recommendations = movies[
        (movies['Title'] != selected_movie['Title']) &
        (movies['Language'] == selected_movie['Language']) &
        (movies['Genre'] == selected_movie['Genre'])
    ].sample(min(3, len(movies)), random_state=42)  # Select up to 3 recommendations
    
    if recommendations.empty:
        st.write("No recommendations available.")
    else:
        for _, movie in recommendations.iterrows():
            st.write(f"**{movie['Title']}**")
            st.write(movie['Description'])
            rec_poster_path = get_poster_path(movie['Poster_Path'])
            if rec_poster_path:
                st.image(Image.open(rec_poster_path), caption=movie['Title'], width=150)
            else:
                st.write("No poster available.")

# Automatically select the first movie from filtered results if available
selected_movie = filtered_movies.iloc[0]
show_recommendations(selected_movie)
