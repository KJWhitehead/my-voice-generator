import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import requests

# App Title
st.title("🗣 Text-to-Speech Voice Generator")

# Configuration for your running OrbStack container
API_URL = "https://travisvn.com"
API_KEY = "your_api_key_here"

# 1. Hardcoded list of premium Microsoft Edge English voices
voice_options = [
    "en-US-AvaNeural", "en-US-AndrewNeural", "en-US-EmmaNeural", "en-US-BrianNeural",
    "en-US-AnaNeural", "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-GuyNeural",
    "en-US-JennyNeural", "en-US-MichelleNeural", "en-GB-SoniaNeural", "en-GB-RyanNeural",
    "en-GB-LibbyNeural", "en-GB-OliverNeural", "en-AU-NatashaNeural", "en-AU-WilliamNeural",
    "en-CA-ClaraNeural", "en-CA-LiamNeural", "en-IN-NeerjaNeural", "en-IN-PrabhatNeural",
    "en-IE-EmilyNeural", "en-IE-ConnorNeural", "en-NZ-MollyNeural", "en-NZ-MitchellNeural",
    "en-ZA-LeahNeural", "en-ZA-LukeNeural"
]

# 2. Build the User Interface
text_input = st.text_area("1. Type your text here:", value="Hello! Welcome to your custom text-to-speech generator.")
selected_voice = st.selectbox("2. Choose an accent / voice:", voice_options)
speed = st.slider("3. Adjust speed (Optional):", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# 3. Handle Generation & Downloading
if st.button("Generate Audio"):
    if not text_input.strip():
        st.error("Please enter some text first!")
    else:
        with st.spinner("Generating your audio file..."):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            payload = {
                "model": "tts-1",
                "input": text_input,
                "voice": selected_voice,
                "response_format": "mp3",
                "speed": speed
            }
            
            try:
                res = requests.post(API_URL, json=payload, headers=headers)
                if res.status_code == 200:
                    st.success("🎉 Audio generated successfully!")
                    st.audio(res.content, format="audio/mp3")
                    st.download_button(
                        label="⬇️ Download MP3 File",
                        data=res.content,
                        file_name="generated_speech.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error(f"Error from server: {res.text}")
            except Exception as e:
                st.error(f"Failed to connect to the audio engine: {e}")