
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import os
import subprocess
from email_utils import EmailConnection
import config

TEMP_COVER_IMAGE = 'cover_img.png'

BASE_URL = config.configuration['BASE_URL']

TARGET_PATH = config.configuration['TARGET_PATH']

page_content = requests.get(BASE_URL + TARGET_PATH)

soup = BeautifulSoup(page_content.text, 'html.parser')


book_name = soup.select('div.detail-top > h2')[0].text
book_name_dash = book_name.replace(' ', '-').lower()
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

# get cover image

imglink = soup.findAll('img')[0]['src']

if(imglink.startswith('..')):
	imglink = imglink[2:]

print(BASE_URL +  imglink)
 
 
# download the url contents in binary format
r = requests.get(BASE_URL +  imglink)
 
# open method to open a file on your system and write the contents
with open(TEMP_COVER_IMAGE, "wb") as code:
    code.write(r.content)

book.set_cover("image.jpg", open('cover_img.png', 'rb').read())

os.remove(TEMP_COVER_IMAGE)

# Navigagte pages

epub_spine = ['nav']
table_of_content = ()

while True:

	print('...fetching....' + link)
	page_content = requests.get(BASE_URL + link)
	soup = BeautifulSoup(page_content.text, 'html.parser')

	story_page_content = soup.select('div.chapter-content-p')[0].contents

	chapter_name = soup.select('h3.title')[0].text
	chapter_name_dash = chapter_name.replace(' ', '-').lower()


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
epub.write_epub(book_name_dash + '.epub', book, {})

print(book_name_dash)

# fire kindlegen to generate .mobi

subprocess.call('lib/KindleGen/kindlegen ' + book_name_dash+'.epub -c1', shell = True)


# send the file to kindle

if( config.configuration['SEND_TO_KINDLE']== 'Y'):

	mailer = EmailConnection(server = config.configuration['SMTP_SERVER'], username = config.configuration['SMTP_USER'], password= config.configuration['SMTP_PASSWORD'])
	mailer.send(send_from = config.configuration['SEND_FROM'], send_to = config.configuration['SEND_TO'], 
		subject= book_name, text ='attaching the content', files = [book_name_dash + '.mobi'])
	mailer.close()


	print("mobi file sent to your kindle!!!")






