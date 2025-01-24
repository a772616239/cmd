import requests
from bs4 import BeautifulSoup
import json
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 目标URL
url = "https://www.dytt8.net/index.htm"

# 设置请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# 发送请求
response = requests.get(url, headers=headers)
if response.status_code != 200:
    logging.error(f"Failed to retrieve the page. Status code: {response.status_code}")
    exit()

# 解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 提取电影信息
movies = []
for movie in soup.select('.movie-list li')[:10]:  # 假设电影排行榜的前十部电影在 .movie-list li 中
    title = movie.select_one('.title').text
    rating = movie.select_one('.rating').text
    genre = movie.select_one('.genre').text
    release_date = movie.select_one('.release-date').text
    description = movie.select_one('.description').text
    download_link = movie.select_one('.download-link')['href'] if movie.select_one('.download-link') else None

    movies.append({
        "title": title,
        "rating": rating,
        "genre": genre,
        "release_date": release_date,
        "description": description,
        "download_link": download_link
    })

    # 设置请求间隔
    time.sleep(2)

# 存储为JSON文件
with open('movies.json', 'w', encoding='utf-8') as f:
    json.dump(movies, f, ensure_ascii=False, indent=4)

logging.info("Data has been successfully saved to movies.json")