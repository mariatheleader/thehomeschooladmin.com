import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def fetch_jobs():
    """Fetch jobs from Himalayas API (FREE, no auth needed)"""
    
    url = "https://api.himalayas.app/v1/jobs"
    
    # Your search terms
    queries = [
        "enablement",
        "operations", 
        "documentation",
        "product operations",
        "learning operations"
    ]
    
    all_jobs = []
    
    for query in queries:
        params = {
            "search": query,
            "employment_type": "Full-time",
            "remote": "true"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            for job in data.get("jobs", [])[:10]:  # Get first 10 per search
                all_jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": job.get("company_name", "N/A"),
                    "location": job.get("location", "Remote"),
                    "salary": job.get("salary_range", "Competitive"),
                    "description": job.get("description", "")[:250],
                    "link": job.get("job_url", "#"),
                    "posted": job.get("published_at", "Today")
                })
        except Exception as e:
            print(f"Error fetching {query}: {e}")
    
    # Remove duplicates
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        if job["link"] not in seen:
            seen.add(job["link"])
            unique_jobs.append(job)
    
    return unique_jobs

def send_email(jobs):
    """Send jobs to your email"""
    
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🎯 Today's Async Remote Jobs - {datetime.now().strftime('%B %d, %Y')}"
    message["From"] = sender
    message["To"] = recipient
    
    # Build HTML email
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">📧 Async Remote Jobs Posted Today</h2>
            <p>Found <strong>{len(jobs)}</strong> new opportunities matching your profile.</p>
    """
    
    if jobs:
        html += "<ul style='list-style: none; padding: 0;'>"
        for i, job in enumerate(jobs, 1):
            html += f"""
            <li style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
                <strong style="font-size: 16px;">#{i} {job['title']}</strong><br>
                <span style="color: #7f8c8d;"><strong>{job['company']}</strong> • {job['location']}</span><br>
                <span style="color: #27ae60; font-weight: bold;">{job['salary']}</span><br>
                <p style="margin: 10px 0; font-size: 14px;">{job['description']}...</p>
                <a href="{job['link']}" style="display: inline-block; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px;">Apply Now →</a>
            </li>
            """
        html += "</ul>"
    else:
        html += "<p>No jobs found today. Check back tomorrow!</p>"
    
    html += """
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #95a5a6;">
                This email was generated automatically by your GitHub Actions workflow.
            </p>
        </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    # Send via Gmail
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())
    
    print(f"✅ Email sent! {len(jobs)} jobs included")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
