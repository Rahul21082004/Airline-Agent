import streamlit as st
import json
import re
import os
from typing import Dict, Any, List, Union
from dotenv import load_dotenv
import together

load_dotenv('api_keys.env')

together_api_key = os.getenv('TOGETHER_API_KEY')
if together_api_key:
    together.api_key = together_api_key


# Flight database
FLIGHT_DATABASE = {
    "AI123": {
        "flight_number": "AI123",
        "departure_time": "08:00 AM",
        "destination": "Delhi",
        "status": "Delayed",
        "terminal": "T2",
        "gate": "G14",
        "arrival_time": "10:30 AM"
    },
    "AI456": {
        "flight_number": "AI456",
        "departure_time": "10:30 AM",
        "destination": "Mumbai",
        "status": "On Time",
        "terminal": "T1",
        "gate": "G22",
        "arrival_time": "12:15 PM"
    },
    "AI789": {
        "flight_number": "AI789",
        "departure_time": "02:15 PM",
        "destination": "Bangalore",
        "status": "Boarding",
        "terminal": "T3",
        "gate": "G5",
        "arrival_time": "04:00 PM"
    },
    "AI234": {
        "flight_number": "AI234",
        "departure_time": "06:45 PM",
        "destination": "Chennai",
        "status": "Cancelled",
        "terminal": "T2",
        "gate": "G19",
        "arrival_time": "08:30 PM"
    },
    "AI567": {
        "flight_number": "AI567",
        "departure_time": "11:15 AM",
        "destination": "Kolkata",
        "status": "On Time",
        "terminal": "T1",
        "gate": "G7",
        "arrival_time": "01:30 PM"
    },
    "AI890": {
        "flight_number": "AI890",
        "departure_time": "04:30 PM",
        "destination": "Hyderabad",
        "status": "Scheduled",
        "terminal": "T3",
        "gate": "G12",
        "arrival_time": "06:15 PM"
    }
}

# Sample transcripts
SAMPLE_TRANSCRIPTS = [
    """
    Agent: Air Express customer service, how may I help you?
    Customer: Hello, I'm having an issue with my baggage. I arrived on flight AI567 this morning, but one of my bags didn't make it.
    Agent: I'm sorry to hear about your missing baggage. Let me help you file a report. Can I have your name and booking reference, please?
    Customer: My name is John Smith, and my booking reference is DEF456.
    Agent: Thank you, Mr. Smith. I'll need some details about your missing bag. Can you describe it for me?
    Customer: It's a large black suitcase with a red tag. It has my contact information on it.
    Agent: Got it. I've filed a report for your missing baggage. Your reference number is BG98765. We'll contact you as soon as we locate your bag.
    Customer: How long does it usually take?
    Agent: Most bags are located within 24-48 hours. We'll send you updates via text message.
    Customer: Okay, thank you for your help.
    Agent: You're welcome. Is there anything else I can assist you with today?
    Customer: No, that's all.
    Agent: Thank you for calling Air Express. We apologize for the inconvenience.
    """,
    
    """
    Agent: Air Express reservations, how may I assist you?
    Customer: Hi, I'd like to change my seat assignment on flight AI890 tomorrow.
    Agent: I'd be happy to help you with that. May I have your name and booking reference?
    Customer: Sarah Johnson, booking reference GHI789.
    Agent: Thank you, Ms. Johnson. I can see you're currently assigned to seat 14C, which is an aisle seat. What type of seat would you prefer?
    Customer: I'd prefer a window seat, if possible.
    Agent: Let me check what's available... I can offer you 12A or 23F, both are window seats.
    Customer: I'll take 12A, please.
    Agent: Perfect. I've updated your seat assignment to 12A. Your boarding pass has been updated and sent to your email.
    Customer: Great, thank you so much!
    Agent: You're welcome. Have a pleasant flight tomorrow. Is there anything else I can help you with?
    Customer: No, that's all for today.
    Agent: Thank you for calling Air Express. Have a wonderful day!
    """
]

# Together AI functions
def is_together_available():
    
    return bool(together_api_key)

def invoke_together_model(prompt: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1") :
    if not together_api_key:
        raise EnvironmentError("Together AI API key not configured")
    
    response = together.Complete.create(
        prompt=prompt,
        model=model,
        max_tokens=500,
        temperature=0.1, 
        top_p=0.9
    )
    
    return response

# Info Agent 
def get_flight_info(flight_number: str):
    flight_number = flight_number.upper()
    
    if flight_number in FLIGHT_DATABASE:
        return FLIGHT_DATABASE[flight_number]
    return {}

def info_agent_request(flight_number: str)  :
    try:
        result = get_flight_info(flight_number)
        
        if not result:
            return json.dumps({"error": f"Flight {flight_number} not found in database."})
        
        return json.dumps(result)
            
    except Exception as e:
        return json.dumps({"error": f"Error processing request: {str(e)}"})

# QA Agent 
def extract_flight_number(query: str)  :
    patterns = [
        r'flight\s+([A-Za-z]{1,3}\d{1,4})', 
        r'([A-Za-z]{1,3}\d{1,4})\s+flight',  
        r'flight\s+number\s+([A-Za-z]{1,3}\d{1,4})',
        r'([A-Za-z]{1,3}\d{1,4})'  
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, query, re.IGNORECASE)
        if matches:
            return matches.group(1)
    
    if is_together_available():
        try:
            prompt = f"""
            Extract the flight number from the following user query. 
            Respond with ONLY the flight number, or 'NONE' if no flight number is found.
            
            User query: {query}
            
            Flight number:
            """
            
            response = invoke_together_model(prompt)
            extracted = response['output']['choices'][0]['text'].strip()
            
            if re.match(r'^[A-Za-z]{1,3}\d{1,4}$', extracted):
                return extracted
            elif extracted != "NONE":
                for pattern in patterns:
                    matches = re.search(pattern, extracted, re.IGNORECASE)
                    if matches:
                        return matches.group(1)
        except Exception as e:
            print(f"Error using Together AI for extraction: {str(e)}")
            pass  
    
    return ""

def qa_agent_respond(user_query: str)  :
    try:
        flight_number = extract_flight_number(user_query)
        
        if not flight_number:
            return json.dumps({
                "answer": "I couldn't identify a flight number in your query. Please specify a flight number like 'AI123'."
            })
        
        info_response = info_agent_request(flight_number)
        flight_data = json.loads(info_response)
        
        if "error" in flight_data:
            return json.dumps({
                "answer": f"Flight {flight_number} not found in database."
            })
        
        if is_together_available():
            try:
                prompt = f"""
                Generate a concise answer to the user's query about a flight based on the flight data provided.
                The response should be factual and address the specific question asked.
                
                User query: {user_query}
                
                Flight data: {json.dumps(flight_data)}
                
                Answer:
                """
                
                response = invoke_together_model(prompt)
                answer = response['output']['choices'][0]['text'].strip()
                
                if answer and len(answer) <= 200:
                    return json.dumps({
                        "answer": answer
                    })
            except Exception as e:
                print(f"Error using Together AI for response generation: {str(e)}")
        
        if re.search(r'depart|departure|leave|time', user_query, re.IGNORECASE):
            answer = f"Flight {flight_data['flight_number']} departs at {flight_data['departure_time']} to {flight_data['destination']}. Current status: {flight_data['status']}."
        elif re.search(r'destination|arrive|goes to|going to', user_query, re.IGNORECASE):
            answer = f"Flight {flight_data['flight_number']} is headed to {flight_data['destination']}. It departs at {flight_data['departure_time']}. Current status: {flight_data['status']}."
        elif re.search(r'status|delayed|on time|cancelled', user_query, re.IGNORECASE):
            answer = f"Flight {flight_data['flight_number']} status: {flight_data['status']}. It's scheduled to depart at {flight_data['departure_time']} to {flight_data['destination']}."
        elif re.search(r'terminal|gate', user_query, re.IGNORECASE):
            answer = f"Flight {flight_data['flight_number']} departs from Terminal {flight_data['terminal']}, Gate {flight_data['gate']}. Current status: {flight_data['status']}."
        else:
            answer = f"Flight {flight_data['flight_number']} to {flight_data['destination']} departs at {flight_data['departure_time']} from Terminal {flight_data['terminal']}, Gate {flight_data['gate']}. Current status: {flight_data['status']}."
        
        return json.dumps({
            "answer": answer
        })
            
    except Exception as e:
        return json.dumps({"answer": f"Error processing request: {str(e)}"})

# Call categorization 
def categorize_call(transcript: str)  :
    try:
        categories = {
            "Flight Booking": ["book", "reserve", "purchase", "buy", "schedule"],
            "Flight Cancellation": ["cancel", "refund", "money back"],
            "Flight Rescheduling": ["reschedule", "change", "move", "different date"],
            "Baggage Issue": ["baggage", "luggage", "bag", "suitcase", "missing", "lost"],
            "Complaint": ["complaint", "unhappy", "disappointed", "poor", "terrible", "bad experience"],
            "Seat Change": ["seat", "change seat", "different seat", "window", "aisle"],
            "General Inquiry": ["status", "check", "information", "time", "when"]
        }
        
        if is_together_available():
            try:
                prompt = f"""
                You are an AI assistant that categorizes airline call center conversations. 
                Categories include: Flight Booking, Flight Cancellation, Flight Rescheduling, 
                Refund Request, Baggage Issue, Complaint, and General Inquiry.
                
                Please categorize the following call transcript and extract key information 
                like flight numbers, dates, and specific issues. Provide the output in JSON 
                format with 'category' and 'details' fields.
                
                Transcript: {transcript}
                
                Output:
                """
                
                response = invoke_together_model(prompt)
                categorization = response['output']['choices'][0]['text'].strip()
                
                try:
                    return categorization
                except json.JSONDecodeError:
                    pass
            except Exception as e:
                print(f"Error using Together AI for categorization: {str(e)}")
        
        transcript_lower = transcript.lower()
        determined_category = "General Inquiry"  
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in transcript_lower:
                    determined_category = category
                    break
        
        flight_numbers = []
        pattern = r'([A-Za-z]{1,3}\d{1,4})'
        matches = re.findall(pattern, transcript)
        if matches:
            flight_numbers = [match for match in matches if match.upper().startswith('AI')]
        
        resolved = "thank you" in transcript_lower and "have a" in transcript_lower
        resolution_status = "Resolved" if resolved else "Pending"
        
        customer_name = "Unknown"
        name_patterns = [
            r'name is ([A-Za-z\s]+),',
            r'name is ([A-Za-z\s]+)\.', 
            r'I\'m ([A-Za-z\s]+),',
            r'this is ([A-Za-z\s]+),'
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, transcript)
            if name_match:
                customer_name = name_match.group(1).strip()
                break
        
        details = {
            "flight_numbers": flight_numbers,
            "customer_name": customer_name,
            "resolution_status": resolution_status,
            "call_summary": f"{determined_category} related to flight(s): {', '.join(flight_numbers) if flight_numbers else 'None specified'}"
        }
        
        return json.dumps({
            "category": determined_category,
            "details": details
        })
    
    except Exception as e:
        return json.dumps({"error": f"Error categorizing call: {str(e)}"})

# KPI
def compute_call_center_kpis(transcripts: List[str])  :
    if not transcripts:
        return json.dumps({"error": "No transcripts provided"})
    
    try:
        categories = {}
        resolution_count = 0
        flight_mentions = {}
        customer_sentiments = []
        
        for transcript in transcripts:
            categorization = json.loads(categorize_call(transcript))
            category = categorization.get("category", "Unknown")
            details = categorization.get("details", {})
            

            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
            
            if details.get("resolution_status") == "Resolved":
                resolution_count += 1
            
            for flight in details.get("flight_numbers", []):
                if flight in flight_mentions:
                    flight_mentions[flight] += 1
                else:
                    flight_mentions[flight] = 1
            
            sentiment_score = 0
            positive_words = ["thank", "good", "great", "excellent", "helpful", "appreciate", "happy", "satisfied"]
            negative_words = ["unhappy", "disappointed", "poor", "terrible", "bad", "issue", "problem", "complaint", "delay"]
            
            transcript_lower = transcript.lower()
            for word in positive_words:
                if word in transcript_lower:
                    sentiment_score += 1
            for word in negative_words:
                if word in transcript_lower:
                    sentiment_score -= 1
                    
            customer_sentiments.append(sentiment_score)
        
        avg_response_time = 25  
        
        avg_sentiment = sum(customer_sentiments) / len(customer_sentiments) if customer_sentiments else 0
        
       
        resolution_rate = (resolution_count / len(transcripts)) * 100 if transcripts else 0
        
        
        most_common_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "None"
        
       
        most_mentioned_flights = sorted(flight_mentions.items(), key=lambda x: x[1], reverse=True)[:3] if flight_mentions else []
        
       
        kpi_result = {
            "total_calls": len(transcripts),
            "call_categories": categories,
            "resolution_rate": resolution_rate,
            "average_response_time": avg_response_time,
            "average_sentiment": avg_sentiment,
            "most_common_issue": most_common_category,
            "most_mentioned_flights": dict(most_mentioned_flights),
            "category_distribution": {category: (count / len(transcripts)) * 100 for category, count in categories.items()}
        }
        
        return json.dumps(kpi_result)
        
    except Exception as e:
        return json.dumps({"error": f"Error computing KPIs: {str(e)}"})


def main():
    st.set_page_config(
        page_title="AI-Powered Airline Call Center System",
        page_icon="✈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("✈ AI-Powered Airline Call Center System")
    st.markdown("---")
    
  
    if is_together_available():
        st.sidebar.success("Together AI API configured successfully")
    else:
        st.sidebar.warning("Together AI API not configured. Add TOGETHER_API_KEY to .env file for enhanced AI capabilities.")
    
 
    st.sidebar.title("Navigation")
    option = st.sidebar.radio(
        "Select a service:",
        ["Info Agent", "QA Response Agent", "Call Categorization", "KPI Analysis"]
    )
    
  
    def display_json(json_str):
        try:
            parsed_json = json.loads(json_str)
            
            tab1, tab2 = st.tabs(["Formatted View", "Raw JSON"])
            
            with tab1:
               
                if option == "Info Agent" and "error" not in parsed_json:
                    st.subheader(f"Flight {parsed_json.get('flight_number', 'N/A')} Information")
                    cols = st.columns(3)
                    with cols[0]:
                        st.metric("Destination", parsed_json.get("destination", "N/A"))
                        st.metric("Terminal", parsed_json.get("terminal", "N/A"))
                    with cols[1]:
                        st.metric("Departure", parsed_json.get("departure_time", "N/A"))
                        st.metric("Gate", parsed_json.get("gate", "N/A"))
                    with cols[2]:
                        st.metric("Status", parsed_json.get("status", "N/A"))
                        st.metric("Arrival", parsed_json.get("arrival_time", "N/A"))
                
                elif option == "QA Response Agent":
                    st.info(parsed_json.get("answer", "No answer provided"))
                    
                elif option == "Call Categorization" and "error" not in parsed_json:
                    st.subheader("Call Categorization Results")
                    st.metric("Category", parsed_json.get("category", "Unknown"))
                    
                    details = parsed_json.get("details", {})
                    if details:
                        st.subheader("Details")
                        cols = st.columns(2)
                        with cols[0]:
                            st.write("Customer:", details.get("customer_name", "Unknown"))
                            st.write("Resolution:", details.get("resolution_status", "Unknown"))
                        with cols[1]:
                            st.write("Flights Mentioned:", ", ".join(details.get("flight_numbers", ["None"])))
                            st.write("Summary:", details.get("call_summary", "No summary available"))
                
                elif option == "KPI Analysis" and "error" not in parsed_json:
                    st.subheader("Call Center KPI Dashboard")

                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Total Calls", parsed_json.get("total_calls", 0))
                    with cols[1]:
                        st.metric("Resolution Rate", f"{parsed_json.get('resolution_rate', 0):.1f}%")
                    with cols[2]:
                        st.metric("Avg Response Time", f"{parsed_json.get('average_response_time', 0)} sec")
                    with cols[3]:
                        sentiment = parsed_json.get('average_sentiment', 0)
                        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
                        st.metric("Customer Sentiment", sentiment_label, delta=sentiment)
                    
                    st.subheader("Call Categories")
                    categories = parsed_json.get("call_categories", {})
                    if categories:
                        for category, count in categories.items():
                            st.write(f"- {category}: {count} calls")
                    
                    st.subheader("Most Common Issue")
                    st.write(parsed_json.get("most_common_issue", "None identified"))
                    
                    st.subheader("Most Mentioned Flights")
                    flights = parsed_json.get("most_mentioned_flights", {})
                    for flight, count in flights.items():
                        st.write(f"- Flight {flight}: {count} mentions")
                
                else:
                    st.json(parsed_json)
            
            with tab2:
                st.json(parsed_json)
                
        except json.JSONDecodeError:
            st.error("Invalid JSON response")
            st.text(json_str)
    
    if option == "Info Agent":
        st.header("Flight Information Agent")
        st.write("Get detailed information about a specific flight by providing its flight number.")
        
        with st.form("info_agent_form"):
            flight_number = st.text_input("Flight Number (e.g., AI123)")
            submitted = st.form_submit_button("Get Flight Information")
            
        if submitted and flight_number:
            with st.spinner("Retrieving flight information..."):
                response = info_agent_request(flight_number)
                st.subheader("Flight Information")
                display_json(response)
    
    elif option == "QA Response Agent":
        st.header("Flight Query Agent")
        st.write("Ask questions about flights, such as departure times, destinations, or status updates.")
        
        if is_together_available():
            st.success("Using Together AI for enhanced natural language processing")
        
        with st.form("qa_agent_form"):
            user_query = st.text_input("Your Question (e.g., 'What is the status of flight AI123?')")
            submitted = st.form_submit_button("Submit Question")
            
        if submitted and user_query:
            with st.spinner("Processing your question..."):
                response = qa_agent_respond(user_query)
                st.subheader("Response")
                display_json(response)
    
    elif option == "Call Categorization":
        st.header("Call Categorization")
        st.write("Analyze and categorize customer service call transcripts.")
        
        if is_together_available():
            st.success("Using Together AI for enhanced call categorization")
        
        transcript_option = st.radio(
            "Choose a transcript option:",
            ["Use Sample Transcript", "Enter Custom Transcript"]
        )
        
        if transcript_option == "Use Sample Transcript":
            selected_index = st.selectbox(
                "Select a sample transcript:",
                range(len(SAMPLE_TRANSCRIPTS)),
                format_func=lambda i: f"Sample Transcript {i+1}"
            )
            transcript = SAMPLE_TRANSCRIPTS[selected_index]
            st.text_area("Transcript Preview", transcript, height=200, disabled=True)
        else:
            transcript = st.text_area(
                "Enter call transcript:",
                "Agent: Hello, thank you for calling Air Express. How may I assist you today?\nCustomer: ",
                height=200
            )
        
        if st.button("Categorize Call"):
            if transcript:
                with st.spinner("Analyzing call transcript..."):
                    response = categorize_call(transcript)
                    st.subheader("Categorization Results")
                    display_json(response)
            else:
                st.warning("Please enter a transcript to categorize.")
    
    elif option == "KPI Analysis":
        st.header("Call Center KPI Analysis")
        st.write("Compute and visualize key performance indicators from call transcripts.")
        
        if is_together_available():
            st.success("Using Together AI for enhanced KPI analysis and sentiment detection")
        
        use_samples = st.checkbox("Use Sample Transcripts", value=True)
        
        if use_samples:
            st.info(f"Using {len(SAMPLE_TRANSCRIPTS)} sample transcripts for KPI analysis.")
            
            if st.expander("Preview Sample Transcripts"):
                for i, transcript in enumerate(SAMPLE_TRANSCRIPTS):
                    st.markdown(f"*Sample Transcript {i+1}*")
                    st.text_area(f"transcript_{i}", transcript, height=100, disabled=True)
            
            if st.button("Compute KPIs"):
                with st.spinner("Analyzing call center data..."):
                    response = compute_call_center_kpis(SAMPLE_TRANSCRIPTS)
                    st.subheader("KPI Analysis Results")
                    display_json(response)
        else:
            st.error("Custom transcript upload is not implemented in this demo version.")
            st.info("Please use the sample transcripts for KPI analysis.")

    st.markdown("---")
    st.markdown("AI-Powered Airline Call Center Optimization System | Streamlit Demo with Together AI Integration")

if __name__ == "__main__":
    main()