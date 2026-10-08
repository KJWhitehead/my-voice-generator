import streamlit as st
import asyncio
import edge_tts

# App Title
st.title("🗣 Multi-Voice Conversation Generator")
st.write("Build a script line-by-line, assign different accents, and generate a single audio file.")

# Premium Microsoft Edge English voices dictionary for cleaner labels
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
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Hello there! Welcome to our new conversation tool."},
        {"voice_label": "🇬🇧 Sonia (UK - Female)", "text": "Brilliant! So I can speak with a British accent right after you?"},
        {"voice_label": "🇺🇸 Andrew (US - Male)", "text": "Exactly. You can add as many script lines as you want."}
    ]

# --- UI Layout ---

st.subheader("📋 Edit Your Script")

# Loop through and display each line in the script
for i, line in enumerate(st.session_state.dialogue_lines):
    col1, col2, col3 = st.columns([3, 6, 1])
    
    with col1:
        # Dropdown to choose the speaker's accent
        line["voice_label"] = st.selectbox(
            f"Speaker {i+1}", 
            list(VOICE_DICT.keys()), 
            index=list(VOICE_DICT.keys()).index(line["voice_label"]),
            key=f"voice_{i}"
        )
    with col2:
        # Text box for what they say
        line["text"] = st.text_input(f"Dialogue Line {i+1}", value=line["text"], key=f"text_{i}", label_visibility="collapsed")
        
    with col3:
        # Delete button for a line
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.dialogue_lines.pop(i)
            st.rerun()

# Button to add new dialogue tracks
if st.button("➕ Add Line to Script"):
    st.session_state.dialogue_lines.append({"voice_label": list(VOICE_DICT.keys())[0], "text": ""})
    st.rerun()

st.markdown("---")

# Helper function to stitch audio chunks together in chronological order
async def generate_conversation_audio(script):
    full_audio = b""
    for line in script:
        if line["text"].strip():
            system_voice = VOICE_DICT[line["voice_label"]]
            communicate = edge_tts.Communicate(line["text"], system_voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    full_audio += chunk["data"]
            # Add a tiny quarter-second pause between speakers so they don't talk over each other
            await asyncio.sleep(0.25)
    return full_audio

# --- Audio Generation ---
if st.button("🔊 Generate Full Conversation Audio", type="primary"):
    if not st.session_state.dialogue_lines:
        st.error("Your script is empty! Add some lines first.")
    else:
        with st.spinner("Stitching voices together into one audio track..."):
            try:
                combined_audio = asyncio.run(generate_conversation_audio(st.session_state.dialogue_lines))
                
                if combined_audio:
                    st.success("🎉 Conversation audio compiled successfully!")
                    st.audio(combined_audio, format="audio/mp3")
                    st.download_button(
                        label="⬇️ Download Full Conversation (MP3)",
                        data=combined_audio,
                        file_name="conversation.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("The compiled audio file was empty. Make sure your lines contain text.")
            except Exception as e:
                st.error(f"Error compiling conversation: {e}")
