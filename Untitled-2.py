import requests
from bs4 import BeautifulSoup
import json
import csv

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_movie_data():
    url = 'http://www.dytt8.net/html/gndy/dyzz/index.html'
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'  # 手动设置编码
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    movies = []
    
    for item in soup.select('.co_content8 ul table'):
        title = item.select_one('.ulink').text.strip()
        year = title.split('(')[-1].split(')')[0] if '(' in title else 'N/A'
        download_link = item.select_one('.download a')['href'] if item.select_one('.download a') else 'N/A'
        
        movie = {
            'title': title,
            'year': year,
            'download_link': download_link
        }
        movies.append(movie)
    
    return movies[:10]  # 只取前十部电影

def save_to_json(data, filename='movies.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_csv(data, filename='movies.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def main():
    movies = fetch_movie_data()
    if movies:
        save_to_json(movies)
        save_to_csv(movies)
        print("数据保存成功！")
    else:
        print("未找到数据。")

if __name__ == "__main__":
    main()