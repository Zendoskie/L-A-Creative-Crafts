# L&A Creative Crafts - AI Chatbot

A Django-based AI chatbot for L&A Creative Crafts, a business specializing in Handmade Crafts & Accessories. The chatbot uses OpenRouter API to access multiple AI models for intelligent customer service.

## Features

- 🤖 AI-powered chatbot using OpenRouter API (access to multiple AI models)
- 💬 Real-time chat interface with beautiful UI
- 🎨 Modern, responsive design
- 🏪 Customized for L&A Creative Crafts business

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Quick Start (Recommended)

Simply run the startup script:

```bash
cd "/home/paul/Downloads/L&A Creative Crafts"
./start.sh
```

This script will:
- ✅ Check for Python 3
- ✅ Create a virtual environment (if needed)
- ✅ Install all dependencies
- ✅ Run database migrations
- ✅ Start the Django development server

Then open your browser to `http://localhost:8000` and start chatting!

## Manual Installation

If you prefer to set up manually:

1. **Navigate to the project directory:**
   ```bash
   cd "/home/paul/Downloads/L&A Creative Crafts"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the Django development server:**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser and navigate to:**
   ```
   http://localhost:8000
   ```

## Project Structure

```
L&A Creative Crafts/
├── chatbot_project/          # Main Django project
│   ├── settings.py          # Project settings (includes Gemini API key)
│   ├── urls.py              # Main URL configuration
│   └── ...
├── chatbot_app/             # Chatbot Django app
│   ├── views.py             # Chat views and API endpoint
│   ├── urls.py              # App URL configuration
│   └── templates/           # HTML templates
│       └── chatbot_app/
│           └── chat.html    # Main chat interface
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── start.sh                 # Quick startup script
└── README.md               # This file
```

## API Configuration

The AI API key (OpenRouter) is configured in `chatbot_project/settings.py`:
```python
AI_API_KEY = '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'
AI_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
AI_MODEL = 'deepseek/deepseek-chat'  # You can change this to any model on OpenRouter
```

**Note:** OpenRouter provides access to multiple AI models. You can change `AI_MODEL` to use different models like:
- `deepseek/deepseek-chat` (default)
- `openai/gpt-3.5-turbo`
- `openai/gpt-4`
- `anthropic/claude-3-haiku`
- And many more available on [OpenRouter](https://openrouter.ai/models)

## Usage

- Type your message in the input field at the bottom
- Press Enter or click the "Send" button
- The AI will respond based on the context of L&A Creative Crafts business
- The chatbot is trained to answer questions about handmade crafts and accessories

## Troubleshooting

If you encounter any issues:

1. **Make sure all dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check that the Django server is running:**
   ```bash
   python manage.py runserver
   ```

3. **Verify the API key is correct in settings.py**

4. **Check browser console for any JavaScript errors**

## Notes

- The chatbot uses OpenRouter API to access AI models (default: DeepSeek Chat)
- All chat interactions are processed through OpenRouter
- You can easily switch between different AI models by changing the `AI_MODEL` setting
- The application runs on localhost:8000 by default
- For production use, update the SECRET_KEY and DEBUG settings

## License

This project is for L&A Creative Crafts business use.

