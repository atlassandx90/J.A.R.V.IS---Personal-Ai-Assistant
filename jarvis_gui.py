import tkinter as tk
from tkinter import PhotoImage, Text, Scrollbar
from PIL import Image, ImageTk
import threading
import requests
import pyttsx3
import speech_recognition as sr
import time

LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"

engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎙️ Listening...")
            speak("Listening...")
            audio = r.listen(source)

            try:
                query = r.recognize_google(audio)
                user_input.set(query)
                send_message()
            except sr.UnknownValueError:
                speak("Sorry, I didn’t catch that.")
            except sr.RequestError:
                speak("Speech service error.")
    except Exception as e:
        print(f"Microphone error: {e}")
        speak("Microphone not working.")

print("Available Microphones:")
print(sr.Microphone.list_microphone_names())

def ask_gemma(message):
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(LM_STUDIO_URL, json=payload, headers=headers)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


root = tk.Tk()
root.title("JARVIS - Personal AI")
root.state("zoomed")
root.configure(bg="black")


def resize_background(event=None):
    new_width = root.winfo_width()
    new_height = root.winfo_height()
    resized_img = bg_image.resize((new_width, new_height), Image.LANCZOS)
    root.bg_photo_resized = ImageTk.PhotoImage(resized_img)
    bg_label.config(image=root.bg_photo_resized)

bg_image = Image.open("background.jpg")
root.bg_photo_resized = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=root.bg_photo_resized)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
root.bind("<Configure>", resize_background)


title_label = tk.Label(root, text="JARVIS", font=("Consolas", 26, "bold"), fg="orange", bg="black")
title_label.place(relx=0.05, rely=0.05, anchor="center")

chatbox_frame = tk.Frame(root, bg="black")
chatbox_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.65)

chatbox = Text(chatbox_frame, bg="black", fg="#03fc98", font=("Consolas", 14), wrap="word", state="disabled")
chatbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
chatbox.tag_config("user", foreground="lightgreen")
chatbox.tag_config("jarvis", foreground="orange")

scrollbar = Scrollbar(chatbox_frame, command=chatbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chatbox.config(yscrollcommand=scrollbar.set)

user_input = tk.StringVar()

entry = tk.Entry(root, font=("Consolas", 14), bg="black", fg="#03fc98", insertbackground="cyan", textvariable=user_input)
entry.place(relx=0.10, rely=0.86, relwidth=0.55, relheight=0.06)

def send_message():
    msg = user_input.get()
    if msg.strip() == "":
        return

    chatbox.config(state="normal")
    chatbox.insert(tk.END, f"\n👨‍💻 You: {msg}\n", "user")
    chatbox.insert(tk.END, "🤖 JARVIS: ...\n", "jarvis")
    chatbox.config(state="disabled")
    chatbox.see(tk.END)

    user_input.set("")

    def ask():
        response = ask_gemma(msg)
        chatbox.config(state="normal")
        chatbox.insert(tk.END, f"\r🤖 JARVIS: {response}\n", "jarvis")
        chatbox.config(state="disabled")
        chatbox.see(tk.END)
        speak(response)

    threading.Thread(target=ask).start()

ask_btn = tk.Button(root, text="🤯 Ask JARVIS", font=("Consolas", 12, "bold"), bg="black", fg="#fcaf08", command=send_message)
ask_btn.place(relx=0.70, rely=0.85, relwidth=0.10, relheight=0.05)

def welcome_message():
    time.sleep(1)
    speak("Hello, I am Jarvis. How can I help you?")

threading.Thread(target=welcome_message).start()

root.mainloop()
