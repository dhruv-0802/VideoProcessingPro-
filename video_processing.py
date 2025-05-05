import google.generativeai as genai
import os
import time
from moviepy import VideoFileClip
from openai import OpenAI
import json
import tempfile

def process_video_for_task(file_path):
    """
    Process a video file to extract task instructions using Gemini AI and OpenAI.
    
    Args:
        file_path (str): Path to the video file
        
    Returns:
        dict: Dictionary containing structured task steps
    """
    try:
        # Get API keys from environment
        gemini_api_key = os.getenv('GOOGLE_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not gemini_api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")
        if not openai_api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
            
        # Initialize API clients
        client = genai.Client(api_key=gemini_api_key)
        client2 = OpenAI(api_key=openai_api_key)
        
        # Process video file
        print(f"Processing video file: {file_path}")
        video_clip = VideoFileClip(file_path)
        video_clip.close()
        
        # Upload file to Gemini
        print("Uploading video to Gemini...")
        myfile = client.files.upload(file=file_path)
        
        print(f"File uploaded with Name: {myfile.name}")
        print(f"Waiting for file to become active...")
        
        # Wait for file to be processed (max 5 minutes)
        timeout_seconds = 300
        start_time = time.time()
        while myfile.state != "ACTIVE":
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"File {myfile.name} did not become active within {timeout_seconds} seconds.")
            
            print(f"File state: {myfile.state}. Waiting...")
            time.sleep(5)
            myfile = client.files.get(name=myfile.name)
            
        print(f"File {myfile.name} is now ACTIVE. Processing with Gemini...")
        
        # Load the prompt texts from the attached assets
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Read first prompt
        try:
            with open(os.path.join(current_dir, "attached_assets/prompt_op.txt"), "r") as file:
                prompt1_text = file.read()
        except FileNotFoundError:
            # Fallback to look in current directory
            try:
                with open("prompt_op.txt", "r") as file:
                    prompt1_text = file.read()
            except FileNotFoundError:
                prompt1_text = """
                # Ripplica Technical Process Analyst Prompt

                ## You Are

                **Ripplica's Technical Process Analyst.** Your mission is to convert screen recording videos into **precise, generalizable, stepwise workflows**. These workflows allow AI operators to **accurately replicate complex business processes** across different environments.


                ## Consolidated Process Flow

                ### 1. Observe the Video & Audio

                Do the following **while watching the video**:
                * Record every **explicit user action**: `click`, `type`, `drag`, 'scroll', `switch`, `wait`
                * Capture **timestamp** for each action (e.g., `00:01:05`)
                * Note **UI structure**: hierarchy, labels, icons, colors, relative positions
                *When describing UI elements, follow these guidelines:
                - Specify the exact location using relative positioning (e.g., top-right, bottom-left, center).
                - Identify the UI component type (e.g., button, text field, icon, drop-down menu).
                - Include any identifying characteristics (e.g., color, label text, shape, size).
                - In case of of ui_interaction as type: Do not mention the content that is to be typed or the content that is already typed in the UI element(e.g., text fields, search boxes). Ignore the text and just mention the details of the UI element. Even avoid mentioning that some text is pre-filled in the UI element.
                - Example of Ui identification : "The search bar is visible at the top-center of the screenshot.", "The "Directions" button is located near the top-left corner next to the search field, marked with a blue icon featuring an arrow","The 'Submit' button is located at the bottom-right corner of the form."
                * Identify **transitional states**: modals, dropdowns, page loads, success/failure indicators
                * Listen for **verbal logic indicators**: *E.g., "Always assign to Dhruv", "If this shows up..."*
                * Note the logic on why each step was performed for (E.g. - click on this button - this is to filter messages)
                * The tone of description should be direct as if ordering the step not descibing the step

                ## Output Format

                For each discrete step, document:

                '''
                json
                {
                  "description": "Brief action performed by the user",
                  "timestamp": "MM:SS",
                  "details": {
                    "action": "Specific interaction (only these actions otherwise none: 'Click', 'Type', 'scroll', 'wait', ('send_key' for eg. press 'enter', 'esc') , 'switch_tab'),'Navigate'.",
                    "ui_element": "Description of the UI component (e.g., 'blue button labeled Filter').",
                    "logic": "Reason for the step (e.g., 'Filter messages to show only unread emails from [Supervisor]')."
                  }
                }
                '''

                ### 2. Write Task Summary (One Paragraph)

                After completing the step breakdown, summarize the task:
                * Describe the **main goal** of the workflow
                * Mention **key actors, entities, and data** involved
                * Clarify the **end result** expected

                **Example**: "This task creates a calendar meeting after reviewing unread emails from Dhruv Bhardwaj. The analyst identifies unread messages, derives meeting context, and schedules an event with Dhruv as a participant."
                """
        
        # Read second prompt
        try:
            with open(os.path.join(current_dir, "attached_assets/prompt2.txt"), "r") as file:
                prompt2_text = file.read()
        except FileNotFoundError:
            # Fallback to look in current directory
            try:
                with open("prompt2.txt", "r") as file:
                    prompt2_text = file.read()
            except FileNotFoundError:
                prompt2_text = """
                # Prompt: Generalize a Specific Workflow with Intelligent Placeholders (Human + Runtime Context)

                ## Task
                -You are given a detailed, step-by-step workflow describing how a user completes a task through a web interface or digital tool.
                -Your goal is to **generalize** the workflow while preserving its structure, sequence, and clarity -- but replacing any overly specific details with meaningful, reusable placeholders.

                ##  Generalization Rules

                1. **Preserve the original structure and step-by-step format**:
                   - Include `Step Title`, `Action`, `UI Hint`, `Inputs`, `Tips` or `Decision Points` where available

                2. **Only replace values with user placeholders** if they must be provided externally:
                   - e.g., company names, school names, campaign list names, filter terms, custom labels, filter names , person names 

                3. **Preserve runtime-resolved information** using descriptive memory-aware placeholders:
                   - Use: `[name of the person you identified earlier]`
                   - Use: `[product found in previous step]`
                   - Use: `[result selected from earlier search]`

                4. **Do NOT remove contextual UI hints or clues**  
                   -These are critical for human or agent operators and should remain intact (e.g., "top-left search bar", "Add button in modal").

                5. **Do NOT remove the platform names or the application names the user is using**
                   - These things are necessary , Like if the task involves use of Linkedin , we will preserve Linkedin , please determine from reading the task summary what the platform is.
                """
        
        # Read third prompt
        try:
            with open(os.path.join(current_dir, "attached_assets/prompt3.txt"), "r") as file:
                prompt3_text = file.read()
        except FileNotFoundError:
            # Fallback to look in current directory
            try:
                with open("prompt3.txt", "r") as file:
                    prompt3_text = file.read()
            except FileNotFoundError:
                prompt3_text = """
                # Prompt: Condense Step-by-Step JSON into Single-Line Descriptions

                ## Input Requirements
                - A JSON object where each step contains:
                  ```json
                  {
                    "description": "text",
                    "timestamp": "HH:MM",
                    "details": {
                      "action": "click|type|scroll|etc.",
                      "ui_element": "location_description",
                      "logic": "purpose_or_outcome"
                    }
                  }
                  ```

                ## Output Rules
                1. **Format**:
                   ```json
                   {
                     "Step X": {
                       "description": "Step X: [Merged sentence from all fields, and make this a meaningful well constructed direction for agent to follow]"
                     }
                   }
                   ```
                2. **Content Merge Guidelines**:
                   - Combine `action`, `ui_element`, and `logic` into **one natural sentence**.
                   - Preserve:
                     - **Actions** (e.g., `click`, `type`)
                     - **UI Locations** (e.g., "below the post")
                     - **UI Locations** ( Make sure the *complete* details of the UI locations is to be used, whatever is given in the input)
                     - **Purpose** (from `logic` field)
                """
        
        # Use Gemini to analyze the video
        model_name = "gemini-2.5-pro-preview-03-25"
        
        # First API call to Gemini
        print("Making first API call to Gemini...")
        first_call_contents = [myfile, prompt1_text]
        response1 = client.models.generate_content(
            model=model_name,
            contents=first_call_contents,
            config={"temperature": 0}
        )
        
        if not response1 or not hasattr(response1, 'text'):
            raise ValueError("First API call failed to return valid text response")
            
        first_response_text = response1.text
        print("First API call completed successfully")
        
        # Second API call to Gemini
        print("Making second API call to Gemini...")
        second_call_contents = [first_response_text, prompt2_text]
        response2 = client.models.generate_content(
            model=model_name,
            contents=second_call_contents,
            config={"temperature": 0}
        )
        
        if not response2 or not hasattr(response2, 'text'):
            raise ValueError("Second API call failed to return valid text response")
            
        second_response_text = response2.text
        print("Second API call completed successfully")
        
        # Third API call to OpenAI
        print("Making API call to OpenAI...")
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # Do not change this unless explicitly requested by the user
        response3 = client2.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt3_text},
                {"role": "user", "content": second_response_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        openai_response_text = response3.choices[0].message.content
        print("OpenAI API call completed successfully")
        
        # Parse the response into a dictionary
        response_dict = json.loads(openai_response_text)
        
        # Clean up by deleting the uploaded file
        try:
            client.files.delete(name=myfile.name)
            print(f"Deleted uploaded file: {myfile.name}")
        except Exception as e:
            print(f"Warning: Failed to delete uploaded file: {e}")
        
        return response_dict
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        raise e
