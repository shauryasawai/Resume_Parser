from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label="Upload Resume (PDF only)")
