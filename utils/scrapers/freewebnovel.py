import requests
from bs4 import BeautifulSoup

def scrape_series_info(url):
    """
    Scrapes the series info from freewebnovel.com
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title from h1 tag
    title_element = soup.find('h1', class_='tit')
    title = title_element.text.strip() if title_element else None

    # Extract description from the div with class 'txt' inside m-desc
    description = None
    m_desc = soup.find('div', class_='m-desc')
    if m_desc:
        txt_div = m_desc.find('div', class_='txt')
        if txt_div:
            inner_div = txt_div.find('div', class_='inner')
            if inner_div:
                paragraphs = inner_div.find_all('p')
                description = '\n'.join(p.get_text().strip() for p in paragraphs)

    # Extract author from meta tag
    author = None
    author_meta = soup.find('meta', property='og:novel:author')
    if author_meta:
        author = author_meta['content']

    # Extract genre from meta tag
    genre = None
    genre_meta = soup.find('meta', property='og:novel:genre')
    if genre_meta:
        genre = genre_meta['content']

    cover_image = soup.find('meta', property='og:image')
    cover_image = cover_image['content'] if cover_image else None

    if not all([title, description]):
        missing_fields = []
        if not title: missing_fields.append('title')
        if not description: missing_fields.append('description')
        raise ValueError(f"Could not find required fields: {', '.join(missing_fields)}")

    return {
        'title': title,
        'description': description,
        'author': author,
        'cover_image': cover_image,
        'genre': genre
    }

def scrape_chapter(url, chapter_number):
    """
    This function will scrape the chapter from freewebnovel.com
    as well as (try to) automatically clear the text of their self-promo.
    """

    full_url = f"{url}/chapter-{chapter_number}"

    chapters_text = []
    for i in range(3): # this is so we can compare to remove chapter of self-promo in filter_self_promo()
        response = requests.get(full_url)
        get_chapter_content(response)
        chapters_text.append(get_chapter_content(response))
    
    filtered_chapter = filter_self_promo(chapters_text)
    return filtered_chapter

def filter_self_promo(chapters_text):
    """
    Filters words that appear in all three chapter texts to remove self-promotion.
    Returns the filtered text as a single string.
    """
    # Split into paragraphs first
    paragraphs = chapters_text[0].split('\n')
    
    filtered_paragraphs = []
    for paragraph in paragraphs:
        words = paragraph.split()
        filtered_words = []
        
        for word in words:
            if word in chapters_text[1] and word in chapters_text[2]:
                filtered_words.append(word)
        
        if filtered_words:  # Only add non-empty paragraphs
            filtered_paragraphs.append(' '.join(filtered_words))

    filtered_text = '\n\n'.join(filtered_paragraphs)

    return filtered_text

def get_chapter_content(response):
    """
    Retrieves the chapter title and content from a BeautifulSoup object.
    Returns a tuple of (chapter_title, paragraphs)
    Raises:
        ValueError: If the chapter title or content cannot be found
    """

    soup = BeautifulSoup(response.text, 'html.parser')

    chapter_title_element = soup.select_one('.chapter')
    if not chapter_title_element:
        raise ValueError("Could not find chapter title")
    full_title = chapter_title_element.text.strip()

    article_div = soup.select_one('.txt #article')
    if not article_div:
        raise ValueError("Could not find chapter content")
    
    all_paragraphs = [p.get_text().strip() for p in article_div.find_all('p') if p.get_text().strip()]
    if not all_paragraphs:
        raise ValueError("Chapter content is empty")

    # Return title and content separately
    return full_title + "\n\n\n" + '\n\n'.join(all_paragraphs)