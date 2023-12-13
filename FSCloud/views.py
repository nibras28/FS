from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.units import inch
from rest_framework.decorators import api_view

from .forms import RegistrationForm, CustomAuthenticationForm


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
            return redirect('index')  # Redirect to the index page after registration
    else:
        form = RegistrationForm()
    return render(request, 'FSCloud/LR.html', {'form': form})


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

    return render(request, 'FSCloud/LR.html', {'form': form, 'error_message': error_message})


@login_required
def index_view(request):
    if request.user.is_authenticated:
        uploaded_data = None

        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                file_name = uploaded_file.name
                try:
                    # Configure AWS S3 client
                    s3 = boto3.client('s3', aws_access_key_id='AKIA4XKGL5GZY2YSA5ON',
                                      aws_secret_access_key='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')

                    s3.upload_fileobj(uploaded_file, 'fetherstillsample', file_name)
                    uploaded_data = f"File '{file_name}' uploaded successfully."
                except NoCredentialsError:
                    uploaded_data = "AWS credentials are not configured."

        return render(request, 'FSCloud/index.html', {'uploaded_data': uploaded_data})
    else:
        return redirect('login')


import csv


@login_required
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


@login_required
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


from django.http import JsonResponse


@api_view(['POST'])
@csrf_exempt
def api_upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            file_name = uploaded_file.name
            try:
                # Configure AWS S3 client
                s3 = boto3.client('s3', aws_access_key_id='AKIA4XKGL5GZY2YSA5ON',
                                  aws_secret_access_key='If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR')

                # Specify your AWS S3 bucket name
                bucket_name = 'fetherstillsample'

                # Upload the file to S3
                s3.upload_fileobj(uploaded_file, bucket_name, file_name)

                return JsonResponse({'status': 'success', 'message': f"File '{file_name}' uploaded successfully."})
            except NoCredentialsError:
                return JsonResponse({'status': 'error', 'message': "AWS credentials are not configured."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method or file not provided.'})


def download_csv(request, file_name):
    # Replace with your own AWS credentials
    aws_access_key_id = 'AKIA4XKGL5GZY2YSA5ON'
    aws_secret_access_key = 'If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR'
    bucket_name = 'fetherstillsample'

    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Retrieve the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)

        # Prepare the file for download
        content = response['Body'].read()
        response = HttpResponse(content, content_type='application/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'

        return response
    except NoCredentialsError:
        return HttpResponse("AWS credentials are not configured.")


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


# ... your other imports ...

def download_pdf(request, file_name):
    # Replace with your own AWS credentials
    aws_access_key_id = 'AKIA4XKGL5GZY2YSA5ON'
    aws_secret_access_key = 'If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR'
    bucket_name = 'fetherstillsample'

    try:
        # Initialize AWS S3 client
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Retrieve the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)

        # Load the CSV content
        content = response['Body'].read().decode('utf-8')

        # Split the content into lines
        lines = content.split('\n')

        # Create a PDF document
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.pdf'
        doc = SimpleDocTemplate(response, pagesize=letter)

        # Create a table to display the CSV data
        data = [line.split(',') for line in lines]
        table = Table(data, colWidths=[1.5 * inch for _ in range(len(data[0]))])

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Build the PDF document
        elements = []
        elements.append(table)
        doc.build(elements)

        return response
    except NoCredentialsError:
        return HttpResponse("AWS credentials are not configured.")


import boto3
from openpyxl import Workbook
from openpyxl.writer.excel import ExcelWriter


def download_excel(request, file_name):
    # Replace with your own AWS credentials
    aws_access_key_id = 'AKIA4XKGL5GZY2YSA5ON'
    aws_secret_access_key = 'If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR'
    bucket_name = 'fetherstillsample'

    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Retrieve the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)

        # Prepare the file for download
        content = response['Body'].read()

        # Create an in-memory Excel workbook
        workbook = Workbook()

        # You can populate the workbook with data here if needed

        # Create a response with the Excel workbook
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'

        # Save the workbook to the response
        ExcelWriter(workbook, response)

        return response
    except NoCredentialsError:
        return HttpResponse("AWS credentials are not configured.")


from docx import Document
from django.http import HttpResponse
from botocore.exceptions import NoCredentialsError


def download_word(request, file_name):
    # Replace with your own AWS credentials
    aws_access_key_id = 'AKIA4XKGL5GZY2YSA5ON'
    aws_secret_access_key = 'If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR'
    bucket_name = 'fetherstillsample'

    # Initialize AWS S3 client
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        # Retrieve the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)

        # Prepare the Word document for download
        content = response['Body'].read().decode('utf-8')
        docx_response = HttpResponse(content_type='application/msword')
        docx_response['Content-Disposition'] = f'attachment; filename="{file_name.replace(".csv", ".docx")}"'

        # Create a Word document
        doc = Document()
        doc.add_paragraph(content)

        doc.save(docx_response)

        return docx_response

    except NoCredentialsError:
        return HttpResponse("AWS credentials are not configured.")

# import boto3
# from botocore.exceptions import NoCredentialsError
# from django.http import HttpResponse
# from openpyxl import Workbook
# from openpyxl.writer.excel import save_virtual_workbook
#
#
# # ... your other views ...
#
# def download_excel2(request, file_name):
#     # Replace with your own AWS credentials
#     aws_access_key_id = 'AKIA4XKGL5GZY2YSA5ON'
#     aws_secret_access_key = 'If8eEm2Pgm+ir/YsFHwN7CpQ/VlKwuW2CQAUfIQR'
#     bucket_name = 'fetherstillsample'
#
#     # Initialize AWS S3 client
#     s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
#
#     try:
#         # Retrieve the file from S3
#         response = s3.get_object(Bucket=bucket_name, Key=file_name)
#
#         # Create an XLSX file from the retrieved content
#         content = response['Body'].read()
#         workbook = Workbook()
#         worksheet = workbook.active
#
#         # Write the content to the worksheet
#         for row in content.splitlines():
#             row_values = row.decode('utf-8').split(',')
#             worksheet.append(row_values)
#
#         # Prepare the XLSX file for download
#         xlsx_file = save_virtual_workbook(workbook)
#         response = HttpResponse(xlsx_file,
#                                 content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
#
#         return response
#     except NoCredentialsError:
#         return HttpResponse("AWS credentials are not configured.")
