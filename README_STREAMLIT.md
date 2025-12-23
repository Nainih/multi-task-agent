# Streamlit AI Assistant App

A user-friendly web interface for the AI Assistant that handles Math, Knowledge queries, and Ground Booking with human-in-the-loop interactions.

## Features

- 🤖 **AI Assistant** - Routes queries to appropriate agents (Math, Knowledge, Ground Booking)
- 💬 **Conversation History** - See all your interactions
- 🖥️ **Machine Resources** - Real-time monitoring of CPU, Memory, and Disk usage
- 🔄 **Human-in-the-Loop** - Handles interrupts when the bot needs more information
- 📱 **Modern UI** - Clean and intuitive Streamlit interface

## Installation

1. Make sure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

2. Ensure you have the required environment variables set (OPENAI_API_KEY, etc.)

## Running the App

Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter your query** in the text input field
2. **Examples:**
   - Math: "What is 15 + 27?"
   - Knowledge: "Tell me about MacBook Air"
   - Booking: "Book a ground for tomorrow at 2pm"

3. If the bot needs more information (for bookings), it will ask you questions
4. **Respond** to the questions when prompted
5. View **machine resources** in the sidebar
6. **Clear history** anytime using the sidebar button

## How It Works

- The app integrates with `graph.py` which routes queries to different agents
- For ground bookings, the system uses LangGraph interrupts to ask for missing information
- Machine resources are monitored using `psutil` and updated in real-time
- Session state manages conversation history and interrupt handling

## Notes

- Each session has a unique thread_id for conversation continuity
- The booking state persists across questions in the same session
- Resources are refreshed on each page reload or when you click "Refresh Resources"

