# 🚀 Hirehead.ai – AI Recruitment Assistant

Hirehead.ai is an **AI-powered recruitment assistant** designed to simplify the job application and hiring process.  
The platform analyzes job descriptions, evaluates resume compatibility, and automatically generates professional job application emails.

This project demonstrates the use of **Artificial Intelligence, web scraping, and data visualization** to help job seekers and recruiters streamline the hiring workflow.

---

## ✨ Features

- 🔎 **Job Description Scraping**
  - Extracts job details directly from job posting URLs.

- 📄 **Resume Analysis**
  - Compares resumes with job descriptions using AI-based matching.

- 📊 **Match Score Visualization**
  - Provides graphical insights on resume-job compatibility.

- ✉️ **Automated Email Generation**
  - Generates personalized job application emails automatically.

- 🤖 **AI Integration**
  - Uses AI APIs to generate smart and context-aware responses.

- 🎨 **Interactive Web Interface**
  - Built with Streamlit for a simple and clean UI.

---

## 🏗️ System Architecture

```
                USER INPUT
      Job URL + Resume Upload
                │
                ▼
         DATA EXTRACTION
      Job Scraper (BeautifulSoup)
                │
                ▼
          PROCESSING LAYER
    Resume Analysis + Keyword Matching
                │
                ▼
         AI GENERATION ENGINE
     Professional Email Generation
                │
                ▼
          VISUALIZATION
     Match Score + Data Insights
```

---

## 🛠️ Tech Stack

- Python
- Streamlit
- BeautifulSoup
- Matplotlib
- Regex
- AI API Integration

---

## 📂 Project Structure

```
Hirehead.ai/
│
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── .github/              # GitHub configuration
├── .devcontainer/        # Development environment setup
└── README.md             # Project documentation
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Ananya-Baghel/Hirehead.ai.git
cd Hirehead.ai
```

### 2️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the environment

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Configuration

This project uses an **AI API for generating application emails**.

Add your API key inside the application file:

```python
API_KEY = "your_api_key_here"
```

---

## ▶️ Running the Application

Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Then open the link shown in the terminal:

```
http://localhost:8501
```

---

## 💡 How It Works

1. User enters a **job posting URL**
2. The application **scrapes the job description**
3. User uploads their **resume**
4. The system **analyzes and calculates a match score**
5. AI **generates a professional application email**
6. Results are **visualized with charts and insights**

---

## 📊 Example Workflow

1️⃣ Paste job posting URL  
2️⃣ Upload your resume  
3️⃣ View resume-job match percentage  
4️⃣ Generate AI-written application email  
5️⃣ Copy or download the generated email

---

## 🚀 Future Improvements

- Support for **multiple job portals**
- Resume parsing with **advanced NLP**
- Integration with **LinkedIn APIs**
- Multi-resume comparison
- Improved **AI-powered recommendations**

---

## 🤝 Contributing

Contributions are welcome!

Steps to contribute:

1. Fork the repository  
2. Create a new branch  
3. Commit your changes  
4. Submit a pull request  

---

## 📄 License

This project is released under the **MIT License**.
