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
EXCEL_FILE_PATH = "uploads/Parser to Data Entry test.xlsx"

def extract_resume_text(pdf_path):
    """Extract text from a PDF resume."""
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

import re

def process_resume_content(extracted_text):
    """Process extracted text into structured data."""
    sections = {
        'education': ['education', 'academic background', 'qualifications', 'degree'],
        'work_experience': ['work experience', 'professional experience', 'employment history'],
        'skills': ['skills', 'technical skills', 'skill set'],
        'certifications': ['certifications', 'certificates'],
        'languages': ['languages'],
        'designation': ['designation', 'role', 'position', 'title', 'current role']
    }

    resume_data = {
        'candidate_name': None,
        'contact_number': None,
        'candidate_location': None,
        'current_designation': None,
        'experience': None,
        'linkedin_url': None,
        'qualifications': []
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

    # Extract candidate location
    location_match = re.search(r'(current location|located at|based in|resides in|Contact)[:\s]*([\w\s,]+)', extracted_text, re.IGNORECASE)
    if location_match:
        resume_data['candidate_location'] = location_match.group(2).strip()

    # Extract experience
    experience_match = re.search(r'(\d+)\+?\s*(years?|yrs?)\b', extracted_text, re.IGNORECASE)
    if experience_match:
        resume_data['experience'] = f"{experience_match.group(1)} years"

    # Extract current designation
    designation_match = re.search(r'(designation|role|position|title|current role)[:\s]*([\w\s]+)', extracted_text, re.IGNORECASE)
    if designation_match:
        resume_data['current_designation'] = designation_match.group(2).strip()

    # Extract candidate name (first capitalized words at the start of the resume)
    def extract_name(text):
        """Extracts candidate name from the top of the resume (first 5 lines)."""
        lines = text.split("\n")[:5]  # Consider only first 5 lines
        for line in lines:
            line = line.strip()
            if len(line.split()) in [2, 3]:  # Candidate name usually has 2-3 words
                if re.match(r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,2}$', line):  # Name pattern
                    return line
        return None

    resume_data['candidate_name'] = extract_name(extracted_text)

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
            section_content[current_section].append(line.strip())

    # Extract qualifications (degree names like B.Tech, MBA, M.Sc, etc.)
    degree_patterns = r'(B\.?Tech|Bachelors?|M\.?Tech|Masters?|M\.?Sc|B\.?Sc|MBA|Ph\.?D|Doctorate|Diploma|Engineering|Computer Science|Management)'
    qualifications = re.findall(degree_patterns, extracted_text, re.IGNORECASE)
    resume_data['qualifications'] = list(set(qualifications))  # Remove duplicates

    return resume_data



import pandas as pd
import os

import pandas as pd
import os

def save_to_excel(resume_data, file_path="uploads/Parser to Data Entry test.xlsx"):
    """Save extracted resume data to an Excel file and append new data under the correct columns."""
    
    # Define the expected column names
    expected_columns = [
        "Candidate Name", "Contact Number", "Email of Candidate", "Candidate Location", "Current Designation", 
        "Experience", "LinkedIn URL", "Qualifications"
    ]
    
    # Convert JSON to DataFrame with correct column names
    df_new = pd.DataFrame([resume_data])
    df_new.rename(columns={
        "candidate_name": "Candidate Name",
        "contact_number": "Contact Number",
        "contact_email": "Email of Candidate",
        "candidate_location": "Candidate Location",
        "current_designation": "Current Designation",
        "experience": "Experience",
        "linkedin_url": "LinkedIn URL",
        "qualifications": "Qualifications"
    }, inplace=True)
    
    # Ensure qualifications are stored as a string if it's a list
    if "Qualifications" in df_new.columns:
        df_new["Qualifications"] = df_new["Qualifications"].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    
    if os.path.exists(file_path):
        # Load existing data
        df_existing = pd.read_excel(file_path)
        
        # Ensure all expected columns exist
        for col in expected_columns:
            if col not in df_existing.columns:
                df_existing[col] = None  # Add missing columns with None values
        
        # Append new data
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        # If file does not exist, create a new one with the correct column order
        df_final = df_new.reindex(columns=expected_columns)
    
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
def upload_resume_and_review(request):
    """Upload resume, extract data, and show for review before saving."""
    if request.method == "POST" and request.FILES.get("resume"):
        uploaded_file = request.FILES["resume"]
        file_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)

        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        extracted_text = extract_resume_text(file_path)
        resume_data = process_resume_content(extracted_text)
        
        return render(request, 'base/review_data.html', {"resume_data": resume_data})

    return render(request, 'base/upload.html')

@csrf_exempt
def save_edited_resume(request):
    """Save edited data to Excel and AppSheet after user review."""
    if request.method == "POST":
        edited_data = request.POST
        resume_data = {
            "candidate_name": edited_data.get("candidate_name"),
            "contact_number": edited_data.get("contact_number"),
            "email_id": edited_data.get("email_id"),
            "candidate_location": edited_data.get("candidate_location"),
            "current_designation": edited_data.get("current_designation"),
            "experience": edited_data.get("experience"),
            "linkedin_url": edited_data.get("linkedin_url"),
            "qualifications": edited_data.get("qualifications")
        }

        # Save to Excel
        df = pd.DataFrame([resume_data])

        if os.path.exists(EXCEL_FILE_PATH):
            existing_df = pd.read_excel(EXCEL_FILE_PATH)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_excel(EXCEL_FILE_PATH, index=False)

        # Send to AppSheet
        api_response = send_data_to_appsheet(resume_data)

        return JsonResponse({
            "message": "Data updated and saved successfully!",
            "appsheet_response": api_response
        })

    return JsonResponse({"error": "Invalid request method"}, status=400)
