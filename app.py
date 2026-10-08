import streamlit as st
import asyncio
import edge_tts

# App Title
st.title("🗣 Text-to-Speech Voice Generator")

# 1. Premium Microsoft Edge English voices
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

# Map human speed slider values to edge-tts formatting strings (e.g. 1.0 -> "+0%", 1.5 -> "+50%")
speed_multiplier = st.slider("3. Adjust speed (Optional):", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
speed_percentage = int((speed_multiplier - 1.0) * 100)
speed_str = f"{speed_percentage:+}%" if speed_percentage != 0 else "+0%"

# Helper function to generate audio directly in the cloud
async def generate_audio(text, voice, speed):
    communicate = edge_tts.Communicate(text, voice, rate=speed)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# 3. Handle Generation & Downloading
if st.button("Generate Audio"):
    if not text_input.strip():
        st.error("Please enter some text first!")
    else:
        with st.spinner("Generating your audio file..."):
            try:
                # Execute the asynchronous voice generator
                audio_bytes = asyncio.run(generate_audio(text_input, selected_voice, speed_str))
                
                if audio_bytes:
                    st.success("🎉 Audio generated successfully!")
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label="⬇️ Download MP3 File",
                        data=audio_bytes,
                        file_name="generated_speech.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("Generated file was empty. Try changing the input text.")
            except Exception as e:
                st.error(f"Failed to generate speech: {e}")
