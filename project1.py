from itertools import count
import lxml
import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import sqlite3

headers = {"User-Agent":
               "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/109.0.0.0 Safari/537.36"}


def parser():
    url = f'https://www.nhl.com/news/'
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")
    sleep(3)
    data = soup.find_all("article", class_="article-item")

    conn = sqlite3.connect('resources and items.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            RESOURCE_ID INTEGER PRIMARY KEY,
            RESOURCE_NAME TEXT,
            RESOURCE_URL TEXT,
            top_tag TEXT,
            bottom_tag TEXT,
            title_cut TEXT,
            date_cut TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO resources (
            RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, ('nhl.com', 'https://www.nhl.com/news/', 'article.article-item', 'h2.article-item__subheader',
          'h1.article-item__headline', 'span.article-item__date[data-date]'))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            res_id INTEGER,
            link TEXT,
            title TEXT,
            content TEXT,
            nd_date TEXT,
            s_date TEXT,
            FOREIGN KEY(res_id) REFERENCES resource(RESOURCE_ID)
        )
    """)

    count = 0
    for d in data:
        try:
            type_of_content = d.find("span", class_="article-item__primary-tag").text
            article1 = d.find("h1", class_="article-item__headline").text
            short_description = d.find("h2", class_="article-item__subheader").text if d.find("h2",
                                                                                              class_="article-item__subheader") else None
            author_html = d.find("span", class_="article-item__contributor")
            author_split = author_html.text.strip().split("by")
            if len(author_split) > 1:
                author = author_split[1].strip().split("/")[0].strip().split("\n")[0].strip()
            else:
                author = "NHL.com"

            date_str = d.find("span", class_="article-item__date")['data-date']
            date_full = date_str.split('T')[0]
            time_str = date_str.split("T")[1][:5]
            card_url = "https://www.nhl.com" + d.find("a", class_="article-item__more").get("href")
            current_time = datetime.now()
            date_and_time = current_time.strftime("%Y-%m-%d %H:%M")

            print(f'Type of Content: {type_of_content}')
            print(f'Article: {article1}')
            print(f'Short Description: {short_description}')
            print(f'Author: {author}')
            print(f'Date of news: {date_full} {time_str}')
            print(f'Card URL: {card_url}')
            print(f'Current date and time: {date_and_time}')
            print('_____')

            cursor.execute("""
                        INSERT INTO items (res_id, link, title, content, nd_date, s_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (1, card_url, article1, short_description, date_full + " " + time_str, date_and_time))

            count += 1
            if count == 5:
                break
        except AttributeError:
            print(AttributeError)
            pass
        except IndexError:
            print(IndexError)
            pass
        except Exception as e:
            print('Error', e)

    conn.commit()
    conn.close()


parser()
