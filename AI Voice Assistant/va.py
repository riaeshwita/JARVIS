import os
import datetime
import subprocess
import requests
import webbrowser
import wikipedia
import pyttsx3
import speech_recognition as sr
import wolframalpha
import re
import json
import pyjokes


# Text-to-Speech Initialization
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def speak_and_log(text, log_function):
    speak(text)
    log_function(text)

def strip_latex(math_text):
    text = re.sub(r"\\[a-zA-Z]+\{([^{}]+)\}", r"\1", math_text)
    text = re.sub(r"[\\{}]", "", text)
    return text

def wishMe(log_function):
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak_and_log("Hello, Good Morning Ria", log_function)
    elif hour < 18:
        speak_and_log("Hello, Good Afternoon Ria", log_function)
    else:
        speak_and_log("Hello, Good Evening Ria", log_function)

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
            statement = r.recognize_google(audio, language='en-in')
            print(f"User said: {statement}\n")
            return statement
        except Exception:
            return "None"

def query_ollama(user_input):
    try:
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "deepseek-r1:8b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are JARVIS, a helpful AI assistant created by Ria. "
                        "You must always respond clearly, solve math questions, and identify equations."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                part = line.decode("utf-8")
                if part.startswith("data:"):
                    content = part.replace("data:", "").strip()
                    try:
                        json_data = json.loads(content)
                        full_response += json_data.get("message", {}).get("content", "")
                    except Exception:
                        continue
        return full_response.strip()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        try:
            print(f"Response: {response.text}")
        except:
            pass
        return f"Error contacting Ollama: {str(e)}"

def start_assistant_logic(log_function, stop_signal):
    wishMe(log_function)
    log_function("Assistant is listening...\n")

    while not stop_signal.is_set():
        try:
            statement = takeCommand().lower()
            if log_function and statement != "none":
                log_function(statement, is_assistant_response=False)

            if statement == "none":
                continue

            if "good bye" in statement or "ok bye" in statement or "stop" in statement:
                speak_and_log("Your personal assistant Jarvis is shutting down. Goodbye!", log_function)
                stop_signal.set()
                break

            elif 'wikipedia' in statement:
                speak_and_log("Searching Wikipedia...", log_function)
                statement = statement.replace("wikipedia", "")
                results = wikipedia.summary(statement, sentences=2)
                speak_and_log("According to Wikipedia", log_function)
                speak_and_log(results, log_function)

            elif "open youtube" in statement:
                webbrowser.open_new_tab("https://www.youtube.com")
                speak_and_log("YouTube is open", log_function)

            elif "open google" in statement:
                webbrowser.open_new_tab("https://www.google.com")
                speak_and_log("Google is open", log_function)

            elif "open gmail" in statement:
                webbrowser.open_new_tab("https://mail.google.com")
                speak_and_log("Gmail is open", log_function)

            elif "close chrome" in statement or "close browser" in statement:
                os.system("taskkill /f /im msedge.exe")
                speak_and_log("Closing Chrome browser", log_function)

            elif "weather" in statement:
                api_key = "8ef61edcf1c576d65d836254e11ea420"
                base_url = "https://api.openweathermap.org/data/2.5/weather?"
                speak_and_log("What's your city name?", log_function)
                city_name = takeCommand()
                complete_url = f"{base_url}appid={api_key}&q={city_name}"
                response = requests.get(complete_url)
                x = response.json()
                if x["cod"] != "404":
                    y = x["main"]
                    current_temperature = y["temp"]
                    current_humidity = y["humidity"]
                    z = x["weather"]
                    weather_description = z[0]["description"]
                    weather_info = f"Temperature: {current_temperature} K, Humidity: {current_humidity}%, Weather: {weather_description}"
                    speak_and_log(weather_info, log_function)
                else:
                    speak_and_log("City not found", log_function)

            elif "time" in statement:
                strTime = datetime.datetime.now().strftime("%H:%M:%S")
                speak_and_log(f"The time is {strTime}", log_function)

            elif "joke" in statement or "make me laugh" in statement:
                joke = pyjokes.get_joke()
                speak_and_log(joke, log_function)

            elif "do you know" in statement:
                topic = statement.replace("do you know", "").strip()
                if topic:
                    speak_and_log(f"Let me show you information about {topic}.", log_function)
                    webbrowser.open_new_tab(f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}")
                    speak_and_log(f"Opening Wikipedia page for {topic}.", log_function)
                else:
                    speak_and_log("Please ask about a specific topic.", log_function)

            elif "who are you" in statement or "what can you do" in statement:
                response = "I am Jarvis, your personal assistant. I can open websites, tell the time and weather, search Wikipedia, and answer questions."
                speak_and_log(response, log_function)

            elif "who made you" in statement or "who created you" in statement:
                speak_and_log("I was built by Roux at AiRobosoft", log_function)

            elif "open stack overflow" in statement:
                webbrowser.open_new_tab("https://stackoverflow.com")
                speak_and_log("Stack Overflow is open", log_function)

            elif "news" in statement:
                webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
                speak_and_log("Here are the latest headlines", log_function)

            elif "search" in statement:
                query = statement.replace("search", "")
                webbrowser.open_new_tab(f"https://www.google.com/search?q={query}")
                speak_and_log(f"Searching for {query}", log_function)

            elif any(op in statement for op in ["calculate", "plus", "minus", "multiply", "divide", "mod", "remainder", "power", "math", "mathematics", "calculation"]) or re.search(r"\d+[\+\-\*/\^=]", statement):
                try:
                    speak_and_log("Let me calculate that for you.", log_function)
                    app_id = "R2K75H-7ELALHR35X"
                    client = wolframalpha.Client(app_id)
                    res = client.query(statement)
                    answer = next(res.results).text
                    clean_answer = strip_latex(answer)
                    speak_and_log(clean_answer, log_function)
                except Exception:
                    ollama_reply = query_ollama(statement)
                    speak_and_log(strip_latex(ollama_reply), log_function)

            elif re.search(r"(what|who|where|how) .*", statement):
                speak_and_log("Let me find it for you.", log_function)
                try:
                    app_id = "R2K75H-7ELALHR35X"
                    client = wolframalpha.Client(app_id)
                    res = client.query(statement)
                    answer = next(res.results).text
                    clean_answer = strip_latex(answer)
                    speak_and_log(clean_answer, log_function)
                except Exception:
                    ollama_reply = query_ollama(statement)
                    speak_and_log(strip_latex(ollama_reply), log_function)

            elif "log off" in statement or "sign out" in statement or "shut down" in statement:
                speak_and_log("Okay, your PC will shut down in 10 seconds", log_function)
                os.system("shutdown /s /t 10")

            elif "good morning" in statement:
                speak_and_log("Good morning! How can I help you today?", log_function)

            elif "good afternoon" in statement:
                speak_and_log("Good afternoon! What would you like me to do?", log_function)

            elif "good evening" in statement:
                speak_and_log("Good evening! Need any assistance?", log_function)

            elif re.search(r"\d+[\+\-\*/\^=]", statement):
                try:
                    app_id = "R2K75H-7ELALHR35X"
                    client = wolframalpha.Client(app_id)
                    res = client.query(statement)
                    answer = next(res.results).text
                    clean_answer = strip_latex(answer)
                    speak_and_log(clean_answer, log_function)
                except Exception:
                    speak_and_log("Could not calculate that. Let me try another method.", log_function)

            elif any(op in statement for op in ["calculate", "plus", "minus", "multiply", "divide", "mod", "remainder", "power", "math", "mathematics", "calculation"]):
                speak_and_log("Opening Calculator.", log_function)
                try:
                    subprocess.Popen("calc.exe")
                except Exception as e:
                    speak_and_log(f"Failed to open calculator: {e}", log_function)

        except Exception as e:
            speak_and_log(f"Error: {str(e)}", log_function)

