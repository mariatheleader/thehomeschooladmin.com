import requests
import os
from datetime import datetime

def fetch_jobs():
    """Fetch jobs from Remotive API"""
    
    jobs = []
    
    target_keywords = [
        "enablement", "operations", "workflow", "implementation", 
        "customer success", "program manager", "documentation",
        "learning", "content operations", "customer education", "product operations"
    ]
    
    exclude_keywords = [
        "sales", "engineer", "developer", "designer", "support", "retail",
        "delivery", "warehouse", "hospitality", "caretaker", "devops"
    ]
    
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {"limit": 100}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"API returned status {response.status_code}")
            return []
        
        data = response.json()
        
        for job in data.get("jobs", []):
            title = (job.get("title") or "").lower()
            
            has_target = any(keyword in title for keyword in target_keywords)
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            
            if has_target and not has_exclude:
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": job.get("company_name", "N/A"),
                    "location": job.get("candidate_required_location", "Remote"),
                    "salary": job.get("salary") or "Not listed",
                    "description": (job.get("description") or "No description")[:150],
                    "url": job.get("url", "#"),
                    "company_url": job.get("company_url", ""),
                })
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []
    
    return jobs[:20]

def send_email_sendgrid(jobs):
    """Send via SendGrid"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = "maria@thehomeschooladmin.com"
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                📧 Today's Async Remote Jobs
            </h2>
            <p style="font-size: 16px; color: #555;">
                Found <strong>{len(jobs)}</strong> qualified opportunities.
            </p>
    """
    
    if jobs:
        for i, job in enumerate(jobs, 1):
            company_link = f'<a href="{job["company_url"]}" style="color: #0645ad;">{job["company"]}</a>' if job["company_url"] else job["company"]
            
            html += f"""
            <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
                <p style="margin: 0 0 8px 0;">
                    <strong style="font-size: 16px;">{i}. {job['title']}</strong>
                </p>
                <p style="margin: 0 0 5px 0; color: #555;">
                    <strong>Company:</strong> {company_link}
                </p>
                <p style="margin: 0 0 5px 0; color: #555;">
                    <strong>Location:</strong> {job['location']} | <strong>Salary:</strong> {job['salary']}
                </p>
                <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">
                    {job['description']}
                </p>
                <a href="{job['url']}" style="display: inline-block; padding: 8px 14px; background: #3498db; color: white; text-decoration: none; border-radius: 4px;">
                    Apply →
                </a>
            </div>
            """
    else:
        html += "<p>No matching jobs found today.</p>"
    
    html += """
        </body>
    </html>
    """
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "personalizations": [{
            "to": [{"email": "maria.galyean.work@gmail.com"}]
        }],
        "from": {"email": sender_email},
        "subject": f"🎯 Async Remote Jobs - {datetime.now().strftime('%B %d')}",
        "content": [{
            "type": "text/html",
            "value": html
        }]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 202:
        print(f"✅ Email sent! {len(jobs)} jobs")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email_sendgrid(jobs)
