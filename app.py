from flask import Flask, render_template, request, send_file
import requests
import base64
from io import BytesIO
from keys import HUGGINGFACE_API_KEY
import json
from datetime import datetime

app = Flask(__name__)

def log_entry(message):
    return f"[{datetime.now().strftime('%H:%M:%S')}] {message}"

@app.route('/', methods=['GET', 'POST'])
def index():
    console_log = []
    if request.method == 'POST':
        company_name = request.form['company_name']
        description = request.form['description']
        try:
            console_log.append(log_entry(f"Generating logo for: {company_name}"))
            console_log.append(log_entry(f"Description: {description}"))
            console_log.append(log_entry("Sending request to Hugging Face API..."))
            
            image_data = generate_logo(company_name, description)
            if image_data:
                # Convert binary image data to base64 for display
                image_b64 = base64.b64encode(image_data).decode('utf-8')
                console_log.append(log_entry("Logo generated successfully!"))
                return render_template('index.html', 
                                    image_data=image_b64, 
                                    company_name=company_name,
                                    error=None,
                                    console_log=console_log)
            else:
                console_log.append(log_entry("Failed to generate logo"))
                return render_template('index.html', 
                                    error="Failed to generate logo. Please try again.",
                                    console_log=console_log)
        except Exception as e:
            console_log.append(log_entry(f"Error: {str(e)}"))
            return render_template('index.html', 
                                error=f"An error occurred: {str(e)}",
                                console_log=console_log)
    return render_template('index.html')

def generate_logo(company_name, description):
    api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Format the prompt for SDXL
    prompt = (
        f"a minimalist cartoon logo design for a company named {company_name}. "
        f"{description}. Professional, clean, modern design, suitable for business, "
        "high contrast, vector style, centered composition"
    )
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "negative_prompt": "text, words, letters, signature, watermark, low quality, blurry, pixelated",
            "width": 1024,
            "height": 1024
        }
    }
    
    try:
        print(f"Sending prompt: {prompt}")  # Debug print
        response = requests.post(api_url, headers=headers, json=payload)
        
        # Print detailed response information for debugging
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            return response.content  # Returns binary image data
        elif response.status_code == 503:
            # Model is loading
            error_message = "Model is currently loading. Please try again in a few moments."
            print(error_message)
            raise Exception(error_message)
        else:
            error_message = f"API Error: Status {response.status_code}"
            try:
                error_detail = response.json()
                error_message += f" - {json.dumps(error_detail)}"
            except:
                error_message += f" - {response.text}"
            print(error_message)
            raise Exception(error_message)
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(debug=True) 