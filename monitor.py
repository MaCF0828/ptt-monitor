import requests
from bs4 import BeautifulSoup
import os
import json
import time

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
BOARDS = ['give', 'Lifeismoney', 'Actuary']
STATE_FILE = '/tmp/seen_articles.json'

def get_latest_articles(board):
    url = f'https://www.ptt.cc/bbs/{board}/index.html'
    res = requests.get(url, cookies={'over18': '1'}, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = []
    for div in soup.select('div.r-ent'):
        title_tag = div.select_one('div.title a')
        if title_tag:
            title = title_tag.text.strip()
            link = 'https://www.ptt.cc' + title_tag['href']
            articles.append({'title': title, 'link': link})
    return articles

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'})

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(STATE_FILE, 'w') as f:
        json.dump(seen, f)

print("PTT Monitor 啟動！")
send_telegram("✅ PTT 監控已啟動！\n監控看板：give、Lifeismoney、Actuary")

while True:
    try:
        seen = load_seen()
        for board in BOARDS:
            try:
                articles = get_latest_articles(board)
                for a in articles:
                    if a['link'] not in seen.get(board, []):
                        send_telegram(f"📢 <b>[{board}]</b> 新文章！\n{a['title']}\n{a['link']}")
                        seen.setdefault(board, []).append(a['link'])
            except Exception as e:
                print(f"[{board}] 爬取失敗：{e}")
        save_seen(seen)
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(120)
