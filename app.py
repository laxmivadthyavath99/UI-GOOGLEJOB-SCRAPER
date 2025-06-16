from flask import Flask, request, jsonify
from flask_cors import CORS
from scrape_jobs import scrape_google_job_details

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    query = data.get('url')
    page = int(data.get('page', 1))
    page_size = int(data.get('page_size', 5))
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    url = f"https://www.google.com/search?q={query}&ibp=htl;jobs"
    results = scrape_google_job_details(url)
    # Pagination logic
    start = (page - 1) * page_size
    end = start + page_size
    paginated = results[start:end]
    print(f"Returning jobs {start+1} to {min(end, len(results))} of {len(results)}")
    print("Paginated jobs data:", paginated)
    return jsonify({
        "jobs": paginated,
        "total": len(results)
    })

if __name__ == "__main__":
    app.run(debug=True)

