import RPi.GPIO as GPIO
import time
import keyboard
import pyttsx3
import speech_recognition as sr
import openai
import pyaudio
import wave
import tempfile
import os

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

API_KEY = "Enter API Key Here"
openai.api_key = API_KEY
name = "Tyson"

def listen_and_convert_to_text(mic_index):
    recognizer = sr.Recognizer()
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000
    audio = pyaudio.PyAudio()
    
    while True:
        print("Please hold down the spacebar and start speaking...")
        while not GPIO.input(10) == GPIO.HIGH:
            time.sleep(0.1)
            
        stream = audio.open(format=format, channels=channels, rate=rate, input=True, input_device_index=mic_index, frames_per_buffer=chunk)
        frames = []
        
            
        print("Recording...")
        while GPIO.input(10) == GPIO.HIGH:
            data = stream.read(chunk)
            frames.append(data)
            
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        
        # Save the recorded audio to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_filename = temp_file.name
        with wave.open(temp_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            
        with sr.AudioFile(temp_filename) as source:
            audio_data = recognizer.record(source)
            
        # Clean up the temporary file
        os.unlink(temp_filename)
        
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            return text
        except sr.UnknownValueError:
            print("No speech detected. Please hold down the button and try again.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return None
        except KeyboardInterrupt:
            break
        
    audio.terminate()
    
def generate_rogerian_response(user_message, conversation_history):
    conversation_history.append(f"Patient: {user_message}")
    # using Rogerian Therapy methods
    prompt = f"ChatGPT, you are a Rogerian Therapist responding to your patient {name}. This is the conversation history you have already had with {name}.\n"
    
    for i, message in enumerate(conversation_history):
        prompt += f"{message}\n \n"
        
    prompt += f"As a Rogerian therapist responding to your patient {name}, it's important to use the conversation history to provide empathetic and personalized support while including Rogerian Therapy techniques. Here's how to respond to {name}'s message:\n\n Look at the conversation history to understand {name}'s thoughts and feelings, and use this information to guide your response.\n Do not repeat the patient's message or your own wording. Instead, use different phrasing and grammatical structures to avoid repetition.\n Be empathetic and supportive by using language that shows you understand how {name} is feeling. For example, you could say \"I can imagine that must be really tough for you\" or \"It sounds like you're feeling really overwhelmed right now\". \n Occasionally ask open-ended questions to encourage {name} to share more about their experiences. For example, you could ask \"Can you tell me more about how that made you feel?\" or \"What do you think might help you feel better?\"\n Avoid constantly asking how {name} is feeling. Instead, use different questions to respond to {name}'s message.\n \n \n Remember, your goal is to provide personalized support and help {name} work through their challenges. By using the conversation history to guide your responses and using empathetic language, you can help {name} feel heard and supported.\n Now, please use this information to respond to {name}'s message."
    prompt += f"\n \n \n Here is {name}'s message: {user_message}\n"
    
    print (prompt)
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        temperature=0.99,
        max_tokens=1048,
        top_p=1,
        frequency_penalty=0.6,
        presence_penalty=0.4,	
    )
    response_text = response.choices[0].text.strip()
    
    response_text = response_text.replace("Patient:", "").replace(user_message, "").replace("Sam:", "").replace("Therapist:", "").strip()
    
    return response_text


def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    mic_index = 0
    conversation_history = []
    
    while True:
        text = listen_and_convert_to_text(mic_index)
        if text is None:
            break
        print(f"User: {text}")
        
        rogerian_response = generate_rogerian_response(text, conversation_history)
        print(f"Therapist: {rogerian_response}")
        
        conversation_history.append(f"Therapist: {rogerian_response}")
        
        speak_text(rogerian_response)
        
if __name__ == "__main__":
    main()
    