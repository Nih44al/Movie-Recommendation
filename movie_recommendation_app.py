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

# ✅ **Cache dataset for faster loading**
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

# ✅ **Preprocess dataset once (instead of every time UI updates)**
movies['Image_Path'] = movies['Image_Path'].str.replace('poster/', 'posters/', regex=False)
movies['Image_Path'] = movies['Image_Path'].str.replace(r'_\.jpg$', '.jpg', regex=True)
movies = movies[(movies['Year'] >= 2014) & (movies['Year'] <= 2024)]
movies['Language'] = movies['Language'].str.strip().str.title()
movies['Genre'] = movies['Genre'].str.strip().str.title()
movies = movies.drop_duplicates(subset=['Title', 'Language', 'Genre', 'Year', 'Rating'])

# ✅ **Cache unique dropdown values to improve UI speed**
@st.cache_data
def get_dropdown_options():
    return {
        "language_options": sorted(movies['Language'].dropna().unique()),
        "genre_options": sorted(movies['Genre'].dropna().unique()),
        "year_options": sorted(movies['Year'].dropna().unique())
    }

dropdowns = get_dropdown_options()

# ✅ **Persistent Selections Using Session State**
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = dropdowns["year_options"][0]
if "selected_genre" not in st.session_state:
    st.session_state["selected_genre"] = dropdowns["genre_options"][0]
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = dropdowns["language_options"][0]

# ✅ **Use temporary variables instead of modifying session state directly**
st.title("🎥 Movie Recommendation System")
st.subheader("Select your preferences to find a movie!")

col1, col2, col3 = st.columns(3)
with col1:
    temp_year = st.selectbox("📅 Select Year", dropdowns["year_options"], index=dropdowns["year_options"].index(st.session_state["selected_year"]))
with col2:
    temp_genre = st.selectbox("🎭 Select Genre", dropdowns["genre_options"], index=dropdowns["genre_options"].index(st.session_state["selected_genre"]))
with col3:
    temp_language = st.selectbox("🗣 Select Language", dropdowns["language_options"], index=dropdowns["language_options"].index(st.session_state["selected_language"]))

# ✅ **Update session state once to avoid multiple reruns**
if temp_year != st.session_state["selected_year"] or temp_genre != st.session_state["selected_genre"] or temp_language != st.session_state["selected_language"]:
    st.session_state["selected_year"] = temp_year
    st.session_state["selected_genre"] = temp_genre
    st.session_state["selected_language"] = temp_language
    st.rerun()  # Refresh once after all changes

# ✅ **Use `.query()` for faster filtering instead of multiple conditions**
filtered_movies = movies.query(
    "Year == @st.session_state.selected_year and Genre == @st.session_state.selected_genre and Language == @st.session_state.selected_language"
)

# If no movies match, show a warning
if filtered_movies.empty:
    st.warning("⚠️ No movies found for the selected criteria. Try different options.")
    st.stop()

# ✅ **Select the First Movie from Filtered Results**
selected_movie = filtered_movies.iloc[0]

# ✅ **Cache function to resolve poster path**
@st.cache_data
def get_poster_path(poster_path):
    """Returns the full path of the poster if available, else returns a default placeholder."""
    default_image = os.path.join("posters", "default.jpg")
    if pd.notna(poster_path):
        full_path = os.path.join(os.getcwd(), poster_path)
        if os.path.exists(full_path):
            return full_path
    return default_image if os.path.exists(default_image) else None

# Function to display recommendations
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
    recommendations = movies.query(
        "Title != @selected_movie.Title and Language == @selected_movie.Language and Genre == @selected_movie.Genre"
    ).sample(min(3, len(movies)), random_state=42)

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
