"""
Flask Web Application for the Valo Spectator Ghost demo.
This lightweight demo provides a spectator UI and does not expose
the AI web search functionality in the public UI.
"""

import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from src.models import SearchError, SearchOptions
from src.search_service import create_search_service

# Load environment variables from the project root
project_root = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)

# Get API key from environment (may be None in demo mode)
api_key = os.getenv("OPENAI_API_KEY")

# Initialize search service. If no API key is available we run in demo
# mode using a lightweight local client—this allows the web UI to function
# without a real OpenAI key (useful for demos and local testing).
try:
    # Use create_search_service to allow demo mode when no API key is present
    search_service = create_search_service(api_key=api_key, allow_demo=True)
    app.config["DEMO_MODE"] = (
        getattr(search_service, "demo_mode", False)
        or isinstance(search_service, object)
        and search_service.__class__.__name__ == "DemoSearchService"
    )
    if app.config["DEMO_MODE"]:
        print(
            "⚠️  Running in DEMO mode: OPENAI_API_KEY not set. Using local demo client."
        )
except Exception as e:
    # If initialization fails (unexpected), surface the error and exit
    print(f"Error initializing search service: {e}")
    sys.exit(1)


@app.route("/")
def index():
    """Render the main search page."""
    return render_template("index.html")


@app.route("/spectator-ghost")
def spectator_ghost():
    """Render the Spectator Ghost concept page."""
    return render_template("spectator_ghost.html")


@app.route("/search", methods=["POST"])
def search():
    """
    Handle search requests.
    Expects JSON payload with 'query' and optional 'domains'.
    """
    try:
        data = request.get_json()
        query = data.get("query", "").strip()

        if not query:
            return (
                jsonify({"success": False, "error": "Please enter a search query"}),
                400,
            )

        # Parse optional domains
        domains = []
        domains_input = data.get("domains", "").strip()
        if domains_input:
            # Split by comma and clean up
            domains = [d.strip() for d in domains_input.split(",") if d.strip()]

        # Create search options (apply domain filters if provided)
        options = (
            search_service.apply_domain_filters(domains) if domains else SearchOptions()
        )

        # Perform search
        result = search_service.search(query, options)

        # Format response
        return jsonify(
            {
                "success": True,
                "query": query,
                "answer": result.text,
                "citations": [
                    {"title": citation.title, "url": citation.url, "number": i + 1}
                    for i, citation in enumerate(result.citations)
                ],
                "citation_count": len(result.citations),
                "search_id": result.search_id,
            }
        )

    except SearchError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "An unexpected error occurred. Please try again.",
                }
            ),
            500,
        )


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Valo Spectator Ghost"})


if __name__ == "__main__":
    # Run the Flask app
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    print("\n" + ("=" * 80))
    print("🚀 Valo Spectator Ghost Application Starting")
    print("=" * 80)
    print(f"📍 URL: http://localhost:{port}")
    print("🎮 Spectator demo ready")
    print(("=" * 80) + "\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
