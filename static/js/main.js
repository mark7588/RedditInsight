// Reddit User Analyzer JavaScript

let timelineChart = null;

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const loadingState = document.getElementById('loadingState');
    const errorAlert = document.getElementById('errorAlert');
    const resultsContainer = document.getElementById('resultsContainer');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        analyzeUser();
    });
});

async function analyzeUser() {
    const username = document.getElementById('username').value.trim();
    
    if (!username) {
        showError('Please enter a valid Reddit username');
        return;
    }

    // Show loading state
    showLoading();
    hideError();
    hideResults();

    try {
        const formData = new FormData();
        formData.append('username', username);

        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Analysis failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error occurred. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayResults(data) {
    // Populate user overview
    document.getElementById('analyzedUsername').textContent = data.username;
    document.getElementById('totalKarma').textContent = data.user_info.total_karma.toLocaleString();
    document.getElementById('postKarma').textContent = data.user_info.post_karma.toLocaleString();
    document.getElementById('commentKarma').textContent = data.user_info.comment_karma.toLocaleString();
    document.getElementById('accountAge').textContent = data.user_info.account_age_years;
    document.getElementById('accountCreated').textContent = data.user_info.account_created;
    document.getElementById('totalPosts').textContent = data.content_stats.total_posts;
    document.getElementById('totalComments').textContent = data.content_stats.total_comments;

    // Display sentiment analysis
    displaySentimentAnalysis(data.sentiment_analysis);

    // Create timeline chart
    createTimelineChart(data.timeline_data);

    // Display character analysis
    displayCharacterAnalysis(data.character_analysis);

    // Show results
    showResults();
}

function displaySentimentAnalysis(sentiment) {
    const polarity = sentiment.overall_polarity;
    const subjectivity = sentiment.overall_subjectivity;

    // Update sentiment bars
    const sentimentBar = document.getElementById('sentimentBar');
    const sentimentPercentage = ((polarity + 1) / 2) * 100; // Convert -1 to 1 range to 0-100%
    sentimentBar.style.width = sentimentPercentage + '%';
    
    // Color code sentiment
    if (polarity > 0.1) {
        sentimentBar.className = 'progress-bar bg-success';
    } else if (polarity < -0.1) {
        sentimentBar.className = 'progress-bar bg-danger';
    } else {
        sentimentBar.className = 'progress-bar bg-secondary';
    }

    document.getElementById('sentimentPolarity').textContent = polarity.toFixed(3);

    // Update subjectivity bar
    const subjectivityBar = document.getElementById('subjectivityBar');
    subjectivityBar.style.width = (subjectivity * 100) + '%';
    document.getElementById('subjectivityScore').textContent = subjectivity.toFixed(3);

    // Update ratios
    document.getElementById('positiveRatio').textContent = sentiment.positive_ratio + '%';
    document.getElementById('neutralRatio').textContent = sentiment.neutral_ratio + '%';
    document.getElementById('negativeRatio').textContent = sentiment.negative_ratio + '%';
}

function createTimelineChart(timelineData) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (timelineChart) {
        timelineChart.destroy();
    }

    const labels = timelineData.map(item => item.date);
    const posts = timelineData.map(item => item.posts);
    const comments = timelineData.map(item => item.comments);
    const totalActivity = timelineData.map(item => item.total_activity);

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Posts',
                    data: posts,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Comments',
                    data: comments,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Total Activity',
                    data: totalActivity,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Activity Count'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'User Activity Over Time'
                }
            }
        }
    });
}



function displayCharacterAnalysis(character) {
    // Display personality traits
    const traitsContainer = document.getElementById('personalityTraits');
    traitsContainer.innerHTML = '';
    character.personality_traits.forEach(trait => {
        const badge = document.createElement('span');
        badge.className = 'trait-badge';
        badge.textContent = trait;
        traitsContainer.appendChild(badge);
    });

    // Display content focus (top subreddits)
    const focusContainer = document.getElementById('contentFocus');
    focusContainer.innerHTML = '';
    character.content_focus.forEach(subreddit => {
        const badge = document.createElement('span');
        badge.className = 'subreddit-badge';
        badge.textContent = 'r/' + subreddit;
        focusContainer.appendChild(badge);
    });

    // Display other character info
    document.getElementById('communicationStyle').textContent = character.communication_style;
    document.getElementById('engagementLevel').textContent = character.engagement_level;
    document.getElementById('sentimentSummary').textContent = character.sentiment_summary;
}

function showLoading() {
    document.getElementById('loadingState').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('d-none');
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorAlert').classList.remove('d-none');
}

function hideError() {
    document.getElementById('errorAlert').classList.add('d-none');
}

function showResults() {
    document.getElementById('resultsContainer').classList.remove('d-none');
    document.getElementById('resultsContainer').classList.add('fade-in');
}

function hideResults() {
    document.getElementById('resultsContainer').classList.add('d-none');
}

// Utility function to format large numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}
