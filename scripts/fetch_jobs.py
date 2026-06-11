import requests
import os
from datetime import datetime
from urllib.parse import urlparse

def fetch_jobs():
    """Fetch jobs from multiple sources with strict filtering"""
    
    jobs = []
    
    # Keywords that signal YOUR roles
    target_keywords = [
        "enablement", "operations", "workflow", "implementation", 
        "customer success", "product operations", "documentation",
        "program manager", "project manager", "learning", "curriculum",
        "content operations", "customer education"
    ]
    
    # Keywords to EXCLUDE
    exclude_keywords = [
        "sales", "support", "engineer", "developer", "devops", "frontend",
        "backend", "full stack", "designer", "ux", "ui", "data science",
        "caretaker", "delivery", "postie", "warehouse", "retail", "hospitality"
    ]
    
    # ===== WE WORK REMOTELY API =====
    try:
        url = "https://weworkremotely.com/api/v2/remote_jobs?limit=50"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        for job in data.get("remote_jobs", []):
            title = job.get("title", "").lower()
            company = job.get("company_name", "N/A")
            
            # Check if matches target AND doesn't match exclude
            has_target = any(keyword in title for keyword in target_keywords)
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            
            if has_target and not has_exclude:
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": company,
                    "location": job.get("location", "Remote"),
                    "salary": job.get("salary") or "Not listed",
                    "description": job.get("description", "")[:200],
                    "url": job.get("url", "#"),
                    "company_url": job.get("company_url", ""),
                    "posted": job.get("published_at", "Today"),
                    "source": "We Work Remotely"
                })
    except Exception as e:
        print(f"Error fetching We Work Remotely: {e}")
    
    # ===== REMOTIVE API (BETTER FILTERING) =====
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {
            "limit": 100,
            "category": "other"  # Gets non-engineering roles
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        for job in data.get("jobs", []):
            title = job.get("title", "").lower()
            company = job.get("company_name", "N/A")
            
            has_target = any(keyword in title for keyword in target_keywords)
            has_exclude = any(keyword in title for keyword in exclude_keywords)
            
            if has_target and not has_exclude:
                jobs.append({
                    "title": job.get("title", "N/A"),
                    "company": company,
                    "location": job.get("candidate_required_location", "Remote"),
                    "salary": job.get("salary") or "Not listed",
                    "description": job.get("description", "")[:200],
                    "url": job.get("url", "#"),
                    "company_url": job.get("company_url", ""),
                    "posted": job.get("published_at", "Today"),
                    "source": "Remotive"
                })
    except Exception as e:
        print(f"Error fetching Remotive: {e}")
    
    # Remove duplicates by URL
    seen = set()
    unique_jobs = []
    for job in jobs:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique_jobs.append(job)
    
    return unique_jobs[:20]  # Return top 20

def send_email_sendgrid(jobs):
    """Send via SendGrid with better formatting"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                📧 Today's Async Remote Jobs
            </h2>
            <p style="font-size: 16px; color: #555;">
                Found <strong>{len(jobs)}</strong> qualified opportunities for you.
            </p>
    """
    
    if jobs:
        for i, job in enumerate(jobs, 1):
            company_link = f'<a href="{job["company_url"]}" style="color: #0645ad;">{job["company"]}</a>' if job["company_url"] else job["company"]
            
            html += f"""
            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
                <p style="margin: 0 0 8px 0;">
                    <strong style="font-size: 18px; color: #000;">#{i} {job['title']}</strong>
                </p>
                <p style="margin: 0 0 8px 0; color: #555;">
                    <strong>Company:</strong> {company_link}
                </p>
                <p style="margin: 0 0 8px 0; color: #555;">
                    <strong>Location:</strong> {job['location']} | <strong>Salary:</strong> {job['salary']}
                </p>
                <p style="margin: 0 0 12px 0; color: #666; font-size: 14px;">
                    {job['description']}...
                </p>
                <p style="margin: 0;">
                    <a href="{job['url']}" style="display: inline-block; padding: 10px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
                        View & Apply →
                    </a>
                </p>
                <p style="margin: 8px 0 0 0; font-size: 12px; color: #999;">
                    Posted on {job['source']}
                </p>
            </div>
            """
    else:
        html += "<p style='color: #999;'>No matching jobs found today. Check back tomorrow!</p>"
    
    html += """
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #999; margin-top: 20px;">
                This is an automated daily job alert. You can customize the search terms by editing the Python script.
            </p>
        </body>
    </html>
    """
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "personalizations": [
            {
                "to": [{"email": "maria.galyean.work@gmail.com"}]
            }
        ],
        "from": {"email": "maria.galyean.work@gmail.com", "name": "Job Alert Bot"},
        "subject": f"🎯 Async Remote Jobs - {datetime.now().strftime('%B %d, %Y')}",
        "content": [
            {
                "type": "text/html",
                "value": html
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 202:
        print(f"✅ Email sent! {len(jobs)} jobs included")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email_sendgrid(jobs)
