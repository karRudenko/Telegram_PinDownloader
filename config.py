# Configuration
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("YOUR_TOKEN")
RAPID_API_KEY = os.getenv("YOUR_KEY")
URL = "https://pinterest-video-and-image-downloader.p.rapidapi.com/pinterest"

headers = {
	"x-rapidapi-key": RAPID_API_KEY,
	"x-rapidapi-host": "pinterest-video-and-image-downloader.p.rapidapi.com"
}
