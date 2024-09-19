import instaloader
import os
import random
import time
import pandas as pd
import requests
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

# Download an image from a URL
def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Failed to download image, status code: {response.status_code}")

# Fetch profile and posts function using Instaloader
def fetch_profile_data(username, password):
    L = instaloader.Instaloader()
    session_file_path = f"{username}_session"
    try:
        L.load_session_from_file(session_file_path)
    except FileNotFoundError:
        L.login(username, password)
        L.save_session_to_file(session_file_path)

    profile = instaloader.Profile.from_username(L.context, username)
    
    # Collecting profile data
    profile_data = {
        'Username': profile.username,
        'Full Name': profile.full_name,
        'Bio': profile.biography,
        'Followers': profile.followers,
        'Following': profile.followees,
        'Profile Picture URL': profile.profile_pic_url
    }

    # Fetching posts
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

    return profile_data, pd.DataFrame(posts)

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
            with st.spinner("Fetching profile and posts..."):
                profile_data, posts_df = fetch_profile_data(username, password)
                st.write(f"Fetched {len(posts_df)} posts.")
                
                # Download and display profile picture
                profile_pic_path = f"{username}_profile_pic.png"
                try:
                    download_image(profile_data['Profile Picture URL'], profile_pic_path)
                    st.image(profile_pic_path, caption=f"Profile Picture of {profile_data['Username']}", width=150)
                except Exception as e:
                    st.write(f"Error downloading profile picture: {e}")

                # Display profile information
                st.subheader("Profile Information")
                st.write(f"**Username:** {profile_data['Username']}")
                st.write(f"**Full Name:** {profile_data['Full Name']}")
                st.write(f"**Bio:** {profile_data['Bio']}")
                st.write(f"**Followers:** {profile_data['Followers']}")
                st.write(f"**Following:** {profile_data['Following']}")

                # Add heading before posts table
                st.subheader("Posts:")

                # Display posts dataframe
                st.dataframe(posts_df)

                if not posts_df.empty:
                    # Plot chart
                    st.subheader("Engagement Over Time")
                    chart_buf = create_chart(posts_df)
                    st.image(chart_buf, use_column_width=True)
        else:
            st.warning("Please enter both username and password.")

if __name__ == "__main__":
    main()
