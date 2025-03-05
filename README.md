# Movie Recommendation System

## Overview
This project is a **Movie Recommendation System** built using **Streamlit**, allowing users to filter and discover movies based on language, genre, year, and rating. The system displays details and posters for selected movies and suggests similar recommendations.

## Features
- Interactive sidebar for filtering movies.
- Displays selected movie details with its poster.
- Provides three recommended movies based on genre and language.
- Handles missing posters gracefully.

## Technologies Used
- **Python** (Data Processing)
- **Streamlit** (Web App UI)
- **Pandas** (Dataset Handling)
- **Pillow** (Image Processing)

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Nih44al/Movie-Recommendation.git
   cd Movie-Recommendation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run movie_recommendation_app.py
   ```

## Dataset Requirements
Ensure the dataset **movies_dataset.xlsx** includes the following columns:
- `Title`, `Description`, `Language`, `Genre`, `Year`, `Rating`, `Image_Path`

## Folder Structure
- `/posters/` → Folder containing movie posters.
- `movie_recommendation_app.py` → Main application script.
- `movies_dataset.xlsx` → Movie data source.
- `requirements.txt` → List of dependencies.

## Future Improvements
- Improve recommendation algorithm.
- Add more filters (e.g., director, actors).
- Enhance UI with better design and responsiveness.
