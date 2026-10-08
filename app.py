import streamlit as st
import asyncio
import edge_tts
import io
from pydub import AudioSegment

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
        if st.button("❌", key=f"delete_{i}"):
            st.session_state.dialogue_lines.pop(i)
            st.rerun()

# Dynamic row actions placed side-by-side using columns
btn_col1, btn_col2 = st.columns([1, 3])

with btn_col1:
    if st.button("➕ Add Line"):
        st.session_state.dialogue_lines.append({"voice_label": "🇺🇸 Ava (US - Female)", "text": "", "pause": 0.5})
        st.rerun()

with btn_col2:
    if st.button("🗑️ Clear Script"):
        # Reset the dynamic dialogue tracks memory back to a single completely blank starting row
        st.session_state.dialogue_lines = [{"voice_label": "🇺🇸 Ava (US - Female)", "text": "", "pause": 0.0}]
        st.rerun()

st.markdown("---")

# Helper function to generate individual speech segments
async def get_voice_bytes(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# Master audio compiler function using Pydub to cleanly merge voice and true silence
def compile_conversation(script):
    combined = AudioSegment.empty()
    
    for line in script:
        if line["text"].strip():
            system_voice = VOICE_DICT[line["voice_label"]]
            pause_secs = line["pause"]
            
            # Create and append a true silent audio clip if requested
            if pause_secs > 0:
                silence_segment = AudioSegment.silent(duration=int(pause_secs * 1000))
                combined += silence_segment
            
            # Generate raw voice clip from the cloud engine
            voice_bytes = asyncio.run(get_voice_bytes(line["text"], system_voice))
            
            if voice_bytes:
                voice_segment = AudioSegment.from_file(io.BytesIO(voice_bytes), format="mp3")
                combined += voice_segment
                
    output_buffer = io.BytesIO()
    combined.export(output_buffer, format="mp3")
    return output_buffer.getvalue()

# --- Audio Generation ---
if st.button("🔊 Generate Full Conversation Audio", type="primary"):
    if not st.session_state.dialogue_lines or (len(st.session_state.dialogue_lines) == 1 and not st.session_state.dialogue_lines[0]["text"].strip()):
        st.error("Your script is empty! Please write some dialogue lines first.")
    else:
        with st.spinner("Stitching voices together with custom pacing..."):
            try:
                combined_audio = compile_conversation(st.session_state.dialogue_lines)
                
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
