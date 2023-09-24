import re
from collections import Counter

import requests
from bs4 import BeautifulSoup


def get_site(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        raise Exception('Response status is not 200')


def get_site_index(url="https://blog.hubspot.com/"):
    try:
        return get_site(url)
    except requests.exceptions.RequestException as e:
        exit(f"An error occurred while trying to access the website: {e}")


def get_site_article(url):
    try:
        return get_site(url)
    except requests.exceptions.RequestException as e:
        return None


def get_articles_title_and_url(soup, limit=3):
    articles = []
    post_h3_titles = soup.find_all('h3', class_='blog-post-card-title')[0:limit]
    for post_h3_title in post_h3_titles:
        if post_h3_title:
            if a_element := post_h3_title.find('a'):
                title = a_element.text
                url = a_element.get('href')
                articles.append((title, url))
    return articles


def get_article_text(article_soup, tags=['p', 'li']):
    text_all = ""
    for tag in tags:
        e = article_soup.find_all(tag)
        for x in e:
            if x.get('class'):
                continue
            if len(x.findChildren()) > 0:
                if x.find('span', style='font-weight: bold;'):
                    pass
                else:
                    continue
            text_all += " " + x.text
    return text_all


def clean_article_text(article_text_raw):
    text_with_only_characters = re.sub(r'[^a-zA-Z\s]', '', article_text_raw)
    text_without_many_spaces = re.sub(r'\s+', ' ', text_with_only_characters)
    text_clean = text_without_many_spaces.lower().split(' ')
    return text_clean


def count_words(article_text_clean):
    return len(article_text_clean)


def count_letters(article_text_clean):
    letter_count = 0
    for x in article_text_clean:
        letter_count += len(x)
    return letter_count


def split_by(words, size=2):
    result = []
    for i in range(len(words) - size + 1):
        a = ""
        for j in range(size):
            a += words[i + j]
            if j + 1 < size:
                a += " "
        result.append(a)
    return result


def create_word_bags(words, size=2):
    result = []
    for word, _ in words:
        word = word.split()
        for k in range(len(word)):
            result.append(' '.join(word[k:k + size]))
    return result


def get_phrases_top(words_1, top_word_count=5):
    words_2 = split_by(words_1, 2)
    words_3 = split_by(words_1, 3)

    top_1 = Counter(words_1).most_common(top_word_count)
    top_2 = Counter(words_2).most_common(top_word_count)
    top_3 = Counter(words_3).most_common(top_word_count)

    word_bag_2 = create_word_bags(top_2, 1)
    word_bag_3 = create_word_bags(top_3, 2)

    result = [] + top_3
    for word_1, count in top_1:
        if word_1 in word_bag_2:
            pass
        elif word_1 in word_bag_3:
            pass
        else:
            result.append((word_1, count))

    for word_2, count in top_2:
        if word_2 not in word_bag_3:
            result.append((word_2, count))

    result_sorted = sorted(result, key=lambda x: x[1], reverse=True)[:top_word_count]
    return result_sorted


if __name__ == "__main__":
    index_soup = get_site_index()
    articles_title_url = get_articles_title_and_url(index_soup, limit=3)

    error_count = 0
    for i, (title, url) in enumerate(articles_title_url, start=1):
        if article_soup := get_site_article(url):
            article_text_raw = get_article_text(article_soup)
            article_text_clean = clean_article_text(article_text_raw)
            word_count = count_words(article_text_clean)
            letter_count = count_letters(article_text_clean)
            phrases_top_5 = get_phrases_top(article_text_clean)
            print(f"{i}. Title: {title}")
            print(f"Word count: {word_count},  Letter count: {letter_count}")
            print("Top phrases: ", phrases_top_5, end='\n\n')
        else:
            error_count += 1
        print(f"Finished with {error_count} errors.")
