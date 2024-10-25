from flask import Flask, render_template, request, jsonify
import pandas as pd
import logging
import re
from Model.model import BookRecommender, recommend_by_rating, recommend_by_publisher




app = Flask(__name__)

# Load dataset
df = pd.read_csv(r'dataset/cleaned_data.csv')
print(df.head(5))

# Configure logging to write to app.log
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_title(title):
    """ Normalize title by removing unwanted characters and converting to lowercase. """
    return re.sub(r'[^\w\s#()]', '', title).lower().strip()

@app.route('/')
def index():
    logger.info("Accessed the index page.")
    return render_template('index.html', title_recommendations=[], rating_recommendations=[], publisher_recommendations=[])


# @app.route('/recommend_by_book', methods=['POST'])
# def recommend_by_book():
#     book_name = request.form.get('book_name', '').strip()  # Normalize input
#     logger.info(f"Received book recommendation request for: {book_name}")
    
#     title_recommendations = BookRecommender(book_name) if book_name else []
    
#     if title_recommendations:
#         logger.info(f"Recommendations found for {book_name}: {title_recommendations}")
#     else:
#         logger.warning("No recommendations found for the given book name.")
    
#     return render_template('recommendations.html', title_recommendations=title_recommendations,
#                            rating_recommendations=[], publisher_recommendations=[])

@app.route('/recommend_by_book', methods=['POST'])
def recommend_by_book():
    book_name = request.form.get('book_name', '').strip()  # Normalize input
    logger.info(f"Received book recommendation request for: {book_name}")
    
    title_recommendations = BookRecommender(book_name) if book_name else []
    
    # Ensure pagination variables are defined
    current_page = 1  # Default to page 1
    total_pages = 1   # Default to 1 page (adjust if needed)

    if title_recommendations:
        logger.info(f"Recommendations found for {book_name}: {title_recommendations}")
    else:
        logger.warning("No recommendations found for the given book name.")
    
    return render_template('recommendations.html',
                           title_recommendations=title_recommendations,
                           rating_recommendations=[], 
                           publisher_recommendations=[],
                           current_page=current_page,
                           total_pages=total_pages)




@app.route('/recommend_by_publisher', methods=['POST'])
def recommend_by_publisher_route():
    publisher = request.form.get('publisher')
    logger.info(f"Received publisher recommendation request for: {publisher}")
    
    # Get recommendations based on the publisher
    publisher_recommendations = recommend_by_publisher(publisher) if publisher else []
    
    # Ensure pagination variables are defined
    current_page = 1  # Default to page 1
    total_pages = 1  # Default to 1 page (adjust if needed)

    if publisher_recommendations:
        logger.info(f"Recommendations found for publisher {publisher}: {publisher_recommendations}")
        
        # If you want to implement pagination, you can limit the number of recommendations here
        items_per_page = 25
        total_recommendations = len(publisher_recommendations)
        
        # Calculate total pages based on the number of recommendations
        total_pages = (total_recommendations + items_per_page - 1) // items_per_page
        
        # Optionally, you can slice the recommendations for pagination
        paginated_recommendations = publisher_recommendations[:items_per_page]  # Get only the first page of results
        
    else:
        logger.warning("No recommendations found for the given publisher.")
        paginated_recommendations = []  # No recommendations to paginate

    return render_template('recommendations.html',
                           title_recommendations=[], 
                           rating_recommendations=[], 
                           publisher_recommendations=paginated_recommendations,
                           current_page=current_page,
                           total_pages=total_pages)
    
    
@app.route('/recommend_by_rating', methods=['GET', 'POST'])
def recommend_by_rating_route():
    if request.method == 'POST':
        rating = request.form.get('rating')
        min_rating = float(rating) if rating else 0.0
        logger.info(f"Received rating recommendation request for minimum rating: {min_rating}")
        
        # Get all recommendations based on the minimum rating
        all_recommendations = recommend_by_rating(min_rating)
        
        # Pagination logic
        page = request.args.get('page', 1, type=int)
        per_page = 25
        total_books = len(all_recommendations)
        start = (page - 1) * per_page
        end = start + per_page
        
        # Slice the recommendations for the current page
        recommendations_to_display = all_recommendations[start:end]
        
        # Calculate total pages
        total_pages = (total_books // per_page) + (1 if total_books % per_page > 0 else 0)

        if recommendations_to_display:
            logger.info(f"Recommendations found: {recommendations_to_display}")
        else:
            logger.warning("No recommendations found for the given minimum rating.")
        
        return render_template('recommendations.html', 
                               title_recommendations=[], 
                               rating_recommendations=recommendations_to_display, 
                               publisher_recommendations=[], 
                               current_page=page, 
                               total_pages=total_pages)
    
    else:  # Handle GET requests for pagination
        min_rating = request.args.get('rating', type=float, default=0.0)
        all_recommendations = recommend_by_rating(min_rating)
        
        # Pagination logic
        page = request.args.get('page', 1, type=int)
        per_page = 25
        total_books = len(all_recommendations)
        start = (page - 1) * per_page
        end = start + per_page
        
        # Slice the recommendations for the current page
        recommendations_to_display = all_recommendations[start:end]
        
        # Calculate total pages
        total_pages = (total_books // per_page) + (1 if total_books % per_page > 0 else 0)

        return render_template('recommendations.html',
                               title_recommendations=[],
                               rating_recommendations=recommendations_to_display,
                               publisher_recommendations=[],
                               current_page=page,
                               total_pages=total_pages)


@app.route('/search_books')
def search_books():
    query = request.args.get('query', '').lower()
    
    # Normalize query for searching
    normalized_query = normalize_title(query)
    
    matching_books = df[df['title'].str.lower().str.contains(normalized_query)]
    
    book_titles = matching_books['title'].tolist()
    
    return jsonify(book_titles)



@app.route('/recommendations')
def recommend():
    logger.info("Accessed the recommendations page.")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
