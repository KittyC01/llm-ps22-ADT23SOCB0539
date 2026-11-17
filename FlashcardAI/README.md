
# 📚 FlashcardAI – Smart Study Flashcards

An AI-powered application that transforms study notes into interactive flashcards using Generative AI.

## 🎯 Project Overview

FlashcardAI helps students prepare for examinations by converting their study material into useful revision flashcards using Generative AI.
Users can select their preferred difficulty level, study generated flashcards, edit questions and answers, and export them as CSV files.

## ✨ Features

- Generate flashcards directly from study notes.
- Three difficulty levels: Easy, Medium and Hard.
- AI-powered question and answer generation.
- Show/hide answers.
- Previous and Next navigation.
- Shuffle and edit flashcards.
- Export flashcards as CSV.
- Interactive Streamlit interface.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Groq API | AI integration |
| OpenAI GPT-OSS 20B | Language model |
| Streamlit | User interface |
| Pandas | Data management |
| JSON / CSV | Data formatting and export |

## 📂 Project Structure

```text
FlashcardAI/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/KittyC01/llm-ps22-ADT23SOCB0539.git
cd FlashcardAI
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure your Groq API key**
Create a folder named .streamlit and create a file named secrets.toml inside it -
Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_api_key"
```

**4. Run the application**

```bash
streamlit run app.py
```

---

*FlashcardAI – Making learning smarter, one flashcard at a time.*
