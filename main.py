import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import time

# Custom SSL Adapter to handle different SSL/TLS versions
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.set_ciphers('HIGH:!DH:!aNULL')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# Function to create a requests session with SSL configuration
def create_session():
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    return session

# Function to fetch the favicon URL
def fetch_favicon(url):
    session = create_session()
    try:
        response = session.get(url)  # Allow SSL verification
    except requests.exceptions.SSLError as e:
        print(f"SSL Error occurred: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error occurred: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all link tags
    link_tags = soup.find_all('link')

    # Filter link tags to find the one with rel attribute containing 'icon'
    icon_link = None
    for tag in link_tags:
        rel = tag.get('rel')
        if rel and 'icon' in [item.lower() for item in rel]:
            icon_link = tag
            break

    if icon_link:
        favicon_url = icon_link.get('href')
        if not favicon_url.startswith('http'):
            # Handle relative URLs
            favicon_url = requests.compat.urljoin(url, favicon_url)
        return favicon_url
    else:
        # Fall back to the default location
        return requests.compat.urljoin(url, '/favicon.ico')

# Function to save the fetched favicon
def save_favicon(favicon_url, output_dir='favicons', file_name='favicon.ico'):
    os.makedirs(output_dir, exist_ok=True)
    session = create_session()
    response = session.get(favicon_url, stream=True)  # Allow SSL verification

    if response.status_code == 200:
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f'Favicon saved to {file_path}')
    else:
        print(f'Failed to download favicon from {favicon_url}')

# Function to process a list of URLs
def process_urls(urls):
    for url in urls:
        favicon_url = fetch_favicon(url)
        time.sleep(2)
        if favicon_url:
            domain_name = url.split('//')[-1].split('/')[0]
            file_name = f"{domain_name}.ico"
            save_favicon(favicon_url, file_name=file_name)
        else:
            print(f"Favicon could not be found for {url}")

# List of colocation and bare metal provider URLs
urls = [
    'https://centersquaredc.com/'
]

# Process each URL to fetch and save favicons
process_urls(urls)