# Video Processing Pro

A Streamlit application that processes screen recording videos to extract detailed step-by-step instructions using Google's Gemini AI.

## Features

- Upload video files (mp4, mov, avi) of screen recordings
- Process videos to extract task steps and instructions
- Generate structured, easy-to-follow guides from video content
- Secure handling of API keys

## Requirements

- Python 3.8+
- Google Gemini API key
- Streamlit account (for deployment)

## Local Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/VideoProcessingPro.git
   cd VideoProcessingPro
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   # Google Gemini API Key
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. Run the application locally:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deployment on Streamlit Cloud

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Create a new app by connecting to your GitHub repository

4. In the app settings, add your API keys as secrets:
   ```toml
   [api_keys]
   google = "your_google_api_key_here"
   ```

5. Deploy your app

## Secure API Key Handling

This application uses two methods to securely handle API keys:

1. **Local Development**: Uses `.env` file with `python-dotenv` (not committed to Git)
2. **Streamlit Deployment**: Uses Streamlit's secrets management

The application code checks for keys in this order:
1. Environment variables
2. Streamlit secrets

## Usage

1. Upload a video recording file
2. Click "Process Video"
3. Review the extracted task steps

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 