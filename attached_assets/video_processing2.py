from google import genai
import os
import time
from moviepy import VideoFileClip  # Import for audio extraction
import os
import json
import uuid
import time
import shutil

from pydantic import BaseModel, Field

class Steps(BaseModel):
  description: str = Field(description="Step number: followed by detailed description dont include timestamps, ensure ui hint as per instructions")


# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remove global client initialization
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

def create_tutorial_html(tutorial_steps, output_filename="tutorial.html"):
    """Create an HTML page with tutorial steps and screenshots"""
    try:
        # Parse tutorial steps if it's a string
        if isinstance(tutorial_steps, str):
            tutorial_steps = tutorial_steps.replace('```json\n', '').replace('\n```', '')
            steps = json.loads(tutorial_steps)
        else:
            steps = tutorial_steps
            
        # HTML template with CSS styling
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tutorial Steps</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    color: #333;
                    text-align: center;
                    padding: 20px 0;
                }
                .step {
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .step-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                }
                .step-number {
                    font-size: 1.2em;
                    font-weight: bold;
                    color: #2196F3;
                }
                .timestamp {
                    color: #666;
                    font-size: 0.9em;
                }
                .description {
                    margin: 15px 0;
                    line-height: 1.5;
                }
                .screenshot {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    margin: 10px 0;
                }
                .ui-interaction {
                    background: #f8f9fa;
                    padding: 10px;
                    border-left: 3px solid #2196F3;
                    margin: 10px 0;
                    font-style: italic;
                    color: #555;
                }
                .ui-location {
                    background: #e3f2fd;
                    padding: 10px;
                    border-left: 3px solid #1565c0;
                    margin: 10px 0;
                    font-weight: bold;
                    color: #1565c0;
                }
            </style>
        </head>
        <body>
            <h1>Tutorial Steps</h1>
        """
        
        # Add each step to the HTML
        for i, step in enumerate(steps, 1):
            html_content += f"""
            <div class="step">
                <div class="step-header">
                    <span class="step-number">Step {i}</span>
            """
            
            # Only add timestamp if it exists
            if 'timestamp' in step:
                html_content += f"""
                    <span class="timestamp">Timestamp: {step['timestamp']:.2f}s</span>
                """
            
            html_content += """
                </div>
                <div class="description">{}</div>
            """.format(step.get('description', ''))
            
            # Only add screenshot if there's both timestamp and UI interaction
            if 'timestamp' in step and 'ui_interaction' in step:
                screenshot_timestamp = step['timestamp'] + 0.5  # Add 0.5s to match capture time
                screenshot_path = f'screenshots/step_{i}_{screenshot_timestamp:.2f}s.png'
                
                if os.path.exists(screenshot_path):
                    # Use screenshots directory directly instead of copying to tutorial_assets
                    html_content += f"""
                    <img class="screenshot" src="{screenshot_path}" alt="Step {i} Screenshot">
                    """
            
            # Only add UI interaction if it exists
            if 'ui_interaction' in step:
                html_content += f"""
                <div class="ui-interaction">UI Action: {step['ui_interaction']}</div>
                """
            
            # Add UI location before closing the step div
            if 'ui_location' in step and step['ui_location']['found']:
                html_content += f"""
                <div class="ui-location">{step['ui_location']['description']}</div>
                """
            
            html_content += "</div>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Write the HTML file
        with open(output_filename, "w") as f:
            f.write(html_content)
            
        print(f"Tutorial HTML created: {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error creating HTML: {str(e)}")
        return False
    
def get_output(file_path):
    myfile = None # Initialize myfile to None
    try:
        # Ensure the moviepy library is installed: pip install moviepy
        video_clip = VideoFileClip(file_path)
        # video_clip.write_videofile(file_path, codec='libx264', audio_codec='aac') # Commented out as it seems unnecessary for upload
        video_clip.close()
        print(f"Attempting to upload video file: {file_path}")

        # Ensure 'client' is an initialized Google Gemini client object that supports file upload and generate_content with config
        # If using the google-generativeai library, 'client' should be an instance of google.generativeai.Client
        if 'client' not in globals() and not isinstance(client, object):
             print("Error: 'client' object is not initialized or not a valid type.")
             return None # Exit if client is not properly set up

        # For google-generativeai client, file upload is typically done via client.files
        # If using GenerativeModel directly, file handling might be different or not directly supported for upload
        # Assuming 'client' is an instance from google.generativeai.Client
        myfile = client.files.upload(file=file_path)

        print(f"File uploaded with Name: {myfile.name}")
        print(f"Polling file state for {myfile.name}...")
        timeout_seconds = 300 # Wait up to 5 minutes
        start_time = time.time()
        while myfile.state != "ACTIVE":
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"File {myfile.name} did not become active within {timeout_seconds} seconds.")

            print(f"File state: {myfile.state}. Waiting...")
            time.sleep(5)
            myfile = client.files.get(name=myfile.name) # Refresh the file object to get the latest state

        print(f"File {myfile.name} is now ACTIVE. Proceeding with content generation (First Call).")
        prompt1_text = ""
        try:
            with open(os.path.join(script_dir, "prompt_op.txt"), "r") as file:
                prompt1_text = file.read()
                print(f"Read prompt from prompt_op.txt (first call).")
        except FileNotFoundError:
            print("Error: prompt_op.txt not found.")
            # Depending on your application, you might want to handle this differently
            # For now, let's exit as the prompt is crucial
            return None # Or raise an exception

        model_name = "gemini-2.5-pro-preview-03-25" # Use the model name you are using
        # For the first call, we pass the uploaded file object and the text prompt
        first_call_contents = [myfile, prompt1_text]
        print(f"Generating content with {model_name} (First Call)...")
        response1 = client.models.generate_content(
            model=model_name,
            contents=first_call_contents,
            config={"temperature": 0}
        )
        print("\n--- Response (First Call) ---")
        # Add check for valid response1 before accessing .text
        if response1 and hasattr(response1, 'text'):
            first_response_text = response1.text
            print(first_response_text)
        else:
            print("Error: First API call did not return a valid text response.")
            print(f"Response object: {response1}") # Print the response object for debugging
            # Handle the case where the first call fails to get text
            return None # Or raise an exception
        print("--- End Response (First Call) ---")

        print(f"\n--- Starting Second API Call ---")
        print(f"Using output from first call as input for the second.")

        prompt2_text = ""
        try:
            with open(os.path.join(script_dir, "prompt2.txt"), "r") as file:
                prompt2_text = file.read()
                print(f"Read prompt from prompt2.txt (second call).")
        except FileNotFoundError:
            print("Error: prompt2.txt not found.")
            # Handle missing prompt2.txt appropriately
            return None # Or raise an exception

        # Prepare the contents for the second call
        # We combine the content of prompt2.txt and the text output from the first call
        # Putting prompt2_text first often works well to give instructions
        second_call_contents = [first_response_text, prompt2_text]

        print(f"Generating content with {model_name} (Second Call)...")
        response2 = client.models.generate_content(
            model=model_name,
            contents=second_call_contents,
            config={"temperature": 0}
        )

        print("\n--- Response (Second Call) ---")
        # Add check for valid response2 before accessing .text
        if response2 and hasattr(response2, 'text'):
            second_response_text = response2.text
            print(second_response_text)
        else:
            print("Error: Second API call did not return a valid text response.")
            print(f"Response object: {response2}") # Print the response object for debugging
            # Handle the case where the second call fails to get text
            return None # Or raise an exception
        print("--- End Response (Second Call) ---")

        print(f"\n--- Starting Third API Call with Gemini (Prompt 3 + Output of Call 2) ---")
        print(f"Using Prompt 3 and output from second call as input.")

        # Read the content of prompt3.txt (Prompt 3)
        prompt3_text = ""
        try:
            with open(os.path.join(script_dir, "prompt3.txt"), "r") as file:
                prompt3_text = file.read()
                print(f"Read prompt from prompt3.txt (third call).")
        except FileNotFoundError:
            print("Error: prompt3.txt not found.")
            exit()
            # Handle missing prompt3.txt appropriately
            #return None # Or raise an exception
        third_call_contents = [second_response_text, prompt3_text]

        print(f"Sending request to Gemini API for structured JSON output...")
        
        try:
            print(f"Generating content with {model_name} (Third Call)...")
            response3 = client.models.generate_content(
                model=model_name,
                contents=third_call_contents,
                config={
                    'temperature':0.7,
                    'response_mime_type':"application/json",
                    'response_schema':list[Steps] 
                }
            )
            
            # Extract the response text
            print("\n--- Response (Third Call) ---")
            print(response3.text) # Print the final output
            print("--- End Response (Third Call) ---")
            
            # Save the response to a file
            output_file_path = os.path.join(script_dir, "gemini_response.json")
            with open(output_file_path, "w") as output_file:
                output_file.write(response3.text)
            
            # Parse the JSON string into a Python object
            try:
                # Try to parse as JSON
                response_list = json.loads(response3.text)
                print(f"Successfully parsed JSON response, type: {type(response_list)}")
            except json.JSONDecodeError as e:
                # If JSON parsing fails, just use the text as a single item
                print(f"Failed to parse JSON response: {e}")
                # Create a simple list with a single item
                response_list = [{"description": "Failed to parse JSON. Raw text: " + response3.text[:100] + "..."}]
            
            # Clean up by deleting the uploaded file from Google Cloud
            if myfile: # Only attempt to delete if myfile was successfully uploaded
                try:
                    client.files.delete(name=myfile.name)
                    print(f"Deleted uploaded file from Google Cloud: {myfile.name}")
                except Exception as e:
                    print(f"Error deleting Google Cloud file: {e}")

            # --- Add local file deletion here ---
            try:
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
            except OSError as e:
                print(f"Error deleting local file {file_path}: {e}")
            # --- End local file deletion ---
            
            return response_list
            
        except Exception as e:
            print(f"Error during third API call: {e}")
            # Clean up by deleting the uploaded file from Google Cloud
            if myfile: # Only attempt to delete if myfile was successfully uploaded
                try:
                    client.files.delete(name=myfile.name)
                    print(f"Deleted uploaded file from Google Cloud: {myfile.name}")
                except Exception as cleanup_e:
                    print(f"Error deleting Google Cloud file: {cleanup_e}")

            # --- Add local file deletion here ---
            try:
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
            except OSError as cleanup_e:
                print(f"Error deleting local file {file_path}: {cleanup_e}")
            # --- End local file deletion ---
            
            return None # Return None if an exception occurs

    except Exception as e:
        # This catches exceptions from file operations, API call exceptions not caught above, etc.
        print(f"An error occurred in get_output: {e}")
        # Ensure file cleanup is attempted even if initial processing fails
        if myfile:
            try:
                client.files.delete(name=myfile.name)
                print(f"Attempted Google Cloud file cleanup after error: {myfile.name}")
            except Exception as cleanup_e:
                print(f"Error during Google Cloud file cleanup: {cleanup_e}")
        try:
            os.remove(file_path)
            print(f"Attempted local file cleanup after error: {file_path}")
        except OSError as cleanup_e:
            print(f"Error during local file cleanup: {cleanup_e}")
        return None

def process_video_for_task(video_path, gemini_api_key=None):
    # Use environment variables as fallback if no keys are provided
    gemini_api_key = gemini_api_key or os.getenv('GOOGLE_API_KEY')
    
    # Check if API keys are available
    if not gemini_api_key:
        raise ValueError("Google Gemini API key is required")
    
    # Generate a unique directory name for this task
    unique_dir_name = str(uuid.uuid4())
    base_dir = os.getcwd()
    # Define paths relative to base_dir
    video_temp_dir = os.path.join(base_dir, 'video_temp', unique_dir_name)
    screenshots_dir = os.path.join(video_temp_dir, 'screenshots')
    transcription_path = os.path.join(video_temp_dir, 'transcription.json')
    tutorial_steps_path = os.path.join(video_temp_dir, 'tutorial_steps.json')
    tutorial_html_path = os.path.join(video_temp_dir, 'tutorial.html')
    if os.path.exists(video_temp_dir):
        shutil.rmtree(video_temp_dir)
    # Recreate the video_temp directory and necessary subdirectories
    os.makedirs(video_temp_dir, exist_ok=True)
    # Ensure directories exist
    os.makedirs(screenshots_dir, exist_ok=True)

    # Delete existing files and directories if necessary
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.makedirs(screenshots_dir)

    if os.path.exists(tutorial_html_path):
        os.remove(tutorial_html_path)
    
    # Messages for tutorial step extraction
    
    video_file = video_path
    response_dict = get_output(video_file)
    return response_dict
    # The following code is commented out as it's being replaced by get_output
    
   
    
   # return response_dict

# Notes for future development
"""Humein tasks karke ek object hai, usme steps karke ek list banani hai aur usmein sab yeh add kardena hai foda bhai"""
"""The main challenge would be to get the last file complete in json, with the fomat, (description: baaki sab) then we can do the rest"""

if __name__ == "__main__":
    video_path = "/Users/dhruv/Desktop/workify_fresh/workify/server/12_devrev.mov"
    response_dict = process_video_for_task(video_path)
    steps = []
        # Process the dictionary items
    for key, value in response_dict.items():
        if isinstance(value, dict) and "description" in value:
            instruction = {}
            instruction['description'] = value["description"]
            steps.append(instruction)
    print(steps)