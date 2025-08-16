import os
import praw
import logging
import re
from datetime import datetime, timezone
from collections import defaultdict, Counter
from textblob import TextBlob
import pandas as pd

class RedditAnalyzer:
    def __init__(self):
        """Initialize Reddit API client"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.environ.get('REDDIT_CLIENT_ID', 'default_client_id'),
                client_secret=os.environ.get('REDDIT_CLIENT_SECRET', 'default_secret'),
                user_agent=os.environ.get('REDDIT_USER_AGENT', 'RedditUserAnalyzer/1.0')
            )
            # Test connection
            self.reddit.user.me()
        except Exception as e:
            logging.warning(f"Reddit API initialization failed: {str(e)}")
            self.reddit = None

    def analyze_user(self, username):
        """Perform comprehensive analysis of a Reddit user"""
        if not self.reddit:
            return {
                'success': False,
                'error': 'Reddit API not properly configured. Please check API credentials.'
            }
        
        try:
            # Get user object
            user = self.reddit.redditor(username)
            
            # Check if user exists
            try:
                user_created = user.created_utc
            except Exception:
                return {
                    'success': False,
                    'error': f'User "{username}" not found or account is suspended'
                }
            
            # Gather user data
            user_data = self._get_user_info(user)
            
            # Analyze posts and comments
            posts_data, comments_data = self._get_user_content(user)
            
            # Perform sentiment analysis
            sentiment_analysis = self._analyze_sentiment(posts_data, comments_data)
            
            # Create timeline data
            timeline_data = self._create_timeline(posts_data, comments_data)
            
            # Extract top keywords from comments
            top_keywords = self._extract_keywords(comments_data)
            
            # Generate character analysis
            character_analysis = self._analyze_character(sentiment_analysis, posts_data, comments_data)
            
            return {
                'success': True,
                'username': username,
                'user_info': user_data,
                'sentiment_analysis': sentiment_analysis,
                'timeline_data': timeline_data,
                'top_keywords': top_keywords,
                'character_analysis': character_analysis,
                'content_stats': {
                    'total_posts': len(posts_data),
                    'total_comments': len(comments_data),
                    'total_content': len(posts_data) + len(comments_data)
                }
            }
            
        except Exception as e:
            logging.error(f"Error analyzing user {username}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to analyze user: {str(e)}'
            }

    def _get_user_info(self, user):
        """Extract basic user information"""
        try:
            created_date = datetime.fromtimestamp(user.created_utc, tz=timezone.utc)
            account_age_days = (datetime.now(timezone.utc) - created_date).days
            
            return {
                'username': user.name,
                'post_karma': getattr(user, 'link_karma', 0),
                'comment_karma': getattr(user, 'comment_karma', 0),
                'total_karma': getattr(user, 'link_karma', 0) + getattr(user, 'comment_karma', 0),
                'account_created': created_date.strftime('%Y-%m-%d'),
                'account_age_days': account_age_days,
                'account_age_years': round(account_age_days / 365.25, 1),
                'is_verified': getattr(user, 'verified', False),
                'has_premium': getattr(user, 'is_gold', False)
            }
        except Exception as e:
            logging.error(f"Error getting user info: {str(e)}")
            return {}

    def _get_user_content(self, user, limit=100):
        """Retrieve user's posts and comments"""
        posts_data = []
        comments_data = []
        
        try:
            # Get recent posts
            for post in user.submissions.new(limit=limit):
                posts_data.append({
                    'id': post.id,
                    'title': post.title,
                    'text': getattr(post, 'selftext', ''),
                    'score': post.score,
                    'created_utc': post.created_utc,
                    'subreddit': str(post.subreddit),
                    'num_comments': post.num_comments,
                    'url': post.url if hasattr(post, 'url') else ''
                })
        except Exception as e:
            logging.error(f"Error fetching posts: {str(e)}")
        
        try:
            # Get recent comments
            for comment in user.comments.new(limit=limit):
                comments_data.append({
                    'id': comment.id,
                    'text': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'subreddit': str(comment.subreddit),
                    'parent_id': comment.parent_id
                })
        except Exception as e:
            logging.error(f"Error fetching comments: {str(e)}")
        
        return posts_data, comments_data

    def _analyze_sentiment(self, posts_data, comments_data):
        """Perform sentiment analysis on user content"""
        sentiments = []
        
        # Analyze posts
        for post in posts_data:
            text = f"{post['title']} {post['text']}"
            if text.strip():
                blob = TextBlob(text)
                sentiments.append({
                    'type': 'post',
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity,
                    'score': post['score'],
                    'created_utc': post['created_utc']
                })
        
        # Analyze comments
        for comment in comments_data:
            if comment['text'].strip() and comment['text'] != '[deleted]':
                blob = TextBlob(comment['text'])
                sentiments.append({
                    'type': 'comment',
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity,
                    'score': comment['score'],
                    'created_utc': comment['created_utc']
                })
        
        if not sentiments:
            return {
                'overall_polarity': 0,
                'overall_subjectivity': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'sentiment_distribution': []
            }
        
        # Calculate overall metrics
        avg_polarity = sum(s['polarity'] for s in sentiments) / len(sentiments)
        avg_subjectivity = sum(s['subjectivity'] for s in sentiments) / len(sentiments)
        
        # Calculate sentiment distribution
        positive = sum(1 for s in sentiments if s['polarity'] > 0.1)
        negative = sum(1 for s in sentiments if s['polarity'] < -0.1)
        neutral = len(sentiments) - positive - negative
        
        total = len(sentiments)
        
        return {
            'overall_polarity': round(avg_polarity, 3),
            'overall_subjectivity': round(avg_subjectivity, 3),
            'positive_ratio': round(positive / total * 100, 1),
            'negative_ratio': round(negative / total * 100, 1),
            'neutral_ratio': round(neutral / total * 100, 1),
            'sentiment_distribution': sentiments,
            'total_analyzed': total,
            'sentiment_summary': self._get_sentiment_summary({
                'overall_polarity': round(avg_polarity, 3),
                'positive_ratio': round(positive / total * 100, 1),
                'negative_ratio': round(negative / total * 100, 1)
            })
        }

    def _create_timeline(self, posts_data, comments_data):
        """Create timeline data for visualization"""
        timeline = defaultdict(lambda: {'posts': 0, 'comments': 0, 'total_score': 0})
        
        # Process posts
        for post in posts_data:
            date = datetime.fromtimestamp(post['created_utc']).strftime('%Y-%m-%d')
            timeline[date]['posts'] += 1
            timeline[date]['total_score'] += post['score']
        
        # Process comments
        for comment in comments_data:
            date = datetime.fromtimestamp(comment['created_utc']).strftime('%Y-%m-%d')
            timeline[date]['comments'] += 1
            timeline[date]['total_score'] += comment['score']
        
        # Convert to sorted list
        timeline_list = []
        for date, data in sorted(timeline.items()):
            timeline_list.append({
                'date': date,
                'posts': data['posts'],
                'comments': data['comments'],
                'total_activity': data['posts'] + data['comments'],
                'total_score': data['total_score']
            })
        
        return timeline_list

    def _extract_keywords(self, comments_data, top_n=10):
        """Extract top keywords from user comments"""
        if not comments_data:
            return []
        
        # Comprehensive stop words to exclude grammatical categories
        stop_words = {
            # Articles
            'the', 'a', 'an',
            
            # Prepositions
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 
            'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 
            'under', 'over', 'across', 'against', 'within', 'without', 'toward', 'towards', 
            'beside', 'behind', 'beneath', 'beyond', 'inside', 'outside', 'upon', 'underneath',
            'off', 'out', 'down', 'near', 'around', 'along', 'throughout', 'concerning',
            'regarding', 'despite', 'except', 'including', 'excluding', 'according',
            
            # Conjunctions
            'and', 'or', 'but', 'nor', 'yet', 'so', 'if', 'although', 'though', 'because', 
            'since', 'unless', 'while', 'whereas', 'however', 'therefore', 'moreover', 
            'furthermore', 'nevertheless', 'nonetheless', 'meanwhile', 'otherwise', 'hence',
            
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'hers', 'its', 'our', 'their', 'mine', 'yours', 'ours',
            'theirs', 'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves',
            'yourselves', 'themselves', 'this', 'that', 'these', 'those', 'who', 'whom',
            'whose', 'which', 'what', 'whoever', 'whomever', 'whatever', 'whichever',
            'someone', 'somebody', 'something', 'anyone', 'anybody', 'anything', 'everyone',
            'everybody', 'everything', 'no one', 'nobody', 'nothing', 'one', 'ones',
            
            # Auxiliary Verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'shall', 'can', 'ought', 'used', 'need', 'dare', 'am',
            
            # Adverbs of Degree/Frequency
            'very', 'quite', 'rather', 'too', 'so', 'enough', 'pretty', 'fairly', 'really',
            'extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'entirely',
            'always', 'never', 'often', 'sometimes', 'usually', 'frequently', 'rarely',
            'seldom', 'occasionally', 'constantly', 'continually', 'regularly', 'normally',
            'generally', 'typically', 'commonly', 'mostly', 'mainly', 'largely', 'mostly',
            'almost', 'nearly', 'barely', 'hardly', 'scarcely', 'just', 'only', 'even',
            'still', 'yet', 'already', 'soon', 'later', 'now', 'then', 'here', 'there',
            'everywhere', 'somewhere', 'anywhere', 'nowhere',
            
            # Interjections/Filler Words
            'oh', 'ah', 'wow', 'hey', 'well', 'um', 'uh', 'hmm', 'yeah', 'yes', 'no', 'okay',
            'ok', 'sure', 'right', 'like', 'actually', 'basically', 'literally', 'seriously',
            'honestly', 'obviously', 'clearly', 'definitely', 'probably', 'maybe', 'perhaps',
            'possibly', 'certainly', 'surely', 'indeed', 'truly', 'really', 'quite', 'rather',
            
            # Negations and Contractions
            'not', 'don\'t', 'doesn\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 'can\'t', 'couldn\'t',
            'shouldn\'t', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 'haven\'t', 'hasn\'t',
            'hadn\'t', 'mustn\'t', 'needn\'t', 'daren\'t', 'shan\'t', 'ain\'t',
            
            # Politeness and Social Words
            'thank', 'thanks', 'thank you', 'please', 'sorry', 'excuse', 'pardon', 'welcome',
            'hello', 'hi', 'bye', 'goodbye', 'farewell', 'greetings', 'cheers', 'regards',
            
            # Emphasis and Agreement Words
            'exactly', 'absolutely', 'totally', 'completely', 'perfectly', 'precisely',
            'correct', 'right', 'true', 'false', 'wrong', 'agree', 'disagree', 'yep', 'nope',
            'uh-huh', 'mm-hmm', 'yup', 'nah', 'yeah', 'yea', 'aye',
            
            # Internet Slang and Abbreviations
            'lol', 'lmao', 'rofl', 'omg', 'wtf', 'tbh', 'imo', 'imho', 'fyi', 'btw', 'aka',
            'etc', 'ie', 'eg', 'vs', 'tho', 'thru', 'ur', 'u', 'r', 'n', 'w/', 'w/o',
            
            # Comprehensive Verb Filtering - All Types of Verbs
            # Action Verbs - Physical Actions
            'walk', 'run', 'jump', 'sit', 'stand', 'move', 'dance', 'swim', 'fly', 'drive',
            'ride', 'climb', 'fall', 'drop', 'lift', 'carry', 'hold', 'grab', 'push', 'pull',
            'throw', 'catch', 'kick', 'hit', 'touch', 'reach', 'stretch', 'bend', 'turn',
            'open', 'close', 'lock', 'unlock', 'enter', 'exit', 'arrive', 'leave', 'return',
            
            # Action Verbs - Mental Actions
            'think', 'know', 'understand', 'remember', 'forget', 'learn', 'study', 'teach',
            'believe', 'doubt', 'wonder', 'imagine', 'dream', 'hope', 'wish', 'want', 'need',
            'love', 'hate', 'like', 'dislike', 'prefer', 'choose', 'decide', 'plan', 'intend',
            'expect', 'assume', 'suppose', 'guess', 'realize', 'recognize', 'notice', 'observe',
            
            # Action Verbs - Communication
            'say', 'tell', 'speak', 'talk', 'whisper', 'shout', 'yell', 'scream', 'call',
            'ask', 'answer', 'reply', 'respond', 'explain', 'describe', 'mention', 'announce',
            'declare', 'state', 'claim', 'argue', 'discuss', 'debate', 'complain', 'suggest',
            'recommend', 'advise', 'warn', 'promise', 'threaten', 'invite', 'request', 'demand',
            
            # Action Verbs - Creation/Destruction
            'make', 'create', 'build', 'construct', 'produce', 'generate', 'develop', 'design',
            'write', 'draw', 'paint', 'compose', 'form', 'shape', 'mold', 'craft', 'cook',
            'bake', 'prepare', 'fix', 'repair', 'restore', 'break', 'destroy', 'damage',
            'ruin', 'demolish', 'tear', 'cut', 'slice', 'chop', 'burn', 'melt', 'freeze',
            
            # Action Verbs - Possession/Transfer
            'have', 'own', 'possess', 'get', 'obtain', 'acquire', 'receive', 'take', 'give',
            'offer', 'provide', 'supply', 'deliver', 'send', 'bring', 'fetch', 'collect',
            'gather', 'save', 'keep', 'store', 'hide', 'lose', 'find', 'discover', 'locate',
            'buy', 'sell', 'trade', 'exchange', 'share', 'lend', 'borrow', 'rent', 'lease',
            
            # Action Verbs - Senses and Perception
            'see', 'look', 'watch', 'stare', 'glance', 'peek', 'observe', 'view', 'notice',
            'hear', 'listen', 'sound', 'smell', 'taste', 'feel', 'touch', 'sense', 'perceive',
            
            # Action Verbs - Technology and Work
            'work', 'operate', 'function', 'run', 'start', 'stop', 'pause', 'continue', 'finish',
            'complete', 'begin', 'end', 'play', 'record', 'save', 'load', 'download', 'upload',
            'install', 'update', 'delete', 'remove', 'add', 'insert', 'copy', 'paste', 'edit',
            'modify', 'change', 'adjust', 'configure', 'setup', 'connect', 'disconnect', 'sync',
            
            # Linking Verbs and State of Being
            'be', 'am', 'is', 'are', 'was', 'were', 'being', 'been', 'become', 'seem', 'appear',
            'look', 'sound', 'smell', 'taste', 'feel', 'remain', 'stay', 'grow', 'turn', 'get',
            'prove', 'act', 'serve', 'represent', 'constitute', 'equal', 'measure', 'weigh',
            
            # Helping/Auxiliary Verbs (already included above but ensuring completeness)
            'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could', 'ought',
            'do', 'does', 'did', 'have', 'has', 'had', 'let', 'help', 'allow', 'permit', 'enable',
            
            # Action Verbs - Social Interactions
            'meet', 'greet', 'visit', 'join', 'participate', 'attend', 'celebrate', 'party',
            'marry', 'divorce', 'date', 'befriend', 'follow', 'lead', 'guide', 'support',
            'help', 'assist', 'serve', 'cooperate', 'collaborate', 'compete', 'fight', 'argue',
            'apologize', 'forgive', 'blame', 'accuse', 'defend', 'protect', 'attack', 'threaten',
            
            # Action Verbs - Emotional/Mental States
            'worry', 'fear', 'panic', 'relax', 'calm', 'enjoy', 'suffer', 'struggle', 'cope',
            'manage', 'handle', 'deal', 'face', 'confront', 'avoid', 'escape', 'flee', 'hide',
            'ignore', 'acknowledge', 'accept', 'reject', 'approve', 'disapprove', 'appreciate',
            'value', 'respect', 'admire', 'envy', 'jealous', 'proud', 'ashamed', 'embarrassed',
            
            # Action Verbs - Time and Process
            'happen', 'occur', 'take place', 'last', 'continue', 'proceed', 'advance', 'progress',
            'develop', 'evolve', 'mature', 'age', 'expire', 'end', 'conclude', 'result', 'cause',
            'lead', 'contribute', 'influence', 'affect', 'impact', 'determine', 'control', 'manage',
            
            # Action Verbs - Movement and Direction
            'travel', 'journey', 'migrate', 'wander', 'roam', 'explore', 'navigate', 'direct',
            'guide', 'lead', 'follow', 'chase', 'pursue', 'hunt', 'search', 'seek', 'find',
            'approach', 'retreat', 'advance', 'withdraw', 'emerge', 'surface', 'dive', 'sink',
            
            # Action Verbs - Health and Body
            'eat', 'drink', 'swallow', 'chew', 'bite', 'taste', 'digest', 'breathe', 'inhale',
            'exhale', 'cough', 'sneeze', 'yawn', 'sleep', 'wake', 'rest', 'exercise', 'stretch',
            'hurt', 'heal', 'recover', 'improve', 'worsen', 'suffer', 'ache', 'bleed', 'bruise',
            
            # Numbers and basic descriptors that don't add context
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'first', 'second', 'third', 'last', 'next', 'previous', 'another', 'other',
            'same', 'different', 'new', 'old', 'young', 'big', 'small', 'large', 'little',
            'good', 'bad', 'best', 'worst', 'better', 'worse', 'great', 'nice', 'fine',
            'long', 'short', 'high', 'low', 'much', 'many', 'few', 'more', 'most', 'less',
            'least', 'all', 'some', 'any', 'each', 'every', 'both', 'either', 'neither',
            'such', 'own', 'back', 'way', 'also', 'too', 'either'
        }
        
        # Collect all comment text
        all_text = ' '.join([comment['text'] for comment in comments_data 
                            if comment['text'] and comment['text'] != '[deleted]'])
        
        if not all_text.strip():
            return []
        
        # Clean and tokenize text
        # Remove URLs, mentions, and special characters
        cleaned_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', all_text)
        cleaned_text = re.sub(r'u/\w+', '', cleaned_text)  # Remove user mentions
        cleaned_text = re.sub(r'r/\w+', '', cleaned_text)  # Remove subreddit mentions
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', cleaned_text)  # Remove non-alphabetic characters
        
        # Convert to lowercase and split into words
        words = cleaned_text.lower().split()
        
        # Filter out stop words and short words
        filtered_words = [word for word in words 
                         if len(word) > 2 and word not in stop_words]
        
        # Count word frequency
        word_counter = Counter(filtered_words)
        
        # Get top keywords with their counts
        top_keywords = []
        for word, count in word_counter.most_common(top_n):
            top_keywords.append({
                'word': word,
                'count': count
            })
        
        return top_keywords

    def _analyze_character(self, sentiment_analysis, posts_data, comments_data):
        """Generate character analysis based on user behavior"""
        if not sentiment_analysis or sentiment_analysis['total_analyzed'] == 0:
            return {
                'personality_traits': ['Insufficient data for analysis'],
                'communication_style': 'Unknown',
                'engagement_level': 'Unknown',
                'content_focus': []
            }
        
        traits = []
        
        # Analyze sentiment patterns
        polarity = sentiment_analysis['overall_polarity']
        subjectivity = sentiment_analysis['overall_subjectivity']
        
        if polarity > 0.2:
            traits.append('Optimistic')
        elif polarity < -0.2:
            traits.append('Critical')
        else:
            traits.append('Balanced')
        
        if subjectivity > 0.6:
            traits.append('Opinionated')
        elif subjectivity < 0.3:
            traits.append('Factual')
        else:
            traits.append('Moderate')
        
        # Analyze posting patterns
        total_posts = len(posts_data)
        total_comments = len(comments_data)
        
        if total_posts > total_comments:
            traits.append('Content Creator')
        elif total_comments > total_posts * 3:
            traits.append('Active Commenter')
        
        # Determine communication style
        if subjectivity > 0.7:
            communication_style = 'Expressive and Personal'
        elif subjectivity < 0.3:
            communication_style = 'Objective and Factual'
        else:
            communication_style = 'Balanced and Thoughtful'
        
        # Determine engagement level
        total_activity = total_posts + total_comments
        if total_activity > 50:
            engagement_level = 'Highly Active'
        elif total_activity > 20:
            engagement_level = 'Moderately Active'
        else:
            engagement_level = 'Casual User'
        
        # Analyze content focus (top subreddits)
        subreddit_counter = Counter()
        for post in posts_data:
            subreddit_counter[post['subreddit']] += 1
        for comment in comments_data:
            subreddit_counter[comment['subreddit']] += 1
        
        content_focus = [subreddit for subreddit, _ in subreddit_counter.most_common(5)]
        
        return {
            'personality_traits': traits,
            'communication_style': communication_style,
            'engagement_level': engagement_level,
            'content_focus': content_focus
        }
    
    def _get_sentiment_summary(self, sentiment_analysis):
        """Generate a human-readable sentiment summary"""
        polarity = sentiment_analysis['overall_polarity']
        positive_ratio = sentiment_analysis['positive_ratio']
        
        if polarity > 0.3:
            return f"Generally positive outlook ({positive_ratio:.1f}% positive content)"
        elif polarity < -0.3:
            return f"Tends toward criticism ({sentiment_analysis['negative_ratio']:.1f}% negative content)"
        else:
            return f"Balanced perspective ({positive_ratio:.1f}% positive, {sentiment_analysis['negative_ratio']:.1f}% negative)"
