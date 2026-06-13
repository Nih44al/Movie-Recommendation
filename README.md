Movie Recommendation System

Business Problem

Streaming platforms offer thousands of movies, making it difficult for users to quickly find content that matches their interests. An effective recommendation system helps users discover relevant content while improving engagement and user satisfaction.

Solution

Developed an interactive Movie Recommendation System that enables users to discover movies based on preferences such as genre, language, release year, and rating. The application provides personalized recommendations and displays detailed movie information through an intuitive interface.

Key Features

• Interactive filtering by language, genre, year, and rating
• Displays movie details and poster images
• Recommends similar movies based on selected movie attributes
• User-friendly dashboard built with Streamlit
• Handles missing images and incomplete data gracefully

Business Value

• Improves content discovery and user experience
• Demonstrates how recommendation systems can support customer engagement
• Reduces the time required to search large movie catalogs
• Showcases practical application of data analysis and personalization techniques

Technologies Used

• Python
• Pandas
• Streamlit
• Pillow
• Excel Dataset

How It Works

1. Users select filtering criteria such as genre, language, year, and rating.
2. The system processes the dataset and identifies matching movies.
3. Similar movies are recommended based on shared attributes.
4. Movie details and posters are displayed within an interactive dashboard.

Results

• Successfully developed a functional recommendation dashboard
• Enabled personalized movie discovery through dynamic filtering
• Applied data processing and recommendation logic to enhance content exploration

Setup Instructions

Clone the repository:

git clone https://github.com/Nih44al/Movie-Recommendation.git

cd Movie-Recommendation

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run movie_recommendation_app.py

Dataset Requirements

The dataset should contain the following columns:

• Title
• Description
• Language
• Genre
• Year
• Rating
• Image_Path

Future Enhancements

• Incorporate advanced recommendation algorithms
• Add filters for actors, directors, and production studios
• Improve recommendation accuracy using machine learning techniques
• Enhance dashboard design and responsiveness
• Integrate user feedback for personalized recommendations
