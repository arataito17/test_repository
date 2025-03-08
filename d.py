import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Chromeのオプション設定（ヘッドレスモード）
chrome_options = Options()
chrome_options.add_argument("--headless")  # ヘッドレスモード

# WebDriverのパスを指定
driver_path = "/usr/local/bin/chromedriver"
url = "https://programs.sigchi.org/shared-list?sharedId=nJCUSGQB"  # 実際のURLに置き換えてください

# WebDriverサービスを設定
service = Service(driver_path)

# Seleniumのブラウザを起動
driver = webdriver.Chrome(service=service, options=chrome_options)

# ウェブページにアクセス
driver.get(url)

# JavaScriptが完全に読み込まれるのを待つ
try:
    wait = WebDriverWait(driver, 120)  # 最大120秒間待機
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Jonathan Lazar')]"))) # 実際のIDに置き換えてください

    # ページのテキストを取得
    page_content = driver.page_source

    # 必要な部分を抽出
    soup = BeautifulSoup(page_content, 'html.parser')

    # テキストを抽出
    text_content = soup.get_text()

    # テキストをファイルに保存
    with open("web_content.txt", "w", encoding="utf-8") as file:
        file.write(text_content)

    print("ウェブサイトの内容がコピーされました。")
except TimeoutException:
    print("ページの読み込みに時間がかかりすぎてタイムアウトしました。")

# WebDriverを閉じる
driver.quit()

# 空白行を削除する処理
input_file = "web_content.txt"  # 元のファイル名
output_file = "output.txt"  # 空白行を削除したファイル名

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        if line.strip():  # 空白や改行のみの行をスキップ
            outfile.write(line)

print(f"空白行を削除した結果が{output_file}に保存されました。")

# arXivで検索する関数
def search_arxiv(title_list, output_file):
    base_url = "https://arxiv.org/search/?query={}&searchtype=title&abstracts=show&order=-announced_date_first&size=50"

    with open(output_file, 'w', encoding='utf-8') as f:
        for title in title_list:
            # タイトルをURLエンコードして検索URLを作成
            query = title.replace(" ", "+")
            search_url = base_url.format(query)

            # arXivで検索
            response = requests.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 論文情報を取得
            papers = soup.find_all('li', class_='arxiv-result')
            f.write(f"Results for: {title}\n")
            if papers:
                for paper in papers:
                    # 論文のタイトルとリンク
                    paper_title = paper.find('p', class_='title').text.strip()
                    paper_link = paper.find('a')['href']
                    f.write(f"Title: {paper_title}\n")
                    f.write(f"Link: {paper_link}\n")  # ここでは"https://arxiv.org"を付けません
                f.write("-" * 40 + "\n")
            else:
                f.write(f"No results found for: {title}\n")
                f.write("-" * 40 + "\n")

# output.txt からタイトルリストを取得する部分
titles = []
with open("output.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1, len(lines)):  # 1行目はスキップ
    if lines[i].strip().lower() == "papers":  # "papers" を小文字比較
        # 空でない直前の行を探す
        j = i - 1
        while j >= 0 and lines[j].strip() == "":
            j -= 1
        if j >= 0:  # 見つかった場合のみ追加
            titles.append(lines[j].strip())  # タイトルをリストに追加

# 結果をファイルに書き出す
output_file = "output_results.txt"
search_arxiv(titles, output_file)
print(f"Results have been written to {output_file}")
