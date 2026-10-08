import streamlit as st
import asyncio
import edge_tts

# App Title
st.title("🗣 Multi-Voice Conversation Generator")
st.write("Build a script line-by-line, assign different accents, adjust pacing, and generate an audio file.")

# Premium Microsoft Edge English voices dictionary
VOICE_DICT = {
    "🇺🇸 Ava (US - Female)": "en-US-AvaNeural",
    "🇺🇸 Andrew (US - Male)": "en-US-AndrewNeural",
    "🇺🇸 Emma (US - Female)": "en-US-EmmaNeural",
    "🇺🇸 Brian (US - Male)": "en-US-BrianNeural",
    "🇬🇧 Sonia (UK - Female)": "en-GB-SoniaNeural",
    "🇬🇧 Ryan (UK - Male)": "en-GB-RyanNeural",
    "🇬🇧 Libby (UK - Female)": "en-GB-LibbyNeural",
    "🇬🇧 Oliver (UK - Male)": "en-GB-OliverNeural",
    "🇦🇺 Natasha (Australia - Female)": "en-AU-NatashaNeural",
    "🇦🇺 William (Australia - Male)": "en-AU-WilliamNeural",
    "🇨🇦 Clara (Canada - Female)": "en-CA-ClaraNeural",
    "🇨🇦 Liam (Canada - Male)": "en-CA-LiamNeural",
    "🇮🇳 Neerja (India - Female)": "en-IN-NeerjaNeural",
    "🇮🇳 Prabhat (India - Male)": "en-IN-PrabhatNeural",
    "🇮🇪 Emily (Ireland - Female)": "en-IE-EmilyNeural",
    "🇮🇪 Connor (Ireland - Male)": "en-IE-ConnorNeural",
    "🇳🇿 Molly (New Zealand - Female)": "en-NZ-MollyNeural",
    "🇳🇿 Mitchell (New Zealand - Male)": "en-NZ-MitchellNeural",
    "🇿🇦 Leah (South Africa - Female)": "en-ZA-LeahNeural",
    "🇿🇦 Luke (South Africa - Male)": "en-ZA-LukeNeural"
}

# Keep track of dialogue lines using Streamlit's session state memory
if "dialogue_lines" not in st.session_state:
    st.session_state.dialogue_lines = [
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Hello there! Welcome back to our conversation builder."},
        {"voice_label": "🇬🇧 Sonia (UK - Female)", "text": "Brilliant. Notice the gap between our voices now?"},
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Yes, you can make it longer or shorter using the control panel below."}
    ]

# --- UI Layout ---

st.subheader("📋 Edit Your Script")

# Loop through and display each line in the script
for i, line in enumerate(st.session_state.dialogue_lines):
    col1, col2, col3 = st.columns([1, 2, 0.3])
    
    with col1:
        line["voice_label"] = st.selectbox(
            f"Speaker {i+1}", 
            list(VOICE_DICT.keys()), 
            index=list(VOICE_DICT.keys()).index(line["voice_label"]),
            key=f"voice_{i}"
        )
    with col2:
        line["text"] = st.text_input(f"Dialogue Line {i+1}", value=line["text"], key=f"text_{i}", label_visibility="collapsed")
        
    with col3:
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.dialogue_lines.pop(i)
            st.rerun()

# Button to add new dialogue tracks
if st.button("➕ Add Line to Script"):
    st.session_state.dialogue_lines.append({"voice_label": "🇺🇸 Ava (US - Female)", "text": ""})
    st.rerun()

st.markdown("---")

st.subheader("⚙️ Conversation Settings")
# Global control slider for pause duration between speakers
pause_duration = st.slider(
    "Adjust pause between speakers (seconds):", 
    min_value=0.0, 
    max_value=3.0, 
    value=0.5, 
    step=0.1
)

st.markdown("---")

# Helper function to generate and stitch audio chunks together with true silence blocks
async def generate_conversation_audio(script, pause_secs):
    full_audio = b""
    
    # Calculate bytes needed for the silent gap (based on standard 24kHz MP3 encoding specs used by Edge-TTS)
    # 24000Hz * 16-bit (2 bytes) * mono = ~48000 bytes per second raw equivalent, but compressed MP3 varies.
    # An easy way to achieve an exact pause in edge-tts stream output is feeding empty space pauses 
    # or utilizing pure silence audio padding.
    
    for idx, line in enumerate(script):
        if line["text"].strip():
            system_voice = VOICE_DICT[line["voice_label"]]
            
            # If this isn't the first line, prepend a user-defined pause before the speaker begins
            if idx > 0 and pause_secs > 0:
                # Generate natural silence in the timeline stream by rendering blank spaces
                silence_communicator = edge_tts.Communicate(" ", system_voice)
                async for chunk in silence_communicator.stream():
                    pass 
                # Alternative: Let the async execution sleep to stagger the batch requests, 
                # but to structurally anchor the silence inside the raw file chunk data:
                # We can append a small empty byte pad or use an inline SSML break rule.
                
            # Connect to engine and generate the vocal audio block
            communicate = edge_tts.Communicate(line["text"], system_voice)
            
            # If a pause is requested, we can use the advanced SSML structure natively supported by edge-tts
            if idx > 0 and pause_secs > 0:
                # Wrapping the text payload inside an SSML structure to inject clean native pauses
                ssml_text = f"<speak><break time='{int(pause_secs * 1000)}ms'/>{line['text']}</speak>"
                communicate = edge_tts.Communicate(ssml_text, system_voice, is_ssml=True)
                
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    full_audio += chunk["data"]
                    
    return full_audio

# --- Audio Generation ---
if st.button("🔊 Generate Full Conversation Audio", type="primary"):
    if not st.session_state.dialogue_lines:
        st.error("Your script is empty! Add some lines first.")
    else:
        with st.spinner("Compiling script and rendering realistic timing gaps..."):
            try:
                combined_audio = asyncio.run(generate_conversation_audio(st.session_state.dialogue_lines, pause_duration))
                
                if combined_audio:
                    st.success("🎉 Conversation compiled beautifully!")
                    st.audio(combined_audio, format="audio/mp3")
                    st.download_button(
                        label="⬇️ Download Full Conversation (MP3)",
                        data=combined_audio,
                        file_name="paced_conversation.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("The compiled audio file was empty. Make sure your lines contain text.")
            except Exception as e:
                st.error(f"Error compiling conversation: {e}")
