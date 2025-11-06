# Configuration
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('YOUR_TOKEN', '')
RAPID_API_KEY = os.environ.get('YOUR_KEY', '')
URL = "https://pinterest-video-and-image-downloader.p.rapidapi.com/pinterest"

headers = {
	"x-rapidapi-key": RAPID_API_KEY,
	"x-rapidapi-host": "pinterest-video-and-image-downloader.p.rapidapi.com"
}
