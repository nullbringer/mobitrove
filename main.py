import urllib3
from bs4 import BeautifulSoup
from ebooklib import epub

BASE_URL = 'http://pnovels.net'

TARGET_PATH = '/241331-a-shadow-in-summer.html'

http = urllib3.PoolManager()
page_content = http.request('GET',BASE_URL + TARGET_PATH)

soup = BeautifulSoup(page_content.data, 'html.parser')


book_name = soup.select('div.detail-top > h2')[0].text
author_name  = soup.select('div.detail-top > p')[0].text.split(':')[1].strip()


link   = soup.select('div.detail-top > a')[0]['href']

print(book_name)
print(author_name)


book = epub.EpubBook()

# set metadata
book.set_identifier('id123456')
book.set_title(book_name)
book.set_language('en')

book.add_author(author_name)

# Navigagte pages

epub_spine = ['nav']
table_of_content = ()

while True:

	print('...fetching....' + link)
	page_content = http.request('GET',BASE_URL + link)
	soup = BeautifulSoup(page_content.data, 'html.parser')

	story_page_content = soup.select('div.chapter-content-p')[0].contents

	chapter_name = soup.select('h3.title')[0].text
	chapter_name_dash = ''.join(e for e in chapter_name if e.isalnum() or e == '-')


	nav_buttons = soup.select('div.chap-select-dropdown > a')


	# create chapter
	epub_chap = epub.EpubHtml(title=chapter_name, file_name=chapter_name_dash + '.xhtml', lang='hr')
	epub_chap.content='<html><head></head><body><h1>' + chapter_name + '</h1>'


	for para in story_page_content:
		para_str = str(para)
		if('<br' not in para_str and 'p>' not in para_str):
			epub_chap.content = epub_chap.content + '<p>' + para_str + '</p>'
			# print(para_str)

	epub_chap.content = epub_chap.content + '</body></html>'
		

	epub_spine.append(epub_chap)
	table_of_content = table_of_content + (epub_chap,)

	# add chapter
	book.add_item(epub_chap)

	should_continue = False
	for nav_button in nav_buttons:
		if (nav_button.text.strip() == 'Next'):
			link   = nav_button['href']
			should_continue = True

	if should_continue == False:
		break
	# break



book.toc = (table_of_content)

# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# define CSS style
style = 'BODY {color: white;}'
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

# add CSS file
book.add_item(nav_css)

# basic spine
book.spine = epub_spine

# write to the file
epub.write_epub('test.epub', book, {})




