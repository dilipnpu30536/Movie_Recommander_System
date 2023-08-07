import pickle   #for reading data from pickle files
import streamlit as st  #creating the web interface
import requests #making HTTP requests
import time #for delay

# Function to fetch the movie poster with error handling and retries
def fetch_poster(movie_id, max_retries=5):
    # URL to fetch movie data from TMDb API
    url = "https://api.themoviedb.org/3/movie/{}?api_key=1a58725314abb61a4d664ca3e1131622&language=en-US".format(movie_id)
    retries = 0
    while retries < max_retries:
        try:
            # Send a request to TMDb API to fetch movie data
            data = requests.get(url)
            data.raise_for_status()  # Raise an exception for 4xx and 5xx errors
            data = data.json()
            poster_path = data['poster_path']
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        except requests.exceptions.RequestException as e:
            # Handle request exceptions and retry
            st.warning(f"Error fetching the movie poster: {e}")
            retries += 1
            # Wait for a few seconds before retrying
            time.sleep(2)
        except KeyError as e:
            # Handle invalid data received from the API
            st.warning(f"Invalid data received from the API: {e}")
            return None
    # If max_retries are reached and the poster is still not fetched, return None
    st.error("Failed to fetch the movie poster. Please try again later.")
    return None

# Function to fetch movie details with error handling and retries
def fetch_movie_details(movie_id, max_retries=5):
    # TMDb API key for accessing movie details
    api_key = "1a58725314abb61a4d664ca3e1131622"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    retries = 0
    while retries < max_retries:
        try:
            # Send a request to TMDb API to fetch movie details
            data = requests.get(url)
            data.raise_for_status()  # Raise an exception for 4xx and 5xx errors
            data = data.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle request exceptions and retry
            st.warning(f"Error fetching movie details: {e}")
            retries += 1
            # Wait for a few seconds before retrying
            time.sleep(2)
    st.error("Failed to fetch movie details. Please try again later.")
    return None

# Function to fetch movie trailers with error handling and retries
def fetch_movie_trailers(movie_id, max_retries=5):
    # TMDb API key for accessing movie trailers
    api_key = "1a58725314abb61a4d664ca3e1131622"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US"
    retries = 0
    while retries < max_retries:
        try:
            # Send a request to TMDb API to fetch movie trailers
            data = requests.get(url)
            data.raise_for_status()  # Raise an exception for 4xx and 5xx errors
            data = data.json()
            return data.get('results', [])
        except requests.exceptions.RequestException as e:
            # Handle request exceptions and retry
            st.warning(f"Error fetching movie trailers: {e}")
            retries += 1
            # Wait for a few seconds before retrying
            time.sleep(2)
    st.error("Failed to fetch movie trailers. Please try again later.")
    return []

# Function to recommend movies
def recommend(movie, genre='Hollywood'):
    try:
        # Find the index of the selected movie in the movies DataFrame
        index = movies[movies['title'] == movie].index[0]
        if genre == 'Hollywood':
            # Get movie similarities for Hollywood genre
            distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
            recommended_movies = []
            for i in distances[1:6]:
                # fetch the movie details for the top 5 similar movies
                movie_id = movies.iloc[i[0]].movie_id
                movie_details = fetch_movie_details(movie_id)
                if movie_details:
                    recommended_movies.append(movie_details)
            return recommended_movies
        else:
            return []
    except IndexError:
        st.error("Movie not found in the database.")
        return []

# Set page configuration for responsiveness
st.set_page_config(
    page_title="Movie Recommender System",
    layout="wide",  # Wide layout to better utilize space
    initial_sidebar_state="auto",  # Sidebar auto-collapsed on narrower screens
)

# Load data from pickle files (movie_list.pkl and similarity.pkl)
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Create a horizontal navigation bar above the title
st.markdown(
    """
    <style>
    .*{
        background-color: #FF6347;
    }
    .navbar {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        padding: 10px;
    }
    .navbar a {
        background-color: #FF6347;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        margin-right: 10px;
        text-decoration: none;
    }
    .navbar a:hover {
        background-color: #FF4500;
        cursor: pointer;
    }

    /* CSS media query for responsiveness */
    @media (max-width: 768px) {
        .navbar {
            justify-content: flex-start;
        }
    }

    .movie-recommendation {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    .google-link {
        display: inline-block;
        text-decoration: none;
        margin-bottom: 20px;
        transition: transform 0.3s, background-color 0.3s;
    }

    .google-button {
        background-color: #4169E1;
        color: white;
        padding: 5px 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: transform 0.3s, background-color 0.3s;
    }

    .google-button:hover {
        background-color: #FF6347;
        transform: scale(1.05);
    }

    .google-button:focus {
        outline: none;
    }

    .movie-details {
        font-size: 18px;
        color: #333;
        margin-top: 10px;
    }
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #4169E1;
        color: white;
    }
    </style>
    <div class="navbar">
        <a href="#" class="stButton">Home</a>
        <a href="https://www.linkedin.com/in/manishkumar742/" target="_blank" class="stButton">About Us</a>
        <a href="https://manishnips.blogspot.com/" class="stButton">Contact</a>
    </div>
    """,
    unsafe_allow_html=True
)

# Page title and header
st.title('Movie Recommender System')

# Sidebar navigation
st.sidebar.title("Genres")
# List of Indian cinema genres
indian_cinema_list = [
    ('Hollywood', 'Hollywood'),
    ('Bollywood', 'Bollywood (Hindi Cinema) - Mumbai, Maharashtra'),
    ('Tollywood', 'Tollywood (Telugu Cinema) - Hyderabad, Telangana'),
    ('Kollywood', 'Kollywood (Tamil Cinema) - Chennai, Tamil Nadu'),
    ('Sandalwood', 'Sandalwood (Kannada Cinema) - Bengaluru, Karnataka'),
    ('Mollywood', 'Mollywood (Malayalam Cinema) - Kochi, Kerala'),
    ('Tollywood', 'Tollywood (Bengali Cinema) - Kolkata, West Bengal'),
    ('Pollywood', 'Pollywood (Punjabi Cinema) - Chandigarh, Punjab'),
    ('Bhojpuri', 'Bhojpuri Cinema - Bhojpur region in North India'),
    ('Gujarati', 'Gujarati Cinema - Gujarat'),
    ('Marathi', 'Marathi Cinema - Mumbai, Maharashtra'),
    ('Odia', 'Odia Cinema (Odia Film Industry) - Odisha'),
    ('Chhollywood', 'Chhollywood (Chhattisgarhi Cinema) - Chhattisgarh'),
    ('Rajasthani', 'Rajasthani Cinema - Rajasthan'),
    ('Haryanvi', 'Haryanvi Cinema - Haryana')
]

selected_genre = st.sidebar.selectbox("Select a genre", indian_cinema_list)

# Dropdown to select a movie
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Button to show recommendation for the selected genre
if selected_genre[0] == 'Hollywood':
    if st.button(f'Show {selected_genre[0]} Movies', key='genre_btn', help=f'Click to see recommended {selected_genre[0]} movies!'):
        recommended_movies = recommend(selected_movie, genre=selected_genre[0])
        if recommended_movies:
            st.subheader('Recommended Movies')
            for movie in recommended_movies:
                movie_name = movie['title']
                google_search_link = f"https://www.google.com/search?q={movie_name.replace(' ', '+')}"
                st.markdown(f"<p class='movie-recommendation'>{movie_name}</p>", unsafe_allow_html=True)
                st.image("https://image.tmdb.org/t/p/w500/" + movie['poster_path'])
                st.write(f"Release Year: {movie['release_date']}")
                st.write(f"Genre: {', '.join(genre['name'] for genre in movie['genres'])}")
                st.write(f"Plot Summary: {movie['overview']}")
                # Check if movie has trailers
                trailers = fetch_movie_trailers(movie['id'])
                if trailers:
                    st.subheader("Trailer")
                    # Show only the first trailer
                    trailer_key = trailers[0]['key']
                    st.video(f"https://www.youtube.com/watch?v={trailer_key}")
                else:
                    st.write("Trailer not available for this movie.")
                # Style the "Search on Google" link as an attractive button on hover
                st.markdown(f"""
                    <a href='{google_search_link}' target='_blank' class='google-link'>
                        <button class='google-button'>Search on Google</button>
                    </a>
                    """,
                    unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.write(f"I'm working on the recommendation for {selected_genre[0]}. Please try again later.")
else:
    st.write(f"I'm working on the recommendation for {selected_genre[0]}. Please try again later.")

# Footer
st.markdown(
    """
    <footer class="footer">
        <p>Designed by @Manish❤️</p>
        <p>Contact: manishcuk@hotmail.com</p>
        <p>Follow me on <a href="https://www.linkedin.com/in/manishkumar742/" target="_blank" style="color: #FF6347;">LinkedIn</a></p>
    </footer>
    """,
    unsafe_allow_html=True
)
