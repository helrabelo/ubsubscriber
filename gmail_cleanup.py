"""Main script for Gmail Marketing Email Cleanup Tool."""

import os
import pickle
import time
import re
from collections import defaultdict
from typing import Dict, Set, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

import config

class GmailCleanupTool:
    def __init__(self):
        self.service = None
        self.sender_stats = defaultdict(lambda: {'count': 0, 'unsubscribe_links': set()})

    def authenticate(self) -> None:
        """Handle Gmail API authentication."""
        creds = None
        if os.path.exists(config.TOKEN_FILE):
            with open(config.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Missing {config.CREDENTIALS_FILE}. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE, config.SCOPES)
                creds = flow.run_local_server(port=8080)

            with open(config.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def analyze_marketing_emails(self) -> None:
        """Analyze inbox for marketing emails."""
        try:
            print("Analyzing marketing emails...")
            results = self.service.users().messages().list(
                userId='me',
                q=config.SEARCH_QUERY,
                maxResults=config.MAX_RESULTS
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                print("No marketing emails found!")
                return

            total = len(messages)
            print(f"Found {total} potential marketing emails")

            for i, message in enumerate(messages, 1):
                print(f"\rProcessing email {i}/{total}...", end='', flush=True)
                
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = msg['payload']['headers']
                sender = next(h['value'] for h in headers if h['name'] == 'From')

                # Get email body
                if 'parts' in msg['payload']:
                    body = msg['payload']['parts'][0]['body'].get('data', '')
                else:
                    body = msg['payload']['body'].get('data', '')

                unsubscribe_links = self.find_unsubscribe_links(body)
                
                self.sender_stats[sender]['count'] += 1
                self.sender_stats[sender]['unsubscribe_links'].update(unsubscribe_links)

                time.sleep(config.RATE_LIMIT_DELAY)

            print("\nAnalysis complete! Processing results...")

        except HttpError as error:
            print(f"An error occurred: {error}")

    def find_unsubscribe_links(self, email_body: str) -> Set[str]:
        """Extract unsubscribe links from email body."""
        soup = BeautifulSoup(email_body, 'html.parser')
        unsubscribe_links = set()

        # Fix the deprecation warning
        for pattern in config.UNSUBSCRIBE_PATTERNS:
            links = soup.find_all('a', href=True, string=re.compile(pattern, re.I))
            unsubscribe_links.update(link['href'] for link in links)

        # Check List-Unsubscribe header links
        header_links = soup.find_all('a', href=True, attrs={'data-saferedirecturl': True})
        unsubscribe_links.update(link['href'] for link in header_links)

        return unsubscribe_links
    def process_emails(self) -> None:
        """Process emails based on user input."""
        print("\nSender Summary:")
        print("-" * 50)

        for sender, stats in sorted(
            self.sender_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        ):
            print(f"\nSender: {sender}")
            print(f"Email count: {stats['count']}")

            if stats['unsubscribe_links']:
                print("Unsubscribe links found:")
                for link in stats['unsubscribe_links']:
                    print(f"- {link}")

            while True:
                action = input(
                    "\nWhat would you like to do with emails from this sender?\n"
                    "1: Delete all\n"
                    "2: Delete and open unsubscribe link\n"
                    "3: Skip\n"
                    "Choice (1-3): "
                )

                if action in ['1', '2', '3']:
                    break
                print("Invalid choice. Please enter 1, 2, or 3.")

            if action in ['1', '2']:
                self.delete_emails(sender)
                
                if action == '2' and stats['unsubscribe_links'] and config.AUTO_OPEN_LINKS:
                    print("Please check your browser for the unsubscribe page.")
                    # Note: In production, you'd want to use a proper browser automation
                    # library to handle the unsubscribe process

            time.sleep(config.RATE_LIMIT_DELAY)

    def delete_emails(self, sender: str) -> None:
        """Delete all emails from a specific sender."""
        if config.DRY_RUN:
            print(f"[DRY RUN] Would delete emails from: {sender}")
            return

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=f'from:{sender}'
            ).execute()

            messages = results.get('messages', [])
            if messages:
                print(f"Deleting {len(messages)} emails from {sender}...")
                for msg in messages:
                    self.service.users().messages().trash(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    time.sleep(config.RATE_LIMIT_DELAY)
                print("Deletion complete!")
            else:
                print("No messages found to delete.")

        except HttpError as error:
            print(f"An error occurred while deleting emails: {error}")

def main():
    """Main function to run the Gmail Cleanup Tool."""
    try:
        tool = GmailCleanupTool()
        tool.authenticate()
        tool.analyze_marketing_emails()
        tool.process_emails()
        print("\nCleanup completed!")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == '__main__':
    main()