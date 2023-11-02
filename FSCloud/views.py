import csv
import io

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm  # Remove this import
from .forms import RegistrationForm
from .forms import CustomAuthenticationForm
from django.contrib import messages
import boto3
from botocore.exceptions import NoCredentialsError
from django.shortcuts import render
from .forms import RegistrationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required


def home_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create a User instance but don't save it yet
            user = form.save(commit=False)
            # Set the user's password (you must set a password to create a user)
            user.set_password(form.cleaned_data['password'])
            # Now save the user instance
            user.save()
            # Log in the user
            login(request, user)
            return redirect('login')  # Redirect to the index page after registration
    else:
        form = RegistrationForm()
    return render(request, 'FSCloud/register.html', {'form': form})


def login_view(request):
    error_message = None

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)  # Use the custom form here
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                error_message = form.error_messages['invalid_login']
        else:
            error_message = "Incorrect Inputs."
            # You can add more specific error handling based on form errors here.
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = CustomAuthenticationForm()

    return render(request, 'FSCloud/login.html', {'form': form, 'error_message': error_message})


@login_required
def index_view(request):
    uploaded_data = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_name = uploaded_file.name
            try:
                # Configure AWS S3 client
                s3 = boto3.client('s3', aws_access_key_id='AKIA4XKGL5GZY2YSA5ON',
                                  aws_secret_access_key='If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR')

                # Upload the file to your AWS S3 bucket
                s3.upload_fileobj(uploaded_file, 'fetherstillsample', file_name)

                uploaded_data = f"File '{file_name}' uploaded successfully."
            except NoCredentialsError:
                uploaded_data = "AWS credentials are not configured."

    return render(request, 'FSCloud/index.html', {'uploaded_data': uploaded_data})


from datetime import datetime


from datetime import datetime
import csv
from django.http import HttpResponse
import tablib
import pandas as pd

def list_data(request):
    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id='AKIA4XKGL5GZY2YSA5ON',
                      aws_secret_access_key='If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR')

    # Specify your AWS S3 bucket name
    bucket_name = 'fetherstillsample'

    # Retrieve a list of objects (files) in the S3 bucket
    objects = s3.list_objects(Bucket=bucket_name)

    file_list = []

    for obj in objects.get('Contents', []):
        # Extract file details
        file_name = obj['Key']
        file_size = obj['Size']
        file_format = file_name.split('.')[-1]
        date_modified = obj['LastModified']

        formatted_date_modified = date_modified.strftime('%b. %d, %Y, %I:%M %p')

        file_list.append({
            'name': file_name,
            'size': file_size,
            'format': file_format,
            'date_modified': formatted_date_modified,
        })

    return render(request, 'FSCloud/list_data.html', {'file_list': file_list})



def view_csv(request, file_name):
    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id='AKIA4XKGL5GZY2YSA5ON',
                      aws_secret_access_key='If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR')

    # Specify your AWS S3 bucket name
    bucket_name = 'fetherstillsample'

    # Retrieve the CSV file content from S3
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    csv_content = response['Body'].read().decode('utf-8')

    # Parse the CSV content
    csv_data = []
    reader = csv.reader(csv_content.splitlines())
    for row in reader:
        csv_data.append(row)

    # Pass the CSV data to the template
    return render(request, 'FSCloud/view_csv.html', {'file_name': file_name, 'csv_data': csv_data})
