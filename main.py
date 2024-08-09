import streamlit as st
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

def fetch_video_info(url):
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
            description = info_dict.get('description', 'No description available.')
            return video_title, video_url, thumbnail_url, description
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Error fetching video information: {e}")
        return None, None, None, None

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
            video_title, direct_video_url, thumbnail_url, description = fetch_video_info(video_url)

            if video_title and direct_video_url:
                st.success(f"Video information fetched successfully: {video_title}")

                # Display thumbnail if available
                thumbnail_data = download_thumbnail(thumbnail_url)
                if thumbnail_data:
                    st.image(thumbnail_data, caption="Video Thumbnail")

                # Display description
                st.subheader("Video Description")
                st.text_area("", description, height=200, disabled=True)

                # Provide download button for the video
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
