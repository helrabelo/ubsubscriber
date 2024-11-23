"""Configuration settings for Gmail Cleanup Tool."""

# API Settings
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

# Search Settings
MAX_RESULTS = 50
SEARCH_PATTERNS = [
    'unsubscribe',
    '"opt out"',
    '"email preferences"'
]
SEARCH_QUERY = ' OR '.join(SEARCH_PATTERNS)
RATE_LIMIT_DELAY = 0.5 

# Operation Settings
DRY_RUN = False  # Set to True to prevent actual deletions
RATE_LIMIT_DELAY = 1  # Seconds between API calls
MAX_RETRIES = 3  # Number of retries for failed API calls

# Time Range Settings (in days, 0 for no limit)
EMAIL_AGE_LIMIT = 0

# Unsubscribe Settings
AUTO_OPEN_LINKS = True  # Whether to automatically open unsubscribe links
UNSUBSCRIBE_PATTERNS = [
    r'unsubscribe',
    r'opt.?out',
    r'subscription.*preferences',
]