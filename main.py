# main.py
import feedparser
import json
import os
import time
import openai
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Konfigurasi
RSS_FEED_URL = "https://rss.detik.com/index.php/inet"  # Ganti sesuai kebutuhan
BLOG_ID = "ganti_dengan_id_blog_kamu"
openai.api_key = "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"
POSTED_PATH = "posted.json"

# Fungsi autentikasi ke Blogger API
def get_blogger_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=["https://www.googleapis.com/auth/blogger"]
    )
    creds = flow.run_local_server(port=0)
    return build("blogger", "v3", credentials=creds)

# Ambil artikel dari RSS
def get_articles():
    feed = feedparser.parse(RSS_FEED_URL)
    return feed.entries

# Rewrite artikel pakai GPT
def rewrite_with_gpt(title, content):
    prompt = f"Rewrite this news article in a professional tone.\nTitle: {title}\nContent: {content}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Cek dan simpan artikel yang sudah dipost

def is_posted(link):
    if not os.path.exists(POSTED_PATH):
        return False
    with open(POSTED_PATH, "r") as f:
        posted = json.load(f)
    return link in posted

def save_posted(link):
    if not os.path.exists(POSTED_PATH):
        posted = []
    else:
        with open(POSTED_PATH, "r") as f:
            posted = json.load(f)
    posted.append(link)
    with open(POSTED_PATH, "w") as f:
        json.dump(posted, f)

# Posting ke Blogger
def post_to_blogger(service, title, content):
    body = {
        "title": title,
        "content": content
    }
    post = service.posts().insert(blogId=BLOG_ID, body=body).execute()
    return post.get("url")

# Main
if __name__ == "__main__":
    service = get_blogger_service()
    articles = get_articles()

    for entry in articles:
        if is_posted(entry.link):
            continue
        rewritten = rewrite_with_gpt(entry.title, entry.summary)
        url = post_to_blogger(service, entry.title, rewritten)
        print(f"Posted: {url}")
        save_posted(entry.link)
        time.sleep(60)  # delay antar post agar tidak terlalu cepat
