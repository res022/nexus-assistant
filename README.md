# Nexus Assistant - Georgian Law Database with AI

🏛️ **Nexus Assistant** is a web application for browsing Georgian law documents with an AI-powered assistant that answers legal questions.

## Features

✅ **Browse 38 Georgian Laws** - View all laws with Georgian text and English summaries  
✅ **AI Chat Assistant** - Ask questions in Georgian, get answers with law citations  
✅ **Smart Search** - Find laws using English keywords or Georgian text  
✅ **Responsive Design** - Works on mobile, tablet, and desktop  
✅ **Two-Step AI Logic** - Efficient law selection before expensive AI calls

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key (free tier available)
3. Copy the key

### 3. Configure Environment

```bash
cp .env.template .env
```

Edit `.env` file and add your API key:
```
GEMINI_API_KEY=your_actual_api_key_here
SECRET_KEY=change_this_to_random_string
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and visit: **http://localhost:5000**

## Project Structure

```
nexus assistant/
├── laws/                  # 38 Georgian law files with metadata ✓
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── browse.html      # Law listing
│   ├── chat.html        # AI assistant
│   ├── law_detail.html  # Single law view
│   └── error.html       # Error page
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       ├── main.js      # Main JavaScript
│       └── chat.js      # Chat functionality
├── app.py              # Flask application
├── law_parser.py       # Law file parser
├── gemini_helper.py    # Gemini API integration
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.template)
└── README.md          # This file
```

## How It Works

### Two-Step AI Logic

**Step 1: Smart Law Selection**
1. User asks question in Georgian
2. System extracts keywords (Georgian → English mapping)
3. Searches law metadata using English keywords
4. Selects top 2-5 most relevant laws

**Step 2: AI Answer Generation**
1. Sends selected laws to Gemini API
2. Includes English summary + full Georgian text
3. Gemini answers in Georgian with law citations
4. Displays answer with sources used

### Law File Format

Each law file contains:
```
[Georgian Law Name - First Line]
[Full Georgian Law Text]

---METADATA---
SUMMARY_EN: English summary explaining the law
KEYWORDS_EN: keyword1, keyword2, keyword3...
```

## API Endpoints

- `GET /` - Home page
- `GET /browse` - Browse all laws
- `GET /browse?q=search` - Search laws
- `GET /law/<filename>` - View single law
- `GET /chat` - AI chat interface
- `POST /api/ask` - Ask AI a question
- `POST /api/clear-history` - Clear conversation history
- `GET /api/laws` - Get all laws (JSON)
- `GET /api/search?q=query` - Search laws (JSON)

## Configuration

Edit `config.py` to customize:

```python
LAWS_DIRECTORY = "laws"          # Law files directory
MAX_LAWS_FOR_AI = 5               # Max laws to send to AI
METADATA_SEPARATOR = "---METADATA---"
DEBUG = True                      # Flask debug mode
```

## Adding New Laws

1. Create a new `.txt` file in `laws/` folder
2. First line: Georgian law name
3. Add full Georgian text
4. Add metadata section:

```
---METADATA---
SUMMARY_EN: Your 3-4 sentence summary in English
KEYWORDS_EN: keyword1, keyword2, keyword3
```

5. Restart the application

## Troubleshooting

### "Gemini API არ არის კონფიგურირებული"

**Solution:** Add your Gemini API key to `.env` file

### Georgian text displays as "??????"

**Solution:** Ensure all files are UTF-8 encoded

### No laws appear in browse page

**Solution:** Check that `laws/` directory contains `.txt` files with metadata

### AI responds in English instead of Georgian

**Solution:** This is a Gemini model issue. The prompt explicitly requests Georgian, but results may vary.

## Technology Stack

- **Backend:** Python 3.8+, Flask
- **AI:** Google Gemini 1.5 Flash (free tier)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Fonts:** Noto Sans Georgian (Google Fonts)
- **Text Encoding:** UTF-8

## Free Tier Limits

**Gemini API (Free):**
- 15 requests per minute
- 1 million tokens per month
- 1,500 requests per day

The two-step approach ensures efficient API usage by only sending 2-5 relevant laws per question.

## License

This project is for educational and roleplay server purposes.

## Support

For issues, check:
1. `.env` file configuration
2. Python dependencies installed
3. Georgian text encoding (UTF-8)
4. Gemini API key validity

## Future Enhancements

- [ ] User authentication
- [ ] Bookmark favorite laws
- [ ] Export chat history
- [ ] Multi-language support
- [ ] Advanced search filters
- [ ] Law comparison tool
- [ ] Mobile app version

---

**Made with ❤️ for San Andreas Roleplay Server**
