import streamlit as st
import asyncio
import edge_tts

# App Title
st.title("🗣 Multi-Voice Conversation Generator")
st.write("Build a script line-by-line, assign accents, and add custom pauses before individual lines.")

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
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Hey Sonia, watch this! I can reply instantly.", "pause": 0.0},
        {"voice_label": "🇬🇧 Sonia (UK - Female)", "text": "Wow, that was fast. But what if I want to wait three seconds?", "pause": 0.0},
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Go ahead, turn up the pause slider on line three.", "pause": 3.0}
    ]

# --- UI Layout ---

st.subheader("📋 Edit Your Script")

# Loop through and display each line in the script
for i, line in enumerate(st.session_state.dialogue_lines):
    # Set up layout columns for inputs
    col1, col2, col3, col4 = st.columns([1, 2, 1, 0.2])
    
    with col1:
        line["voice_label"] = st.selectbox(
            f"Speaker {i+1}", 
            list(VOICE_DICT.keys()), 
            index=list(VOICE_DICT.keys()).index(line["voice_label"]),
            key=f"voice_{i}"
        )
    with col2:
        line["text"] = st.text_input(
            f"Dialogue Line {i+1}", 
            value=line["text"], 
            key=f"text_{i}", 
            label_visibility="collapsed",
            placeholder="Type what they say here..."
        )
        
    with col3:
        # Mini-slider for individual pause before this line starts
        # Only show the label on the first line to keep it clean
        slider_label = "Pause before line (s):" if i == 0 else ""
        line["pause"] = st.slider(
            slider_label,
            min_value=0.0,
            max_value=5.0,
            value=float(line["pause"]),
            step=0.1,
            key=f"pause_{i}"
        )
        
    with col4:
        # Delete row button
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.dialogue_lines.pop(i)
            st.rerun()

# Button to add new dialogue tracks
if st.button("➕ Add Line to Script"):
    st.session_state.dialogue_lines.append({"voice_label": "🇺🇸 Ava (US - Female)", "text": "", "pause": 0.5})
    st.rerun()

st.markdown("---")

# Helper function to generate audio with dynamic individual pauses
async def generate_conversation_audio(script):
    full_audio = b""
    
    for line in script:
        if line["text"].strip():
            system_voice = VOICE_DICT[line["voice_label"]]
            pause_secs = line["pause"]
            
            # Using SSML to inject the unique pause time specified for this specific line
            if pause_secs > 0:
                ssml_text = f"<speak><break time='{int(pause_secs * 1000)}ms'/>{line['text']}</speak>"
                communicate = edge_tts.Communicate(ssml_text, system_voice, is_ssml=True)
            else:
                communicate = edge_tts.Communicate(line["text"], system_voice)
                
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    full_audio += chunk["data"]
                    
    return full_audio

# --- Audio Generation ---
if st.button("🔊 Generate Full Conversation Audio", type="primary"):
    if not st.session_state.dialogue_lines:
        st.error("Your script is empty! Add some lines first.")
    else:
        with st.spinner("Compiling script with custom dialogue pauses..."):
            try:
                combined_audio = asyncio.run(generate_conversation_audio(st.session_state.dialogue_lines))
                
                if combined_audio:
                    st.success("🎉 Conversation compiled successfully!")
                    st.audio(combined_audio, format="audio/mp3")
                    st.download_button(
                        label="⬇️ Download Full Conversation (MP3)",
                        data=combined_audio,
                        file_name="custom_paced_conversation.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("The compiled audio file was empty. Make sure your lines contain text.")
            except Exception as e:
                st.error(f"Error compiling conversation: {e}")
