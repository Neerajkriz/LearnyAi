from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from huggingface_hub import InferenceClient
from gtts import gTTS
import re
import io
import base64
import time
from PIL import Image
from collections import deque
from threading import Lock
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

# Initialize rate-limiting variables
REQUEST_LIMIT = 3  # API limit: 3 requests per minute
REQUEST_WINDOW = 70  # Time window in seconds
request_times = deque()  # To track timestamps of requests
lock = Lock()  # To synchronize access to shared variables

@app.route('/', methods=['GET', 'POST'])
def home():
    audio_path = None
    prompt_image_map = {}  # Initialize this to avoid issues if not in POST request
    if request.method == 'POST':
        # Store the topic in the session
        topic = request.form['name']
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        print(topic)
        llama_client = InferenceClient(api_key="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")
        messages = [
        {
            "role": "user",
            "content": f"Create a short, engaging story that explains the concept of {topic} in a way that is easy to understand for differently-abled students. The story should be no more than 150 words and include sentences with at least 6 words each. Use relatable characters, vivid imagery, and a simple narrative to ensure the story flows smoothly and maintains the reader’s attention. The story should illustrate the concept in a fun, imaginative way that promotes learning and encourages curiosity. Make sure there is a clear connection between events, so the students can follow along easily and understand the main idea by the end."
        }
        ]
        completion = llama_client.chat.completions.create(
            model="meta-llama/Llama-3.2-3B-Instruct", 
            messages=messages, 
            max_tokens=500
        )

        generated_story = completion['choices'][0]['message']['content']

        # Clean and split story into sentences
        cleaned_story = generated_story.replace("*", "")
        cleaned_story2 = cleaned_story.replace("\n", "")

        split_story = re.split(r'[.!]+', cleaned_story2)
        processed_lines = [line.strip() for line in split_story if line.strip()]
        print(processed_lines)

        # Initialize Stable Diffusion API Client
        sd_client = InferenceClient(
            api_key="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",
            model="stabilityai/stable-diffusion-3.5-large-turbo"
        )

        prompt_image_map = {}
        # Generate images for each line in the story
        for line in processed_lines:
            with lock:  # Ensure thread-safe access
                # Remove timestamps older than the rate limit window
                while request_times and time.time() - request_times[0] > REQUEST_WINDOW:
                    request_times.popleft()

                # Check if we have hit the request limit
                if len(request_times) >= REQUEST_LIMIT:
                    print("Rate limit reached. Waiting for reset...")
                    time.sleep(REQUEST_WINDOW - (time.time() - request_times[0]))
                    request_times.popleft()

                # Add the current timestamp to the tracker
                request_times.append(time.time())

            # Generate image
            image = sd_client.text_to_image(line)

            # Convert the image to a base64 string
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Map the prompt (line) to its generated image
            prompt_image_map[line] = img_str
        print(prompt_image_map)

                # Generate audio for the story
        tts = gTTS(generated_story)
        audio_path = "static/story_audio.mp3"
        tts.save(audio_path)

    return render_template('form.html', prompt_image_map=prompt_image_map,audio_path=audio_path)

@app.route('/play_audio', methods=['GET'])
def play_audio():
    return send_file("static/story_audio.mp3", as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True)