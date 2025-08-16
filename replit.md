# Reddit User Analyzer

## Overview

This is a Flask-based web application that analyzes Reddit users by retrieving and processing their public post and comment data. The application provides comprehensive analytics including activity patterns, sentiment analysis, subreddit participation, and engagement metrics through an interactive dashboard.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (dark theme) for responsive UI
- **JavaScript**: Vanilla JavaScript for form handling and dynamic content updates
- **Visualization**: Chart.js for data visualization (timeline and sentiment charts)
- **Styling**: Custom CSS with Bootstrap components and Font Awesome icons

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **API Integration**: PRAW (Python Reddit API Wrapper) for Reddit data access
- **Data Processing**: Pandas for data manipulation and TextBlob for sentiment analysis
- **Deployment**: Gunicorn WSGI server with autoscaling configuration

### Data Processing Pipeline
1. User input validation and sanitization
2. Reddit API authentication and user verification
3. Content retrieval (posts and comments)
4. Data analysis and sentiment processing
5. Results aggregation and JSON response formatting

## Key Components

### Core Modules
- **app.py**: Main Flask application with routing and request handling
- **reddit_analyzer.py**: Core analysis engine with Reddit API integration
- **main.py**: Application entry point for development server

### Frontend Components
- **templates/index.html**: Main interface with user input form and results display
- **static/js/main.js**: Client-side logic for form submission and data visualization
- **static/css/style.css**: Custom styling and responsive design elements

### Configuration
- **pyproject.toml**: Python dependencies and project metadata
- **.replit**: Replit-specific configuration with Python 3.11 and PostgreSQL packages

## Data Flow

1. **User Input**: Username entered through web interface
2. **API Request**: Form submission triggers POST request to `/analyze` endpoint
3. **Data Retrieval**: Reddit API fetches user profile, posts, and comments
4. **Analysis Processing**: 
   - Sentiment analysis using TextBlob
   - Activity pattern analysis
   - Subreddit participation metrics
   - Engagement statistics calculation
5. **Response Generation**: Structured JSON response with analysis results
6. **Visualization**: Client-side chart rendering and dashboard population

## External Dependencies

### Reddit API Integration
- **Authentication**: Requires REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT environment variables
- **Rate Limiting**: Handled by PRAW library
- **Data Access**: Read-only access to public user content

### Python Packages
- **Flask**: Web framework and templating
- **PRAW**: Reddit API wrapper
- **Pandas**: Data manipulation and analysis
- **TextBlob**: Natural language processing for sentiment analysis
- **Gunicorn**: Production WSGI server

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Chart.js**: Data visualization library
- **Font Awesome**: Icon library

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Production Server**: Gunicorn with autoscaling deployment target
- **Development**: Hot-reload enabled for development workflow
- **Port Configuration**: Application runs on port 5000 with external binding

### Environment Setup
- PostgreSQL included in Nix packages (for potential future database integration)
- SSL/TLS support through OpenSSL package
- Locale support for international text processing

## Changelog

- June 20, 2025. Initial setup
- June 20, 2025. Page separation and theme toggle implementation:
  - Split main page from results page for better user flow
  - Added dark/light mode toggle with orange (#FF5700) color scheme for light mode
  - Created separate JavaScript files for theme management
  - Updated routing to handle form submissions via POST redirect
  - Maintained all existing analysis functionality
- June 21, 2025. Sentiment analysis redesign and keyword extraction:
  - Removed sentiment distribution chart and related code
  - Redesigned sentiment analysis section as single-card layout
  - Added top 10 keyword extraction from user comments with frequency counts
  - Implemented keyword filtering with comprehensive stop words list
  - Added visual keyword badges with different styling based on frequency
  - Positioned keywords section between sentiment analysis and character analysis
  - Expanded stop words list with extensive adverbs, conjunctive adverbs, and interjections
  - Enhanced filtering to exclude common verbs, pronouns, auxiliary verbs, and filler words
- July 10, 2025. Comprehensive verb filtering enhancement:
  - Expanded keyword extraction to exclude all types of verbs from results
  - Added comprehensive verb categories: physical actions, mental actions, communication, creation/destruction, possession/transfer, sensory, technology/work, linking, social interaction, emotional/mental states, time/process, movement, and health/body verbs
  - Implemented extensive verb filtering with 200+ verb exclusions for topic-focused keyword extraction
  - Moved sentiment summary from Character Analysis to Sentiment Analysis section for better organization

## User Preferences

Preferred communication style: Simple, everyday language.