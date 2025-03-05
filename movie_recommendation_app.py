import streamlit as st
import pandas as pd
import os
from PIL import Image

# Set Streamlit page config
st.set_page_config(page_title="Movie Recommendation", layout="wide")

# Apply custom CSS to keep default mouse pointer everywhere
st.markdown(
    """
    <style>
        /* Force default pointer everywhere, including dropdowns */
        * { cursor: default !important; }

        /* Restore pointer for interactive elements */
        input, select, textarea, button, [role="button"] {
            cursor: pointer !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Load the dataset with error handling
try:
    movies = pd.read_excel('movies_dataset.xlsx')
    required_columns = {'Title', 'Description', 'Language', 'Genre', 'Year', 'Rating', 'Image_Path'}

    if not required_columns.issubset(movies.columns):
        st.error("Dataset is missing required columns!")
        st.stop()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Fix incorrect poster paths
movies['Image_Path'] = movies['Image_Path'].str.replace('poster/', 'posters/', regex=False)
movies['Image_Path'] = movies['Image_Path'].str.replace(r'_\.jpg$', '.jpg', regex=True)  # Fix extra underscores

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

# Sidebar filters with collapsible section
with st.sidebar.expander("🔍 *Adjust Filters (Click to Expand)*", expanded=True):
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
    st.warning("⚠ No movies found based on the selected filters. Try adjusting your filters.")
    st.stop()

# Function to resolve the full poster path
def get_poster_path(poster_path):
    """Returns the full path of the poster if available, else returns a default placeholder."""
    default_image = os.path.join("posters", "default.jpg")  # Default poster

    if pd.notna(poster_path):
        full_path = os.path.join(os.getcwd(), poster_path)  # Use the dataset's path as is
        if os.path.exists(full_path):
            return full_path

    return default_image if os.path.exists(default_image) else None  # Use default if missing

# Function to display recommendations
def show_recommendations(selected_movie):
    st.subheader("🎬 Selected Movie:")
    st.write(f"{selected_movie['Title']} ({selected_movie['Year']}, {selected_movie['Rating']}/10)")
    st.write(selected_movie['Description'])

    # Load and display the selected movie's poster
    poster_path = get_poster_path(selected_movie['Image_Path'])  # Use Image_Path column
    if poster_path:
        st.image(Image.open(poster_path), caption=selected_movie['Title'], width=200)
    else:
        st.warning("🚨 Poster not available!")

    # Display recommended movies
    st.subheader("✨ Recommended Movies:")
    recommendations = movies[
        (movies['Title'] != selected_movie['Title']) &
        (movies['Language'] == selected_movie['Language']) &
        (movies['Genre'] == selected_movie['Genre'])
    ].sample(min(3, len(movies)), random_state=42)  # Select up to 3 recommendations
    
    if recommendations.empty:
        st.write("No recommendations available.")
    else:
        for _, movie in recommendations.iterrows():
            st.write(f"{movie['Title']} ({movie['Year']}, {movie['Rating']}/10)")  # Show movie title + year + rating
            st.write(movie['Description'][:200] + "...")  # Show first 200 chars only
            rec_poster_path = get_poster_path(movie['Image_Path'])
            if rec_poster_path:
                st.image(Image.open(rec_poster_path), caption=movie['Title'], width=150)
            else:
                st.warning("🚨 Poster not available!")

# Automatically select the first movie from filtered results if available
selected_movie = filtered_movies.iloc[0]
show_recommendations(selected_movie)
