import os
import json
import re
import requests
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from pdfminer.high_level import extract_text

# AppSheet API Configuration
APPSHEET_APP_ID = "1f1a1702-e3f7-40aa-b5c2-43a44f373086"
APPSHEET_ACCESS_KEY = "V2-pL7rg-a3jss-c4SVT-9reJ9-4FHk4-MLRb1-OhrpE-3vOyJ"
APPSHEET_TABLE_NAME = "Parser to Data Entry test"

# Path to store extracted data in Excel
EXCEL_FILE_PATH = "uploads/Parser_to_Data_Entry_test.xlsx"

def extract_resume_text(pdf_path):
    """Extract text from a PDF resume."""
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def process_resume_content(extracted_text):
    """Process extracted text into structured data"""
    sections = {
        'education': ['education', 'academic background', 'qualifications'],
        'work_experience': ['work experience', 'professional experience', 'employment history'],
        'skills': ['skills', 'technical skills', 'skill set'],
        'certifications': ['certifications', 'certificates'],
        'languages': ['languages']
    }

    resume_data = {
        'candidate_name': None,
        'email_id': None,
        'contact_number': None,
        'linkedin_url': None,
        'experience': None,
        'qualifications': [],
        'skillset': [],
        'work_experience_details': [],
        'certifications': [],
        'languages': []
    }

    # Extract contact info
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', extracted_text)
    if email_match:
        resume_data['email_id'] = email_match.group(0)

    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', extracted_text)
    if phone_match:
        resume_data['contact_number'] = phone_match.group(0)

    linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/\S+', extracted_text)
    if linkedin_match:
        resume_data['linkedin_url'] = linkedin_match.group(0)

    # Experience extraction
    experience_match = re.search(r'(\d+)\+?\s*(years?|yrs?)\b', extracted_text, re.IGNORECASE)
    if experience_match:
        resume_data['experience'] = f"{experience_match.group(1)} years"

    # Process sections
    lines = extracted_text.split('\n')
    current_section = None
    section_content = {key: [] for key in sections.keys()}

    for line in lines:
        line_lower = line.lower()
        for section, keywords in sections.items():
            if any(keyword in line_lower for keyword in keywords):
                current_section = section
                break
        if current_section:
            section_content[current_section].append(line)

    resume_data['qualifications'] = [' '.join(section_content['education'])] if section_content['education'] else []
    resume_data['skillset'] = [skill.strip() for skill in ', '.join(section_content['skills']).split(',') if skill]
    resume_data['work_experience_details'] = [' '.join(section_content['work_experience'])] if section_content['work_experience'] else []
    resume_data['certifications'] = section_content['certifications']
    resume_data['languages'] = [lang.strip() for lang in ', '.join(section_content['languages']).split(',') if lang]

    return resume_data

import pandas as pd
import os

def save_to_excel(resume_data, file_path="uploads/Parser to Data Entry test"):
    """Save extracted resume data to an Excel file and append new data."""
    
    # Convert JSON to DataFrame
    df_new = pd.DataFrame([resume_data])

    if os.path.exists(file_path):
        # Load existing data
        df_existing = pd.read_excel(file_path)
        
        # Append new data
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        # If file does not exist, create a new one
        df_final = df_new

    # Save to Excel
    df_final.to_excel(file_path, index=False)
    print("✅ Excel updated successfully!")


def send_data_to_appsheet(data):
    """Send extracted data to AppSheet API."""
    url = f"https://api.appsheet.com/api/v2/apps/{APPSHEET_APP_ID}/tables/{APPSHEET_TABLE_NAME}/Action"

    headers = {
        "ApplicationAccessKey": APPSHEET_ACCESS_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "Action": "Add",
        "Properties": {"Locale": "en-US", "Location": "Auto"},
        "Rows": [data],
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return {"success": True, "message": "Data sent to AppSheet successfully!"}
    else:
        return {"success": False, "message": response.text}


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def upload_resume_and_send(request):
    """Handle resume upload, process it, save to Excel, and send to AppSheet"""
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        fs = FileSystemStorage(location='uploads/')
        filename = fs.save(resume_file.name, resume_file)
        file_path = os.path.join('uploads', filename)

        extracted_text = extract_resume_text(file_path)
        if extracted_text:
            resume_data = process_resume_content(extracted_text)

            # Save data to Excel
            save_to_excel(resume_data, "uploads/Parser to Data Entry test.xlsx")  # Pass the second argument

            # Send data to AppSheet
            appsheet_response = send_data_to_appsheet(resume_data)

            return JsonResponse({
                'message': 'Resume processed successfully',
                'data': resume_data,
                'appsheet_response': appsheet_response
            })

        return JsonResponse({'error': 'Failed to process resume'}, status=400)

    return JsonResponse({'error': 'Invalid request. Use POST with a file.'}, status=400)