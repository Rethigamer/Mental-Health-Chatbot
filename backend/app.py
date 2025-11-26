from flask import Flask, render_template, request, jsonify, session
from google import genai
from google.genai import types
from collections import Counter
import os

# --- Configuration & Initialization ---
app = Flask(__name__)
# REQUIRED for session management
app.secret_key = 'super_secret_key_for_session_management' 

# 3. Gemini API Setup
# --- IMPORTANT: Ensure GEMINI_API_KEY is valid ---
GEMINI_API_KEY = "AIzaSyDEHliHDg3Erac8skKyMh9LfqVyGXKSb28" # <<< REPLACE THIS
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    exit()

# System Instruction (Same as before)
GEMINI_SYSTEM_INSTRUCTION = """
You are a friendly, interactive, and brief assistant designed for natural conversation.
Your goal is to chat normally with the user, like a helpful friend.
For every user message, you will be provided with an analyzed sentiment for that message in the format: SENTIMENT = {sentiment}.
Crucial Rules:
1. NEVER reveal the sentiment value (e.g., 'SENTIMENT = positive').
2. NEVER mention that you are using a sentiment model.
3. Keep your responses short, friendly, and natural.
4. When the user signals the end of the chat (e.g., 'thank you', 'bye', 'stop', 'done', etc.), you must politely and clearly end the conversation. Your final response should be a friendly farewell.
5. You must detect these ending phrases: "thank you", "thanks", "thank u", "ok bye", "bye", "that’s all", "stop", "done", "end chat", "no more", "exit", "goodbye".
"""

END_PHRASES = [
    "thank you", "thanks", "thank u", "ok bye", "bye",
    "that's all", "stop", "done", "end chat", "no more", "exit", "goodbye"
]

# --- Sentiment Analysis MOCK Function ---
# Global variable to cycle through sentiments for testing
_sentiment_cycle_index = 0
_SENTIMENTS = ["positive", "neutral", "negative"]

def analyze_sentiment(text):
    """
    MOCK function to replace Azure API call. 
    It cycles through positive, neutral, and negative for testing.
    """
    global _sentiment_cycle_index
    
    if any(phrase in text.lower() for phrase in END_PHRASES):
        return "positive" 

    sentiment = _SENTIMENTS[_sentiment_cycle_index % len(_SENTIMENTS)]
    _sentiment_cycle_index += 1
    return sentiment


# --- Route Handlers ---

@app.route("/")
def index():
    # Reset chat state if not found in session
    if 'chat_history_dicts' not in session or 'all_sentiments' not in session:
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_INSTRUCTION
            )
        )
        # Store history as a list of dicts using model_dump()
        session['chat_history_dicts'] = [c.model_dump() for c in chat.get_history()] 
        session['all_sentiments'] = []
    
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"bot": "Please enter a message.", "end": False})

    history_dicts = session.get('chat_history_dicts', [])
    all_sentiments = session.get('all_sentiments', [])
    
    # FIX: Re-create the chat history by using model_validate() instead of from_dict()
    history_content = [types.Content.model_validate(d) for d in history_dicts]

    chat = client.chats.create(
        model="gemini-2.5-flash",
        history=history_content,
        config=types.GenerateContentConfig(
            system_instruction=GEMINI_SYSTEM_INSTRUCTION
        )
    )

    # 1. Analyze sentiment 
    current_sentiment = analyze_sentiment(user_input)
    all_sentiments.append(current_sentiment)

    # 2. Check for end phrases
    is_ending = any(
        phrase in user_input.lower() for phrase in END_PHRASES
    )

    # 3. Construct the prompt for Gemini
    gemini_prompt = (
        f"SENTIMENT = {current_sentiment.upper()}: "
        f"{user_input}"
    )

    # 4. Get response from Gemini
    try:
        response = chat.send_message(gemini_prompt)
        bot_reply = response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        bot_reply = "I'm sorry, I ran into a technical issue. Could you please try again?"
        is_ending = True

    # 5. Handle chat end logic
    if is_ending:
        
        if all_sentiments:
            final_sentiment = Counter(all_sentiments).most_common(1)[0][0]
        else:
            final_sentiment = "N/A"
            
        session.pop('chat_history_dicts', None)
        session.pop('all_sentiments', None)
        
        return jsonify({
            "bot": bot_reply,
            "sentiment": final_sentiment.upper(),
            "end": True 
        })

    else:
        # 6. Update session history for the next turn
        session['chat_history_dicts'] = [c.model_dump() for c in chat.get_history()]
        session['all_sentiments'] = all_sentiments
        
        return jsonify({
            "bot": bot_reply,
            "end": False
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)