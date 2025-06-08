# 🧠 SmartLLM – AI-Powered CSV Data Assistant

SmartLLM is a Django-based web application that enables users to upload CSV files and ask natural language questions about their data. It uses OpenRouter + DeepSeek LLMs to provide intelligent, contextual answers by applying Retrieval-Augmented Generation (RAG) techniques.

---

## 🚀 Features

- 📁 **CSV Upload & Session Handling** – Upload and process CSV files in the browser with session-based storage.
- 🧠 **LLM-Powered Question Answering** – Query the uploaded data in plain English using OpenRouter + DeepSeek LLMs.
- 🎯 **RAG-Style Retrieval** – Automatically parses and indexes CSV content to provide relevant, accurate answers.
- ⚙️ **Django REST Framework** – Clean and scalable API structure.
- 🎨 **Tailwind CSS UI** – Responsive and minimal UI for easy interaction.

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework
- **LLM Integration:** OpenRouter + DeepSeek
- **Frontend:** Tailwind CSS, HTMX (if used)
- **Storage:** Django Sessions (currently), PostgreSQL (planned)
- **Async (Planned):** Celery + Redis
- **Deployment (Planned):** Docker + Render/AWS
