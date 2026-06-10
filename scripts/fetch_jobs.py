import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

# Job boards to scrape (or use their APIs)
SEARCH_TERMS = [
    "async remote enablement",
    "async remote operations",
    "async remote documentation",
    "async remote product operations"
]

def fetch_jobs():
    """Fetch jobs from Indeed, LinkedIn, or use job board APIs"""
    jobs = []
    
    # Example: Scrape Indeed (or use their API if you have access)
    for term in SEARCH_TERMS:
        # This is pseudocode - you'd use a job API or web scraping
        url = f"https://www.indeed.com/jobs?q={term}+remote+async"
        # Fetch and parse results
        pass
    
    return jobs

def send_email(jobs):
    """Send formatted job list to your email"""
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    # Build email
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Daily Async Remote Jobs - {datetime.now().strftime('%B %d')}"
    message["From"] = sender
    message["To"] = recipient
    
    # Format job list as HTML
    html = "<h2>Today's Async Remote Jobs</h2><ul>"
    for job in jobs:
        html += f"""
        <li>
            <strong>{job['title']}</strong> @ {job['company']} | {job['salary']}<br>
            {job['description']}<br>
            <a href="{job['link']}">Apply →</a>
        </li>
        """
    html += "</ul>"
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    # Send via Gmail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())
    
    print(f"✅ Email sent to {recipient}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    if jobs:
        send_email(jobs)
    else:
        print("No jobs found today")
