# 🛩 Airline Call Center Optimization System

## 📋 Overview
A single-file Streamlit application designed to optimize airline call center operations. This system processes flight queries, categorizes customer calls, and generates performance metrics—all with standardized JSON outputs.

## 🛠 Components
- Flight Information Retrieval
- Natural Language Query Processing
- Call Transcript Analysis
- Performance Metrics Computation

## 🧰 Technology Stack
- *Streamlit*: User interface framework
- *Together AI* (optional): Enhanced language processing
- *JSON*: Standardized output format
- *Regular Expressions*: Pattern matching for data extraction

## 💻 Quick Start Guide
## 📥 Installation

### Prerequisites

- Python 3.8 or higher
-  pip package manager

### Setup

1. Clone this repository:
   
   git clone https://github.com/Rahul21082004/Airline-Agent.git
   cd Airline-Agent
   

2. Create a virtual environment (recommended):
   
   python -m venv venv
   

3. Activate the virtual environment:
   - On Windows:
     
     venv\Scripts\activate
     
   - On macOS/Linux:
     
     source venv/bin/activate
     

4. Install the required dependencies:
   
   pip install -r requirements.txt
   

5. Create a .env file in the project root and add your Together AI API key (optional):
   
   TOGETHER_API_KEY=your_api_key_here
   

## 🚀 Running the Code

1. Run the application:

  streamlit run main.py


## 📊 Available Services

### 🔎 Flight Lookup
Enter any flight number to retrieve comprehensive details:
- Departure/arrival times
- Terminal and gate information
- Current flight status

### 🗣 Query Assistant
Ask questions in natural language:

What time does flight AI123 depart?
Is flight AI456 on time?
From which terminal does flight AI789 leave?


### 📝 Call Analyzer
Submit call transcripts to automatically:
- Identify call purpose
- Extract mentioned flight numbers
- Determine resolution status
- Generate structured summary

### 📈 KPI Dashboard
Analyze multiple call transcripts to produce:
- Resolution rates
- Common inquiry types
- Sentiment metrics
- Performance indicators

## 🔄 Processing Pipeline

1. *Input Reception*: User provides data through Streamlit interface
2. *Agent Processing*: Specialized function handles the specific request type
3. *Data Extraction*: System extracts relevant information using patterns or AI
4. *Response Generation*: Structured JSON response is created
5. *Visualization*: Results are displayed in the Streamlit interface

## 🌟 Feature Highlights

- *Pattern Fallback*: System works even without AI integration
- *Strict JSON Format*: All outputs follow consistent structure
- *Interactive UI*: User-friendly Streamlit interface
- *Single-File Design*: Easy deployment with minimal setup

## 📝 Input Examples

### Flight Query:

What is the status of flight AI123?


### Sample Call Transcript:

Agent: Hello, thank you for calling Air Express. How may I assist you today?
Customer: Hi, I need to check the status of my flight AI123 to Delhi.
Agent: I'd be happy to help you with that. May I have your booking reference?
Customer: It's ABC123.
...


## 🏁 Getting Started

1. Launch the application with streamlit run main.py
2. Select a service from the sidebar
3. Enter the required information
4. View the JSON response

## 🔗 Dependencies
- streamlit
- together
- python-dotenv
- json
- re

---

Created for optimizing airline call center operations with AI assistance
