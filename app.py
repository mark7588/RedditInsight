import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from reddit_analyzer import RedditAnalyzer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")

# Initialize Reddit analyzer
reddit_analyzer = RedditAnalyzer()

@app.route('/')
def index():
    """Main landing page with user input form"""
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    """Results page that handles analysis"""
    if request.method == 'POST':
        # Get username from form and redirect to results page with parameter
        username = request.form.get('username', '').strip()
        if username.startswith('u/'):
            username = username[2:]
        return redirect(url_for('results', username=username))
    
    # Handle GET request - show results page
    return render_template('results.html')

@app.route('/analyze', methods=['POST'])
def analyze_user():
    """Analyze Reddit user and return comprehensive analytics"""
    try:
        username = request.form.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Please enter a valid Reddit username'
            })
        
        # Remove u/ prefix if present
        if username.startswith('u/'):
            username = username[2:]
        
        # Perform analysis
        analysis_result = reddit_analyzer.analyze_user(username)
        
        if analysis_result['success']:
            return jsonify(analysis_result)
        else:
            return jsonify({
                'success': False,
                'error': analysis_result.get('error', 'Analysis failed')
            })
            
    except Exception as e:
        logging.error(f"Error analyzing user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis'
        })

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error occurred'
    }), 500
