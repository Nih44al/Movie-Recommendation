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

# ✅ **1️⃣ Cache the dataset to prevent reloading**
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('movies_dataset.xlsx')
        df['Image_Path'] = df['Image_Path'].str.replace('poster/', 'posters/', regex=False)
        df['Image_Path'] = df['Image_Path'].str.replace(r'_\.jpg$', '.jpg', regex=True)
        df['Language'] = df['Language'].str.strip().str.title()
        df['Genre'] = df['Genre'].str.strip().str.title()
        return df[(df['Year'] >= 2014) & (df['Year'] <= 2024)].drop_duplicates(subset=['Title', 'Language', 'Genre', 'Year', 'Rating'])
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

movies = load_data()

# ✅ **2️⃣ Store selections in session state for faster filtering**
if "selected_year" not in st.session_state:
    st.session_state["selected_year"] = movies["Year"].min()
if "selected_genre" not in st.session_state:
    st.session_state["selected_genre"] = movies["Genre"].iloc[0]
if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = movies["Language"].iloc[0]

# ✅ **3️⃣ Use temporary variables & update session state only if changed**
st.title("🎥 Movie Recommendation System")
st.subheader("Select your preferences to find a movie!")

col1, col2, col3 = st.columns(3)
with col1:
    temp_year = st.selectbox("📅 Select Year", sorted(movies["Year"].unique()), index=sorted(movies["Year"].unique()).index(st.session_state["selected_year"]))
with col2:
    temp_genre = st.selectbox("🎭 Select Genre", sorted(movies["Genre"].unique()), index=sorted(movies["Genre"].unique()).index(st.session_state["selected_genre"]))
with col3:
    temp_language = st.selectbox("🗣 Select Language", sorted(movies["Language"].unique()), index=sorted(movies["Language"].unique()).index(st.session_state["selected_language"]))

# ✅ **4️⃣ Only trigger rerun if a filter changes (prevents unnecessary UI reloads)**
if (temp_year != st.session_state["selected_year"]) or (temp_genre != st.session_state["selected_genre"]) or (temp_language != st.session_state["selected_language"]):
    st.session_state["selected_year"] = temp_year
    st.session_state["selected_genre"] = temp_genre
    st.session_state["selected_language"] = temp_language
    st.rerun()  # ✅ This now only runs when a real change happens

# ✅ **5️⃣ Use `query()` for optimized filtering**
filtered_movies = movies.query("Year == @st.session_state.selected_year & Genre == @st.session_state.selected_genre & Language == @st.session_state.selected_language")

# If no movies match, show a warning
if filtered_movies.empty:
    st.warning("⚠️ No movies found for the selected criteria. Try different options.")
    st.stop()

# ✅ **6️⃣ Cache Image Loading (Faster Poster Display)**
@st.cache_resource
def load_image(image_path):
    """Loads an image efficiently."""
    default_image = "posters/default.jpg"
    if pd.notna(image_path):
        corrected_path = os.path.join("posters", os.path.basename(image_path))
        if os.path.exists(corrected_path):
            return Image.open(corrected_path)
    return Image.open(default_image) if os.path.exists(default_image) else None

# **Step 2: Select the First Movie from Filtered Results**
selected_movie = filtered_movies.iloc[0]

# Display selected movie
st.subheader("🎬 Selected Movie:")
st.markdown(f"### **{selected_movie['Title']} ({selected_movie['Year']}, {selected_movie['Rating']}/10)**")
st.markdown(f"**Description:** {selected_movie['Description']}")

# Load and display the selected movie's poster
poster_image = load_image(selected_movie['Image_Path'])
if poster_image:
    st.image(poster_image, caption=selected_movie['Title'], width=200)
else:
    st.warning("🚨 Poster not available!")

# ✅ **7️⃣ Use `.sample(n, random_state)` efficiently for recommendations**
st.subheader("✨ Recommended Movies:")
recommendations = movies.query("Language == @selected_movie.Language & Genre == @selected_movie.Genre & Title != @selected_movie.Title").sample(min(3, len(movies)), random_state=42)

if recommendations.empty:
    st.write("No recommendations available.")
else:
    for _, movie in recommendations.iterrows():
        st.markdown(f"### **{movie['Title']} ({movie['Year']}, {movie['Rating']}/10)**")
        st.markdown(f"**Description:** {movie['Description']}")
        rec_poster = load_image(movie['Image_Path'])
        if rec_poster:
            st.image(rec_poster, caption=movie['Title'], width=150)
        else:
            st.warning("🚨 Poster not available!")
