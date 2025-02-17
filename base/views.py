from django.shortcuts import render
import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from .forms import ResumeUploadForm
from .models import UploadedResume
from pdfminer.high_level import extract_text
import re
from django.core.files.storage import FileSystemStorage

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

    resume_data['qualifications'] = [' '.join(section_content['education'])]
    resume_data['skillset'] = [skill.strip() for skill in ', '.join(section_content['skills']).split(',') if skill]
    resume_data['work_experience_details'] = [' '.join(section_content['work_experience'])]
    resume_data['certifications'] = section_content['certifications']
    resume_data['languages'] = [lang.strip() for lang in ', '.join(section_content['languages']).split(',') if lang]

    return resume_data



def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        fs = FileSystemStorage(location='uploads/')  
        filename = fs.save(resume_file.name, resume_file)
        file_path = os.path.join('uploads', filename)
        
        extracted_text = extract_resume_text(file_path)
        if extracted_text:
            resume_data = process_resume_content(extracted_text)
            return JsonResponse(resume_data)  # Return JSON output
        
        return JsonResponse({'error': 'Failed to process resume'}, status=400)

    return render(request, 'base/index.html')