from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def get_video_links(channel_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(channel_url)

    video_links = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_attempts = 100  # Increase this if needed

    while scroll_attempts < max_attempts:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Increased wait time

        # Find and add new links
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/@leksidenation:3/']")
        new_links = set(element.get_attribute('href') for element in elements)
        video_links.update(new_links)

        # Check scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0
            last_height = new_height

        print(f"Found {len(video_links)} unique links so far...")

    driver.quit()
    return list(video_links)

def save_links_to_file(links, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for link in links:
            f.write(f"{link}\n")

# Main execution
channel_url = "https://odysee.com/@leksidenation:3"
output_file = "video_links.txt"

video_links = get_video_links(channel_url)
save_links_to_file(video_links, output_file)

print(f"Found {len(video_links)} unique video links. Saved to {output_file}")import streamlit as st
import yt_dlp
import requests
from urllib.parse import urlparse
import io

def get_video_url():
    url = st.text_input("Please enter the Odysee video URL:", "")
    if url and not url.startswith("https://odysee.com/"):
        st.error("Invalid URL. Please enter a valid Odysee video URL.")
        return None
    return url

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'writethumbnail': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with st.spinner("Fetching video information..."):
                info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'Unknown Title')
            video_url = info_dict.get('url')
            thumbnail_url = info_dict.get('thumbnail', None)
            return video_title, video_url, thumbnail_url
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Error fetching video information: {e}")
        return None, None, None

def download_thumbnail(thumbnail_url):
    if not thumbnail_url:
        return None
    try:
        response = requests.get(thumbnail_url, timeout=30)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.RequestException as e:
        st.error(f"Failed to download the thumbnail: {e}")
        return None

def main():
    st.title("Odysee Video Downloader")

    video_url = get_video_url()

    if video_url:
        st.info(f"Attempting to fetch video information from: {video_url}")

        if st.button("Fetch Video"):
            video_title, direct_video_url, thumbnail_url = download_video(video_url)

            if video_title and direct_video_url:
                st.success(f"Video information fetched successfully: {video_title}")

                # Display thumbnail if available
                thumbnail_data = download_thumbnail(thumbnail_url)
                if thumbnail_data:
                    st.image(thumbnail_data, caption="Video Thumbnail")

                # Provide a download button for the video
                st.download_button(
                    label="Download Video",
                    data=requests.get(direct_video_url).content,
                    file_name=f"{video_title}.mp4",
                    mime="video/mp4"
                )
            else:
                st.warning("Failed to fetch video information.")

if __name__ == "__main__":
    main()
