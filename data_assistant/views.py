from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import CSVFileSerializer
from .models import CSVFile
from rest_framework import generics
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseNotAllowed
from django.core.files.storage import default_storage
from django.views.decorators.http import require_POST

# class CSVUploadView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request, *args, **kwargs):
#         serializer = CSVFileSerializer(data=request.data)
#         if serializer.is_valid():
#             # you can add more processing here
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class CSVUploadView(generics.CreateAPIView):
    def post(self, request):
        queryset = CSVFile.objects.all()
        serializer_class = CSVFileSerializer

from django.http import JsonResponse
import pandas as pd
from django.conf import settings
import requests
import hashlib
import os


@csrf_exempt
def upload_view(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')  # get list of uploaded files

        if not uploaded_files:
            return JsonResponse({"error": "No files uploaded"}, status=400)

        for uploaded_file in uploaded_files:
            if not uploaded_file.name.endswith('.csv'):
                continue  # skip non-csv files

            save_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

            # Optional: overwrite existing file to avoid duplicates
            if default_storage.exists(uploaded_file.name):
                default_storage.delete(uploaded_file.name)

            with default_storage.open(uploaded_file.name, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

        request.session['uploaded_df'] = True

        uploaded_names = [f.name for f in uploaded_files]
        return render(request, 'upload_success.html', {'files': uploaded_names})


    elif request.method == 'GET':
        return render(request, 'upload.html')

    return HttpResponseNotAllowed(['GET', 'POST'])

def get_all_csv_data():
    media_path = settings.MEDIA_ROOT
    all_dataframes = []

    for filename in os.listdir(media_path):
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(os.path.join(media_path, filename))
                df['__source_file__'] = filename  # Optional: add source info
                all_dataframes.append(df)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if all_dataframes:
        return pd.concat(all_dataframes, ignore_index=True)
    else:
        return None

# @csrf_exempt
# def ask_question_view(request):
#     if request.method == 'GET':
#         # Check for session data
#         if 'uploaded_df' not in request.session:
#             return render(request, 'no_data.html')
#         return render(request, 'ask.html')

#     elif request.method == 'POST':
#         # Check for CSV session data
#         if 'uploaded_df' not in request.session:
#             return render(request, 'no_data.html')

#         question = request.POST.get("question")
#         if not question:
#             return render(request, 'ask.html', {'error': "Please enter a question."})

#         # # Restore the DataFrame from session
#         # df_json = request.session['uploaded_df']
#         # df = pd.read_json(df_json, orient='split')

#         # # Prepare prompt
#         # df_str = df.to_csv(index=False)
#         # prompt = f"""You are a data analyst. Given the following CSV data:\n\n{df_str}\n\nAnswer this question:\n{question}"""

#         df = get_all_csv_data()
#         if df is None:
#             return render(request, 'no_data.html')

#         df_str = df.head(100).to_csv(index=False)

#         prompt = f"""You are a data analyst. Below is a combination of multiple CSV files:\n\n{df_str}\n\nAnswer this question:\n{question}"""


#         # API Request
#         headers = {
#             "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
#             "HTTP-Referer": "http://localhost:8000",
#             "X-Title": "Smart LLM Data Assistant",
#             "Content-Type": "application/json",
#         }
#         payload = {
#             "model":"deepseek/deepseek-r1-0528:free",
#             "messages": [{"role": "user", "content": prompt}],
#         }

#         response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

#         if response.status_code != 200:
#             return render(request, 'ask.html', {'error': "LLM request failed.", "details": response.text})

#         result = response.json()
#         reply = result['choices'][0]['message']['content']

#         return render(request, 'ask.html', {'question': question, 'response': reply})

#     return JsonResponse({"error": "Only GET or POST allowed"}, status=405)

@csrf_exempt
def ask_question_view(request):

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == 'GET':
        if 'uploaded_df' not in request.session:
            return render(request, 'no_data.html')
        return render(request, 'ask.html', {
            'chat_history': request.session['chat_history']
        })

    elif request.method == 'POST':
        if 'uploaded_df' not in request.session:
            return render(request, 'no_data.html')

        question = request.POST.get("question")
        if not question:
            return render(request, 'ask.html', {
                'error': "Please enter a question.",
                'chat_history': request.session.get('chat_history', [])
            })

        df = get_all_csv_data()
        if df is None:
            return render(request, 'no_data.html')

        df_str = df.head(200).to_csv(index=False)
        prompt = f"""You are a data analyst. Below is a combination of multiple CSV files:\n\n{df_str}\n\nAnswer this question:\n{question}"""

        # API call
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Smart LLM Data Assistant",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek/deepseek-r1-0528:free",
            "messages": [{"role": "user", "content": prompt}],
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            return render(request, 'ask.html', {
                'error': "LLM request failed.",
                'chat_history': request.session.get('chat_history', [])
            })

        reply = response.json()['choices'][0]['message']['content']

        # Append to chat history
        chat_history = request.session['chat_history']
        # chat_history.append({"question": question, "response": reply})
        chat_history.append({
            'question': question,
            'response': render_markdown_to_html(reply),
        })

        request.session['chat_history'] = chat_history

        return render(request, 'ask.html', {
            'chat_history': chat_history
        })

    return JsonResponse({"error": "Only GET or POST allowed"}, status=405)

def clear_chat(request):
    request.session['chat_history'] = []
    return redirect('/api/ask/')


import markdown
from django.utils.safestring import mark_safe

def render_markdown_to_html(md_text):
    html = markdown.markdown(md_text, extensions=['extra', 'tables'])
    return mark_safe(html)