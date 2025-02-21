import os
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Access environment variables
email_sender = os.getenv('EMAIL_SENDER')
email_password = os.getenv('EMAIL_PASSWORD')
resume_path = os.getenv('RESUME_PATH')

# Validate that the environment variables are set
if not email_sender or not email_password or not resume_path:
    raise ValueError("Please ensure EMAIL_SENDER, EMAIL_PASSWORD, and RESUME_PATH are set in the .env file.")

def send_email(email_receiver, subject, body, email_sender, email_password, resume_path):
    """
    Send an email with a PDF resume attached.
    """
    # Create a MIMEMultipart message
    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.attach(MIMEText(body, 'plain'))  # Attach the email body

    # Attach the PDF resume
    with open(resume_path, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)  # Encode the attachment in base64
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{resume_path.split("/")[-1]}"'
        )
        em.attach(part)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

def scrape_job_details(job_id):
    """
    Scrape job title, email address, and status from a specific job posting.
    Returns tuple of (job_id, title, email, status)
    """
    url = f"https://seasonaljobs.dol.gov/jobs/{job_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job title
            title_tag = soup.find('h2', class_="text-primary-dark")
            job_title = title_tag.text.strip() if title_tag else None
            
            # Extract email
            email_label = soup.find('dt', text="Email address to Apply:")
            email = None
            if email_label and (email_tag := email_label.find_next_sibling('dd')):
                if email_link := email_tag.find('a'):
                    email = email_link['href'].replace('mailto:', '')
            
            # Check if the job is inactive
            inactive_tag = soup.find('span', class_="w-min text-sm text-red-700 border-red-700 border font-bold rounded-sm px-2 mt-2")
            if inactive_tag and inactive_tag.text.strip() == "INACTIVE":
                return job_id, None, None, None, "inactive"
            
            # Extract job status (e.g., "ACTIVE")
            active_tag = soup.find('span', class_="w-min text-sm text-green-700 border-green-700 border font-bold rounded-sm px-2 mt-2")
            job_status = active_tag.text.strip() if active_tag else "UNKNOWN"
            
            # Determine status
            if email and job_title:
                status = "success"
            elif email:
                status = "missing title"
            elif job_title:
                status = "missing email"
            else:
                status = "no data found"
                
            return job_id, job_title, email, job_status, status
        else:
            return job_id, None, None, None, f"HTTP {response.status_code}"
    except requests.RequestException as e:
        return job_id, None, None, None, f"error: {str(e)}"

def main():
    # Your list of job IDs
    data = [
    'H-400-25001-582200', 'H-400-25001-582249', 'H-400-25001-583468', 'H-400-25001-583482', 
    'H-400-25001-583498', 'H-400-25001-583504', 'H-400-25001-583522', 'H-400-25001-583561', 
    'H-400-25001-583589', 'H-400-25001-583613', 'H-400-25001-583630', 'H-400-25001-583648', 
    'H-400-25001-583545', 'H-400-24256-332593', 'H-400-24256-332616', 'H-400-24256-332633', 
    'H-400-24256-332660', 'H-400-24256-332669', 'H-400-24256-332757', 'H-400-25001-583275', 
    'H-400-24285-402459', 'H-400-24285-402494', 'H-400-24285-402518', 'H-400-24285-402547', 
    'H-400-25001-580700', 'H-400-25001-583517', 'H-400-25001-583638', 'H-400-25001-583640', 
    'H-400-25001-583657', 'H-400-25001-583661', 'H-400-25001-583747', 'H-400-25001-583889', 
    'H-400-25001-583929', 'H-400-25001-584096', 'H-400-25001-584774', 'H-400-25001-584777', 
    'H-400-25001-584783', 'H-400-25001-584784', 'H-400-25001-584793', 'H-400-25001-584796', 
    'H-400-25001-584797', 'H-400-25001-584806', 'H-400-25001-584808', 'H-400-25001-584813', 
    'H-400-25001-584816', 'H-400-25001-584825', 'H-400-25001-584829'
]

    
    # Dictionary to store results
    results = {}
    
    
    # Email body template
    body_template = """
Hello! I hope this email finds you well.

My name is Henrique, and I am very interested in this opportunity. I am familiar with many of the listed tasks. 
Additionally, I am fluent in English, allowing me to communicate effectively in the workplace.

I am available to start immediately if an H-2B or H-2A visa is sponsored, and I would love the opportunity 
to contribute to your team. I have attached my resume with more details about my experience and skills. 
Please let me know if you need any additional information.

Looking forward to your response.

Best regards,
Henrique Kutner Cordeiro
kutner.cordeiro@gmail.com
+55 11 98241-8368
"""
    
    # Process each job ID
    for job_id in data:
        print(f"\nProcessing {job_id}...")
        
        # Add delay to be respectful to the server
        time.sleep(1)
        
        # Scrape the job details
        job_id, title, email, job_status, status = scrape_job_details(job_id)
        
        # Skip inactive jobs
        if status == "inactive":
            print(f"Skipping {job_id} (INACTIVE)")
            continue
        
        # Store the results
        results[job_id] = {
            'title': title,
            'email': email,
            'job_status': job_status,
            'status': status
        }
        
        # Print progress
        print(f"Status: {status}")
        if title:
            print(f"Title found: {title}")
        if email:
            print(f"Email found: {email}")
        if job_status:
            print(f"Job Status: {job_status}")
        
        # Send email if email is found
        if email:
            # Customize the subject with the job title
            subject = f'{title}'
            
            # Personalize the email body
            personalized_body = body_template.format(job_title=title, job_id=job_id)
            
            try:
                send_email(email, subject, personalized_body, email_sender, email_password, resume_path)
                print(f"Email sent to {email}")
            except Exception as e:
                print(f"Failed to send email to {email}: {str(e)}")
    
    # Print final summary
    print("\nFinal Results:")
    print("-" * 50)
    successful = sum(1 for r in results.values() if r['email'] is not None and r['title'] is not None)
    partial = sum(1 for r in results.values() if (r['email'] is not None or r['title'] is not None) and not (r['email'] is not None and r['title'] is not None))
    print(f"Complete records (title + email): {successful}")
    print(f"Partial records (title or email): {partial}")
    print(f"Total jobs processed: {len(data)}")
    
    # Print all successful results
    print("\nDetailed Results:")
    for job_id, result in results.items():
        if result['title'] or result['email']:
            print(f"\nJob ID: {job_id}")
            if result['title']:
                print(f"Title: {result['title']}")
            if result['email']:
                print(f"Email: {result['email']}")
            if result['job_status']:
                print(f"Job Status: {result['job_status']}")

if __name__ == "__main__":
    main()