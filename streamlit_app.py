import streamlit as st
import os
import tempfile
import time
from datetime import datetime
from video_processing import process_video_for_task

# Set up page configuration
st.set_page_config(
    page_title="Video Processing App",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verify API Keys
missing_keys = []

# Check Google API key
if not os.environ.get("GOOGLE_API_KEY") and not st.secrets.get("api_keys", {}).get("google"):
    missing_keys.append("GOOGLE_API_KEY")

# If keys are missing, display error message


# Page configuration
#st.set_page_config(page_title="Video Task Extractor", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .task-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
        border-left: 5px solid #1e88e5;
    }
    .task-title {
        color: #1e88e5;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .task-description {
        color: #333333;
        font-size: 1rem;
        line-height: 1.5;
    }
    .api-warning {
        background-color: #ffe0e0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #e53935;
    }
</style>
""", unsafe_allow_html=True)

st.title("Video Task Extractor with Gemini AI")
st.markdown("Upload a video to extract task instructions using Google's Gemini AI")



# File uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Display some file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / (1024*1024):.2f} MB"
    }
    st.write("File Details:")
    for key, value in file_details.items():
        st.write(f"- {key}: {value}")
    
    # Process button
    if st.button("Process Video"):
        # Create progress indicators
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        try:
            # Update status
            status_container.text("Starting video processing...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            # Process the video
            status_container.text("Analyzing video content...")
            progress_bar.progress(30)
            
            # Perform the actual processing
            result = process_video_for_task(temp_path)
            steps = []
            # Process the dictionary items
            for key in result:
                instruction = {}
                instruction['description'] = key["description"]
                steps.append(instruction)
            
            progress_bar.progress(90)
            status_container.text("Finalizing results...")
            time.sleep(0.5)
            
            # Complete
            progress_bar.progress(100)
            status_container.text("Processing complete!")
            
            # Display results in a clear format
            st.markdown("## Extracted Task Steps")
            
            for i, step in enumerate(steps, 1):
                with st.expander(f"Step {i}: {step['description'][:50]}...", expanded=True):
                    st.markdown(f"**{step['description']}**")
            
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

# Add information about the application
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
    This application processes videos of screen recordings to extract detailed step-by-step instructions.
    
    It uses Google's Gemini AI to analyze the video content and generate structured task steps.
    
    **How it works:**
    1. Upload your screen recording video
    2. Click "Process Video"
    3. Review the extracted task steps
    """)
    
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} Video Processing Pro") 
