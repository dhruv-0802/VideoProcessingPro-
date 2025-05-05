import streamlit as st
import os
import tempfile
from video_processing import process_video_for_task
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(page_title="Video Task Extractor", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("Video Task Extractor with Gemini AI")
st.markdown("Upload a video to extract task instructions using Google's Gemini AI")

# Check for required API keys
if not os.getenv('GOOGLE_API_KEY'):
    st.error("ERROR: GOOGLE_API_KEY is not set in environment variables. Please set it before continuing.")
elif not os.getenv('OPENAI_API_KEY'):
    st.error("ERROR: OPENAI_API_KEY is not set in environment variables. Please set it before continuing.")
else:
    # File uploader
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
            # Write the uploaded file to the temporary file
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        # Display the uploaded video
        st.video(temp_path)

        if st.button("Extract Tasks"):
            with st.spinner('Processing video with Gemini AI... This may take a few minutes'):
                # Process the video
                try:
                    response_dict = process_video_for_task(temp_path)
                    
                    if response_dict:
                        # Extract steps and create output string
                        steps = []
                        output_str = ""
                        
                        # Process the dictionary items
                        for key, value in response_dict.items():
                            if isinstance(value, dict) and "description" in value:
                                instruction = {}
                                instruction['description'] = value["description"]
                                steps.append(instruction)
                                output_str += f"{value['description']}\n\n"
                        
                        # Display results
                        st.subheader("Extracted Tasks")
                        
                        # Display in a nice card layout with better text visibility
                        for i, step in enumerate(steps, 1):
                            with st.container():
                                st.markdown(f"""
                                <div class="task-card">
                                    <div class="task-title">Step {i}</div>
                                    <div class="task-description">{step['description']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Option to download the output as text
                        st.download_button(
                            label="Download as Text",
                            data=output_str,
                            file_name="extracted_tasks.txt",
                            mime="text/plain"
                        )
                        
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                        except Exception as e:
                            st.warning(f"Could not remove temporary file: {str(e)}")
                            
                    else:
                        st.error("Error processing video. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please upload a video file to begin.")

# Add some information at the bottom of the page
st.markdown("---")
st.caption("Video Task Extractor uses Google's Gemini AI to process videos and extract step-by-step instructions") 
