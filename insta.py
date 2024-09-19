import instaloader
import os
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import matplotlib.pyplot as plt
from io import BytesIO
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

# Helper function to randomize delay
def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

# Fetch posts function using Instaloader
def fetch_posts(username, password):
    L = instaloader.Instaloader()
    session_file_path = f"{username}_session"
    try:
        L.load_session_from_file(session_file_path)
    except FileNotFoundError:
        L.login(username, password)
        L.save_session_to_file(session_file_path)

    profile = instaloader.Profile.from_username(L.context, username)
    posts = []
    try:
        for post in profile.get_posts():
            posts.append({
                'Date': str(post.date),
                'Caption': post.caption if post.caption else 'No caption',
                'Likes': post.likes,
                'Comments': post.comments,
                'URL': f"https://www.instagram.com/p/{post.shortcode}/"
            })
            if len(posts) == 10:
                break
            random_delay(1, 3)
    except Exception as e:
        st.write(f"Error fetching posts: {e}")
    
    return pd.DataFrame(posts)

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

def random_delay(min_seconds=2, max_seconds=5):
    import time
    import random
    time.sleep(random.uniform(min_seconds, max_seconds))

def take_screenshot(username, save_path):
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={ua.random}')
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    service = Service("C:/driver/chromedriver.exe")

    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(f'https://www.instagram.com/{username}/')

        # Wait for the profile page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "img"))
        )

        random_delay(2, 4)

        screenshot_path = os.path.join(save_path, f'{username}_profile.png')
        driver.save_screenshot(screenshot_path)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        driver.quit()

    return screenshot_path

# Create an engagement chart using Matplotlib
def create_chart(posts_df):
    posts_df['Date'] = pd.to_datetime(posts_df['Date'])
    plt.figure(figsize=(10, 5))
    plt.plot(posts_df['Date'], posts_df['Likes'], marker='o', label='Likes')
    plt.plot(posts_df['Date'], posts_df['Comments'], marker='s', label='Comments')
    plt.title('Engagement Metrics Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Streamlit application
def main():
    st.title("Instagram Profile Analyzer")

    username = st.text_input("Enter Instagram Username")
    password = st.text_input("Enter Instagram Password", type="password")
    
    if st.button("Fetch Data"):
        if username and password:
            with st.spinner("Fetching posts..."):
                posts_df = fetch_posts(username, password)
                st.write(f"Fetched {len(posts_df)} posts.")
                st.dataframe(posts_df)

            if not posts_df.empty:
                # Plot chart
                st.subheader("Engagement Over Time")
                chart_buf = create_chart(posts_df)
                st.image(chart_buf, use_column_width=True)

                # Take profile screenshot
                save_path = "C:/insta_posts"
                os.makedirs(save_path, exist_ok=True)
                with st.spinner("Taking screenshot..."):
                    profile_screenshot = take_screenshot(username, save_path)
                    st.image(profile_screenshot, caption=f"Profile Screenshot of {username}")
        else:
            st.warning("Please enter both username and password.")

if __name__ == "__main__":
    main()
