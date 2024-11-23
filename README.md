# Gmail Marketing Email Cleanup Tool

A Python tool to help you manage, unsubscribe from, and clean up marketing emails in your Gmail inbox.

## Features

- Identifies marketing emails by searching for "unsubscribe" patterns
- Analyzes email frequency by sender
- Finds unsubscribe links automatically
- Provides options to bulk delete emails from specific senders
- Helps manage unsubscribe process

## Prerequisites

- Python 3.7+
- A Google Cloud Project with Gmail API enabled
- OAuth 2.0 Client credentials

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/gmail-cleanup-tool.git
cd gmail-cleanup-tool
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the Gmail API
   - Create OAuth 2.0 Client ID credentials
   - Download credentials and save as `credentials.json` in the project directory
   - Set up authorized redirect URIs to include:
     * http://localhost:8080
     * http://localhost

## Usage

1. Run the script:
```bash
python gmail_cleanup.py
```

2. Follow the authentication prompt in your browser

3. For each sender of marketing emails, you'll have options to:
   - Delete all emails from that sender
   - Delete emails and open unsubscribe link
   - Skip to next sender

## Configuration

Edit `config.py` to customize:
- Maximum number of emails to analyze
- Search patterns for marketing emails
- Time range for email analysis

## Safety Features

- Confirmation before bulk deletions
- Preview mode available (set `DRY_RUN=True` in config.py)
- Rate limiting to avoid API quota issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Use this tool at your own risk. Always ensure you have backups of important emails before bulk deletions.