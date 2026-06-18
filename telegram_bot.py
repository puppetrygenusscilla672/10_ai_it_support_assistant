import os
import sqlite3
import urllib.request
import json
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

DB_NAME = "tickets_knowledge_base.db"
OLLAMA_URL = "http://localhost:11434/api/generate"
CONFIG_FILE = "config_bot.json"

# Load or create bot config
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "telegram_bot_token": "",
            "allowed_chat_ids": [],
            "ollama_model": "qwen2.5-coder:7b"
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {}

# Train fallback Naive Bayes model
def train_fallback_model():
    if not os.path.exists(DB_NAME):
        return None
    try:
        conn = sqlite3.connect(DB_NAME)
        df_db = pd.read_sql_query("SELECT description, category FROM tickets", conn)
        conn.close()
        
        if len(df_db) == 0:
            return None
            
        model = make_pipeline(TfidfVectorizer(lowercase=True, stop_words='english'), MultinomialNB())
        model.fit(df_db["description"], df_db["category"])
        return model
    except Exception as e:
        print(f"Error training fallback model: {e}")
        return None

fallback_classifier = train_fallback_model()

# Fallback Solutions dictionary
fallback_solutions = {
    "Network & Internet": {
        "priority": "Medium",
        "checklist": [
            "Verify cable connection / Kiểm tra kết nối cáp mạng",
            "Flush local DNS / Xoá bộ nhớ đệm DNS local",
            "Release and renew IP address / Cấp phát lại địa chỉ IP"
        ],
        "script": "Clear-DnsClientCache\nipconfig /release\nipconfig /renew"
    },
    "Hardware & Peripherals": {
        "priority": "Low",
        "checklist": [
            "Verify physical cable connection / Kiểm tra cáp vật lý",
            "Check device power / Kiểm tra nguồn thiết bị",
            "Restart device Manager spooler / Khởi động lại Spooler quản lý thiết bị"
        ],
        "script": "Restart-Service -Name Spooler -Force\npnputil /scan-devices"
    },
    "Software & OS": {
        "priority": "Medium",
        "checklist": [
            "Verify Task Manager usage / Kiểm tra hiệu suất CPU/RAM",
            "Reboot OS / Khởi động lại hệ điều hành",
            "Scan file system integrity / Quét tính toàn vẹn hệ thống tệp"
        ],
        "script": "sfc /scannow\nDISM /Online /Cleanup-Image /RestoreHealth"
    },
    "Access & Security": {
        "priority": "High",
        "checklist": [
            "Verify Caps Lock key / Kiểm tra phím Caps Lock",
            "Confirm domain connection / Xác nhận kết nối tên miền",
            "Check active directory lockout status / Kiểm tra trạng thái khoá tài khoản AD"
        ],
        "script": "net user $env:USERNAME"
    },
    "General": {
        "priority": "Low",
        "checklist": [
            "Inspect basic configurations / Kiểm tra cấu hình cơ bản",
            "Perform physical system restart / Thực hiện khởi động lại hệ thống"
        ],
        "script": "# Execute generic diagnostics\nWrite-Host 'Running basic system diagnostics...'"
    }
}

# Audit Ollama status
def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            models = [m["name"] for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []

# RAG Retrieval Engine
def retrieve_similar_tickets(query, num_results=3):
    if not os.path.exists(DB_NAME):
        return []
    try:
        conn = sqlite3.connect(DB_NAME)
        tickets = pd.read_sql_query("SELECT id, description, category, resolution, script FROM tickets", conn)
        conn.close()
        
        if len(tickets) == 0:
            return []
            
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(tickets["description"])
        query_vector = vectorizer.transform([query])
        
        similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[-num_results:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:
                results.append(tickets.iloc[idx].to_dict())
        return results
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return []

# Query local Ollama API
def query_local_llm(model_name, prompt):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        OLLAMA_URL, 
        data=data, 
        headers={'Content-Type': 'application/json'},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=300) as response:
        res_data = json.loads(response.read().decode())
        return res_data.get("response", "")

# Telegram Bot API utilities
def get_updates(token, offset=None):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    if offset:
        url += f"?offset={offset}&timeout=10"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Error fetching updates: {e}")
        return None

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"Markdown send failed, retrying with plain text: {e}")
        payload["parse_mode"] = ""
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e2:
            print(f"Send message failed: {e2}")

def main():
    print("=========================================")
    print("🤖 Starting Local AI IT Support Telegram Bot...")
    print("=========================================")
    
    config = load_config()
    token = config.get("telegram_bot_token", "")
    allowed_chats = config.get("allowed_chat_ids", [])
    configured_model = config.get("ollama_model", "qwen2.5-coder:7b")
    
    if not token:
        print(f"[WARNING] 'telegram_bot_token' is empty in '{CONFIG_FILE}'.")
        print("Please edit the config file, enter your bot token, and restart this script.")
        return

    offset = None
    print(f"Bot is listening for messages... (Configured model: {configured_model})")
    
    while True:
        updates = get_updates(token, offset)
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                offset = update.get("update_id") + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")
                
                if not text or not chat_id:
                    continue
                
                # Check authorization if list is configured
                if allowed_chats and chat_id not in allowed_chats:
                    print(f"Ignored unauthorized message from Chat ID: {chat_id}")
                    send_message(token, chat_id, "❌ You are not authorized to use this IT Support Bot.")
                    continue
                
                print(f"Received issue query from Chat ID {chat_id}: '{text}'")
                
                # Command handling
                if text.startswith("/start") or text.startswith("/help"):
                    welcome = (
                        "💻 *AI IT Support Assistant* 🤖\n\n"
                        "Send me any computer issue or error message you are experiencing, "
                        "and I will query our local Knowledge Base and use our local AI to "
                        "diagnose the issue and write recovery scripts for you!\n\n"
                        "*Example queries:*\n"
                        "- `Cannot connect to Wi-Fi`\n"
                        "- `Printer queue is stuck / Kẹt hàng đợi máy in`\n"
                        "- `Blue screen of death / Lỗi màn hình xanh`"
                    )
                    send_message(token, chat_id, welcome)
                    continue
                
                # Send typing feedback
                send_message(token, chat_id, "🔍 *Analyzing your issue, searching knowledge base...*")
                
                # Step 1: Retrieval (RAG)
                similar_tickets = retrieve_similar_tickets(text, 2)
                
                # Step 2: Diagnostic & Generation
                ollama_online, installed_models = check_ollama()
                
                # Choose active model
                model_to_use = configured_model
                if ollama_online and installed_models:
                    if configured_model not in installed_models:
                        model_to_use = installed_models[0]
                
                if ollama_online:
                    context_str = ""
                    for i, ticket in enumerate(similar_tickets):
                        context_str += f"Ticket {i+1}:\n- Description: {ticket['description']}\n- Category: {ticket['category']}\n- Resolution: {ticket['resolution']}\n- Script:\n{ticket['script']}\n\n"
                    
                    prompt = (
                        "You are an expert IT Systems Engineer and Level 2 Helpdesk support specialist.\n"
                        "Review the following user issue and similar past tickets to formulate a solution.\n\n"
                        f"### Similar Resolved Tickets (Context):\n{context_str}\n"
                        f"### User Issue to Resolve:\n{text}\n\n"
                        "### Output requirements:\n"
                        "1. Predicted Category (Network & Internet, Hardware & Peripherals, Software & OS, or Access & Security)\n"
                        "2. Suggested Priority Level (Low, Medium, High)\n"
                        "3. Step-by-step troubleshooting checklist\n"
                        "4. A clean, executable PowerShell or Bash script block to diagnostic/fix the issue.\n\n"
                        "Respond in clear, professional English or Vietnamese (based on user's query language). "
                        "Keep the explanation concise and direct."
                    )
                    
                    try:
                        response_text = query_local_llm(model_to_use, prompt)
                        send_message(token, chat_id, f"🤖 *AI Resolution Report ({model_to_use}):*\n\n{response_text}")
                    except Exception as e:
                        print(f"Ollama query failed: {e}")
                        ollama_online = False
                
                if not ollama_online:
                    # Fallback to Naive Bayes
                    global fallback_classifier
                    if not fallback_classifier:
                        fallback_classifier = train_fallback_model()
                        
                    predicted_category = "General"
                    if fallback_classifier:
                        try:
                            predicted_category = fallback_classifier.predict([text])[0]
                        except Exception:
                            pass
                            
                    sol = fallback_solutions.get(predicted_category, fallback_solutions["General"])
                    priority = sol["priority"]
                    script = sol["script"]
                    
                    checklist_str = "\n".join([f"- [ ] {c}" for c in sol["checklist"]])
                    
                    fallback_report = (
                        "⚠️ *Ollama local LLM is offline. Running Fallback Rule-based Classifier...*\n\n"
                        f"📦 *Predicted Category:* `{predicted_category}`\n"
                        f"⚡ *Priority:* `{priority}`\n\n"
                        f"🔍 *Troubleshooting Checklist:*\n{checklist_str}\n\n"
                        f"💻 *Automated Recovery Script (PowerShell):*\n```powershell\n{script}\n```"
                    )
                    send_message(token, chat_id, fallback_report)
                    
        time.sleep(1)

if __name__ == "__main__":
    main()
