
# Reddit User Analyzer

## Introduction

Reddit User Analyzer is a comprehensive web application that provides deep insights into Reddit users' posting behavior, sentiment patterns, and engagement metrics. Built with Flask and modern web technologies, this tool analyzes public Reddit data to generate detailed analytics dashboards with interactive visualizations.

## Problem Solved

Social media analysis is crucial for understanding user behavior, content patterns, and community engagement. However, manually analyzing a Reddit user's posting history across multiple subreddits and timeframes is time-consuming and inefficient. This application solves several key problems:

- **Manual Analysis Overhead**: Eliminates the need to manually browse through hundreds of posts and comments
- **Sentiment Understanding**: Provides automated sentiment analysis to understand user's emotional patterns
- **Engagement Insights**: Reveals posting frequency, peak activity times, and community participation
- **Content Categorization**: Identifies key topics and interests through keyword extraction
- **Behavioral Patterns**: Analyzes communication style and personality traits based on posting behavior

## How the Application Works

### Architecture Overview

The application follows a modern web architecture pattern with separated frontend and backend concerns:

1. **Frontend Interface**: Users input a Reddit username through a clean, responsive web interface
2. **API Processing**: Flask backend processes the request and interfaces with Reddit's API
3. **Data Analysis**: Multiple analysis engines process the retrieved data:
   - Sentiment analysis using TextBlob
   - Keyword extraction with custom filtering
   - Timeline analysis for activity patterns
   - Character analysis based on behavioral patterns
4. **Results Visualization**: Interactive charts and metrics are displayed on a dedicated results page

### Data Flow

```
User Input → Form Submission → Reddit API → Data Processing → Analysis → Visualization
```

## Tech Stack and Libraries

### Backend Technologies
- **Flask 3.0+**: Python web framework for routing and API endpoints
- **PRAW (Python Reddit API Wrapper)**: Official Reddit API integration
- **TextBlob**: Natural language processing for sentiment analysis
- **Pandas**: Data manipulation and analysis
- **Gunicorn**: Production WSGI server with autoscaling

### Frontend Technologies
- **HTML5 & CSS3**: Modern web standards with semantic markup
- **Bootstrap 5**: Responsive UI framework with dark/light theme support
- **Vanilla JavaScript**: Client-side interactivity and AJAX requests
- **Chart.js**: Interactive data visualization library
- **Font Awesome**: Icon library for enhanced UI

### Development and Deployment
- **Python 3.11**: Runtime environment
- **Replit**: Cloud development and deployment platform
- **Environment Variables**: Secure API credential management

## How to Use the Application

### Prerequisites

1. **Reddit API Credentials**: You need to register a Reddit application to get API credentials
   - Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
   - Create a new application (script type)
   - Note down your `client_id`, `client_secret`

2. **Environment Setup**: Configure the following environment variables in Replit:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=RedditUserAnalyzer/1.0
   ```

### Running the Application

1. **Fork the Project**: Fork this Repl to your account
2. **Install Dependencies**: Dependencies are automatically installed via `pyproject.toml`
3. **Configure API Keys**: Set up your Reddit API credentials in Replit's Secrets
4. **Start the Application**: Click the "Run" button or use the command:
   ```bash
   python main.py
   ```
5. **Access the Application**: Open the web interface at the provided URL

### Using the Interface

#### Step 1: Enter Username
- Navigate to the main page
- Enter a Reddit username in the input field (without the "u/" prefix)
- Click "Analyze User" to start the analysis

#### Step 2: View Results
The results page provides comprehensive analytics organized into several sections:

**User Information**
- Account age and creation date
- Karma breakdown (post and comment karma)
- Account verification status

**Activity Timeline**
- Interactive chart showing posting frequency over time
- Daily breakdown of posts vs comments
- Activity patterns and trends

**Sentiment Analysis**
- Overall sentiment polarity (-1 to +1 scale)
- Positive, negative, and neutral content ratios
- Sentiment distribution visualization

**Top Keywords**
- Most frequently used words in comments
- Filtered to exclude common stop words and verbs
- Reveals main topics of interest

**Character Analysis**
- Personality traits based on posting behavior
- Communication style assessment
- Engagement level classification
- Primary subreddit communities

#### Step 3: Theme Customization
- Toggle between light and dark modes using the theme button
- Theme preference is saved across sessions
- Consistent theming between main and results pages

### API Endpoints

The application exposes the following endpoints:

- `GET /`: Main landing page with input form
- `GET /results`: Results page for displaying analytics
- `POST /results`: Redirects to results page with username parameter
- `POST /analyze`: API endpoint that performs the actual analysis

### Error Handling

The application includes comprehensive error handling for:
- Invalid or non-existent usernames
- API rate limiting
- Network connectivity issues
- Suspended or deleted accounts
- Insufficient data scenarios

### Performance Considerations

- **Rate Limiting**: Respects Reddit's API rate limits
- **Data Caching**: Efficient data processing to minimize API calls
- **Responsive Design**: Optimized for various screen sizes
- **Progressive Loading**: Shows loading states during analysis

## Development Notes

### Local Development
```bash
# Install dependencies
uv add praw textblob pandas

# Run development server
python main.py
```

### Deployment on Replit
The application is configured for seamless deployment on Replit with:
- Automatic dependency management
- Environment variable integration
- Production-ready Gunicorn configuration

### Contributing
1. Fork the repository
2. Make your changes
3. Test thoroughly with various Reddit usernames
4. Submit a pull request with detailed description

## License

This project is designed for educational and research purposes. Please respect Reddit's API terms of service and user privacy when using this tool.
