import streamlit as st
import pandas as pd
import os
from PIL import Image

# Set Streamlit page config
st.set_page_config(page_title="Movie Recommendation", layout="wide")

# Apply custom CSS
st.markdown(
    """
    <style>
        * { cursor: default !important; }
        input, select, textarea, button, [role="button"] { cursor: pointer !important; }
        .stMarkdown { white-space: pre-wrap !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ **Load the dataset once (No Caching)**
@st.cache_data
def load_movies():
    try:
        movies = pd.read_excel('movies_dataset.xlsx')
        required_columns = {'Title', 'Description', 'Language', 'Genre', 'Year', 'Rating', 'Image_Path'}
        if not required_columns.issubset(movies.columns):
            st.error("Dataset is missing required columns!")
            st.stop()
        return movies
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

movies = load_movies()

# ✅ **Preprocess dataset once**
movies['Image_Path'] = movies['Image_Path'].str.replace('poster/', 'posters/', regex=False)
movies = movies[(movies['Year'] >= 2014) & (movies['Year'] <= 2024)]
movies['Language'] = movies['Language'].str.strip().str.title()
movies['Genre'] = movies['Genre'].str.strip().str.title()
movies = movies.drop_duplicates(subset=['Title', 'Language', 'Genre', 'Year', 'Rating'])

# ✅ **Get unique values (NO Caching to improve response time)**
language_options = sorted(movies['Language'].dropna().unique())
genre_options = sorted(movies['Genre'].dropna().unique())
year_options = sorted(movies['Year'].dropna().unique())

# ✅ **Session State Defaults**
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = year_options[0]
if "selected_genre" not in st.session_state:
    st.session_state["selected_genre"] = genre_options[0]
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = language_options[0]

# ✅ **Faster UI Updates (No unnecessary `st.rerun()`)**
st.title("🎥 Movie Recommendation System")
st.subheader("Select your preferences to find a movie!")

col1, col2, col3 = st.columns(3)
with col1:
    selected_year = st.selectbox("📅 Select Year", year_options, index=year_options.index(st.session_state["selected_year"]))
with col2:
    selected_genre = st.selectbox("🎭 Select Genre", genre_options, index=genre_options.index(st.session_state["selected_genre"]))
with col3:
    selected_language = st.selectbox("🗣 Select Language", language_options, index=language_options.index(st.session_state["selected_language"]))

# ✅ **Only update session state if values change**
if (selected_year != st.session_state["selected_year"] or
    selected_genre != st.session_state["selected_genre"] or
    selected_language != st.session_state["selected_language"]):
    st.session_state["selected_year"] = selected_year
    st.session_state["selected_genre"] = selected_genre
    st.session_state["selected_language"] = selected_language

# ✅ **Use direct Pandas filtering instead of `.query()`**
filtered_movies = movies.loc[
    (movies['Year'] == st.session_state["selected_year"]) &
    (movies['Genre'] == st.session_state["selected_genre"]) &
    (movies['Language'] == st.session_state["selected_language"])
]

# If no movies match, show a warning
if filtered_movies.empty:
    st.warning("⚠️ No movies found for the selected criteria. Try different options.")
    st.stop()

# ✅ **Select the First Movie from Filtered Results**
selected_movie = filtered_movies.iloc[0]

# ✅ **Fast function to get poster path (No Caching to Avoid Overhead)**
def get_poster_path(poster_path):
    """Returns the full path of the poster if available, else returns a default placeholder."""
    default_image = os.path.join("posters", "default.jpg")
    if pd.notna(poster_path):
        full_path = os.path.join("posters", os.path.basename(poster_path))
        if os.path.exists(full_path):
            return full_path
    return default_image if os.path.exists(default_image) else None

# ✅ **Optimized Recommendation System**
def show_recommendations(selected_movie):
    st.subheader("🎬 Selected Movie:")
    st.markdown(f"### **{selected_movie['Title']} ({selected_movie['Year']}, {selected_movie['Rating']}/10)**")
    st.markdown(f"**Description:** {selected_movie['Description']}")

    # Load and display the selected movie's poster
    poster_path = get_poster_path(selected_movie['Image_Path'])
    if poster_path:
        st.image(Image.open(poster_path), caption=selected_movie['Title'], width=200)
    else:
        st.warning("🚨 Poster not available!")

    # Display recommended movies
    st.subheader("✨ Recommended Movies:")
    recommendations = movies.loc[
        (movies['Title'] != selected_movie['Title']) &
        (movies['Language'] == selected_movie['Language']) &
        (movies['Genre'] == selected_movie['Genre'])
    ].sample(min(3, len(movies)), random_state=42)

    if recommendations.empty:
        st.write("No recommendations available.")
    else:
        for _, movie in recommendations.iterrows():
            st.markdown(f"### **{movie['Title']} ({movie['Year']}, {movie['Rating']}/10)**")
            st.markdown(f"**Description:** {movie['Description']}")
            rec_poster_path = get_poster_path(movie['Image_Path'])
            if rec_poster_path:
                st.image(Image.open(rec_poster_path), caption=movie['Title'], width=150)
            else:
                st.warning("🚨 Poster not available!")

# Display the selected movie and recommendations
show_recommendations(selected_movie)
