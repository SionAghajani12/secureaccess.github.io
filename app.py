from flask import Flask, request, render_template
import requests  # Add this import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

def check_csrf_with_selenium(url):
    # Configure options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    results = []

    try:
        # Load the URL
        driver.get(url)
        # Get the page source after JavaScript has executed
        page_source = driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all forms in the HTML content
        forms = soup.find_all('form')
        if not forms:
            results.append(f"No forms found on {url}")
            return results

        for i, form in enumerate(forms, start=1):
            # Find all input fields within the form
            inputs = form.find_all('input')
            csrf_tokens = []

            for input_tag in inputs:
                # Look for potential CSRF tokens
                if 'csrf' in input_tag.get('name', '').lower():
                    csrf_tokens.append(input_tag)

            # Check if CSRF tokens are found
            if csrf_tokens:
                results.append(f"Form {i} on {url} has the following CSRF tokens:")
                for token in csrf_tokens:
                    results.append(f" - Name: {token['name']}, Type: {token.get('type', 'hidden')}, Value: {token.get('value', 'N/A')}")
            else:
                results.append(f"Form {i} on {url} does not have any CSRF tokens.")
    
    except Exception as e:
        results.append(f"An error occurred while fetching the URL: {e}")
    
    finally:
        driver.quit()

    return results

def check_loosely_scoped_cookies(url):
    try:
        response = requests.get(url)

        if 'Set-Cookie' in response.headers:
            cookies = response.headers['Set-Cookie'].split('; ')

            for cookie in cookies:
                if cookie.startswith('Domain=.') or cookie.startswith('Path=/'):
                    return [f"Loosely scoped cookie found: {cookie}"]
        
        return ["No loosely scoped cookies found."]
    
    except Exception as e:
        return [f"An error occurred: {str(e)}"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('templates/check', methods=['POST'])
def check():
    url = request.form['domain']
    check_type = request.form['check_type']
    
    if check_type == 'csrf':
        results = check_csrf_with_selenium(url)
    elif check_type == 'cookies':
        results = check_loosely_scoped_cookies(url)
    else:
        results = ["Invalid check type."]
    
    return render_template('results.html', results=results, url=url, check_type=check_type)

if __name__ == '__main__':
    app.run(port=5001)
