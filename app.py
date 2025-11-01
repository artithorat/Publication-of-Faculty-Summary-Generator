from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from scholarly import scholarly
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Serve the frontend HTML
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

# Endpoint to list faculty names from Google Scholar search
@app.route('/list_faculties', methods=['GET'])
def list_faculties():
    try:
        search_keyword = request.args.get('search', '').strip()
        if not search_keyword:
            return jsonify({"error": "Search keyword is required."}), 400

        logger.info(f"Searching for authors matching: {search_keyword}")
        search_query = scholarly.search_author(search_keyword)
        authors = []

        for _ in range(5):  # Limit results
            author = next(search_query, None)
            if author:
                authors.append(author.get('name', 'Unknown'))
            else:
                break

        return jsonify({"faculty_names": authors}), 200
    except Exception as e:
        logger.error(f"Error in /list_faculties: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to generate a faculty summary
@app.route('/generate_summary', methods=['POST'])
def generate_summary():
    try:
        data = request.get_json()
        faculty_name = data.get('faculty_name', '').strip()

        if not faculty_name:
            return jsonify({"error": "Faculty name is required."}), 400

        logger.info(f"Generating summary for: {faculty_name}")
        scholar_data = fetch_google_scholar_data(faculty_name)
        return jsonify(scholar_data), 200
    except Exception as e:
        logger.error(f"Error in /generate_summary: {e}")
        return jsonify({"error": str(e)}), 500

# Helper function to fetch and format scholar data
def fetch_google_scholar_data(faculty_name):
    try:
        search_query = scholarly.search_author(faculty_name)
        author = next(search_query, None)
        if not author:
            return {"error": f"No data found for '{faculty_name}'."}

        author_details = scholarly.fill(author)

        publications = [
            {
                "Title": pub.get("bib", {}).get("title", "N/A"),
                "Year": pub.get("bib", {}).get("pub_year", "N/A"),
                "Citations": pub.get("num_citations", 0),
            }
            for pub in author_details.get("publications", [])[:5]
        ]

        return {
            "exact_name": author_details.get("name", "N/A"),
            "affiliation": author_details.get("affiliation", "N/A"),
            "total_citations": author_details.get("citedby", 0),
            "publications": publications,
            "profile_link": author_details.get("url", "")
        }
    except Exception as e:
        logger.error(f"Error fetching scholar data: {e}")
        return {"error": f"An error occurred while fetching data: {str(e)}"}

if __name__ == '__main__':
    app.run(debug=True)
