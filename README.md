# NextTrack: Music Recommendation System

NextTrack is a Django-based web application that uses a K-Nearest Neighbors (KNN) machine learning model to provide music recommendations based on audio features like energy, danceability, and tempo.

## Features
* **KNN Recommendation Engine:** 
* **Hybrid Filtering:** 
* **Data Visualization:** 
* **Interactive Player:** 

## Setup Instructions
Follow these steps to get the project running on your local machine.

### 1. Create a Virtual Environment
It is highly recommended to use a virtual environment to ensure library versions (NumPy, Scikit-Learn) match the trained models and to avoid version-related loading errors.

### 2. Install Dependencies
Once the virtual environment is activated, install the required libraries:

pip install -r requirements.txt

### 3. Run the Application
The project includes a pre-configured SQLite database. Start the development server:

python manage.py runserver 127.0.0.1:8000

Once the server is running, open your browser and go to: http://127.0.0.1:8000/
