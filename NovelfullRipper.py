import os
import queue
import threading
import time
from urllib.request import urlopen
import urllib.request
from ebooklib import epub
from bs4 import BeautifulSoup
import re
# import requests


class NovelfullThreaded:

    def __init__(self):
        self.start_time = time.time()

        # self.url = 'http://novelfull.com/king-of-gods.html'
        # self.bookTitle = 'King Of Gods'
        # self.start = 1383
        # self.end = 1399

        # self.url = 'http://novelfull.com/release-that-witch.html'
        # self.bookTitle = 'Release that Witch'
        # self.start = 1378
        # self.end = 1498
        #
        # self.url = 'http://novelfull.com/realms-in-the-firmament.html'
        # self.bookTitle = 'Realms in the firmament'
        # self.start = 1670
        # self.end = 1753

        self.url = 'https://novelfull.com/lord-xue-ying.html'
        self.bookTitle = 'Reincarnation Of The Strongest Sword God'
        self.start = 1
        self.end = 1387



        # self.url = "https://novelfull.com/lord-xue-ying.html"
        # self.bookTitle = 'Lord Xue Ying'
        # self.start = 0
        # self.end = 1382

        # self.url = 'http://novelfull.com/the-strongest-system.html'
        # self.bookTitle = 'The Strongest System'
        # self.start = 1
        # self.end = 1159


        # url = 'http://novelfull.com/war-sovereign-soaring-the-heavens.html'
        # bookTitle = 'War Sovereign Soaring The Heavens'
        # start = 1
        # end = 1499

        # self.url = 'http://novelfull.com/the-legend-of-futian.html'
        # self.bookTitle = 'The Legend of Futian'
        # self.start = 1279
        # self.end = 1343

        # self.url = 'http://novelfull.com/martial-god-asura.html'
        # self.bookTitle = 'Martial God Asura'
        # self.start = 3987
        # self.end = 4068

        # self.url = 'http://novelfull.com/reborn-evolving-from-nothing.html'
        # self.bookTitle = 'Reborn - Evolving From Nothing'
        # self.start = 0
        # self.end = 153

        # self.url = 'http://novelfull.com/mystical-journey.html'
        # self.bookTitle = 'Mystical Journey'
        # self.start = 1
        # self.end = 1008

        # self.url = 'http://novelfull.com/ancient-godly-monarch.html'
        # self.bookTitle = 'ANCIENT GODLY MONARCH'
        # self.start = 1668
        # self.end = 1679

        # Ids
        self.base_url = 'https://novelfull.com/'
        self.idOverview = {"id": "list-chapter"}
        self.idContent = {"id": "chapter-content"}

        # Create The EPUB File
        self.book = epub.EpubBook()
        self.book.set_language('en')

        # Book Title
        self.book.set_title(self.bookTitle)

        # stuff
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.headers = {'User-Agent': self.user_agent, }
        self.length = self.end - self.start
        self.chapters = []
        self.q = queue.Queue()

    @staticmethod
    def sort_by_first_value(val):
        return val[0]

    def check_different_divs_title(self, soup, current_chapter_number):
        title_locations = [soup.h3, soup.find('a', {"class": "chapter-title"}), soup.h2, soup.find("div", {"class": "cha-tit"}),
                           "Chapter %s" % current_chapter_number]
        title = []
        count = 0
        while title is None or len(title) < 1:
            title = title_locations[count]
            count += 1
        return title

    def get_all_paragraphs(self, soup):
        data = ''
        for dat in soup.find_all('p'):
            data += str(dat)
        return data

    def check_different_divs_content(self, soup, current_chapter_number):
        divs = [soup.find("div", {"class": "cha-words"}), soup.find("div", {"class": "cha-content"}),
                self.get_all_paragraphs(soup), "No content found for chapter %s. Check if url is correct or "
                                               "if the divs or correct. This could also be an internal error of bs4"
                                                % current_chapter_number]
        data = []
        count = 0
        while data is None or len(data) < 25:
            data = divs[count]
            count += 1
        return data

    def get_web_page_urls(self, data):
        urls = []
        for link in data.find_all('a'):
            x = link.get('href')
            urls.append(x)
        return urls

    def check_urls(self, urls, current):
        for link in urls[0:50]:
            chapter = self.get_first_number_from_string(link)
            if int(chapter) + 50 < current:
                return None
            if int(chapter) == current:
                return link
            if int(chapter) > current:
                print("not found " + str(chapter))
                return False, 'No data for chapter ' + str(current)

    def get_all_web_pages(self, urls, current_chapter_number):
        print("current chapter " + str(current_chapter_number) + " - " + str(current_chapter_number%50) + ". " + str(len(urls)))
        page_data = self.get_data_from_web_page(self.base_url[:-1] + urls[current_chapter_number%50 - 1], self.idContent,
                                                current_chapter_number - 1)
        return page_data

    def get_url_from_links(self, urls, current_chapter_number, index_page):
        # TODO
        link = urls[0]
        link_chapter = self.get_first_number_from_string(link)
        while link_chapter > current_chapter_number:
            index_url = self.build_index_link_php(int(index_page - 1))
            data = self.get_data_from_web_page(index_url, self.idOverview)
        while (int(link_chapter) + 49) < current_chapter_number:
            index_url = self.build_index_link_php(int(index_page + 1))
            data = self.get_data_from_web_page(index_url, self.idOverview)
        correct_link = urls[current_chapter_number - link_chapter]

    def get_first_number_from_string(self, string):
        return re.search(r'\d+', string).group()

    def find_data_from_content(self, soup, div_id, current_chapter_number):
        data = soup.find("div", div_id)
        if data is None or len(data) < 30 and div_id != self.idOverview:
            data = self.check_different_divs_content(soup, current_chapter_number)
        return data

    def get_content_from_web_page(self, url):
        request = urllib.request.Request(url, None, self.headers)
        response = urllib.request.urlopen(request)
        content = response.read()
        return content

    def get_data_from_web_page(self, url, div_id, current_chapter_number):
        all_data = []
        content = self.get_content_from_web_page(url)

        soup = BeautifulSoup(content, 'html.parser')
        data = self.find_data_from_content(soup, div_id, current_chapter_number)
        title = self.check_different_divs_title(soup, current_chapter_number)

        all_data.append(title)
        all_data.append(data)

        return all_data

    def build_index_link(self, counter):
        index = self.url + '?page=' + str(counter) + '&per-page=50'
        return index

    def build_index_link_php(self, counter):
        index_url = self.base_url + 'index.php/' + self.url[len(self.base_url):] + '?page=' + str(counter) + '&per-page=50'
        return index_url

    def guess_indexurl_location(self, current_chapter_number):
        if current_chapter_number % 50 != 0:
            return (current_chapter_number / 50) + 1
        else:
            return current_chapter_number / 50

    def get_correct_web_page(self, current_chapter_number, index_page, index_page_data):
        # TODO
        not_correct = True
        while not_correct:
            urls = self.get_web_page_urls(index_page_data[1])
            correct_url = self.check_urls(urls, current_chapter_number)
            if correct_url is None:
                print('not the correct url' + ' in chapter ' + str(current_chapter_number))
                index_url = self.build_index_link_php(int(index_page + 1))
                data = self.get_data_from_web_page(index_url, self.idOverview, False)
            elif correct_url[0] is False:
                pageData = ['chapter ' + str(correct_url[0]), 'Not found']
                break
            else:
                not_correct = False
        if not not_correct:
            pageData = self.get_data_from_web_page(self.base_url[:-1] + correct_url, self.idContent, True)
        self.chapters.append([current_chapter_number, pageData])
        self.q.task_done()

    def start_ripping(self):
        while True:
            current_chapter_number = self.q.get()
            index_page = 1
            if current_chapter_number > 50:
                index_page = int(self.guess_indexurl_location(current_chapter_number))
            index_url = self.build_index_link_php(int(index_page))
            index_page_data = self.get_data_from_web_page(index_url, self.idOverview, current_chapter_number)
            # self.get_correct_web_page(current_chapter_number, index_page, index_page_data)
            urls = self.get_web_page_urls(index_page_data[1])[0:50]
            page_data = self.get_all_web_pages(urls, current_chapter_number)
            self.chapters.append([current_chapter_number, page_data])
            self.q.task_done()

    def convert_book(self):
        # why is a while True here?
        # while True:
        current_chapter_number = self.q.get()
        index_page = 1
        if current_chapter_number > 50:
            index_page = int(self.guess_indexurl_location(current_chapter_number))
        index_url = self.build_index_link_php(int(index_page))
        data = self.get_data_from_web_page(index_url, self.idOverview, False)
        not_correct = True
        while not_correct:
            urls = self.get_web_page_urls(data[1])
            correctUrl = self.check_urls(urls, current_chapter_number)
            if correctUrl is None:
                print('not the correct url' + ' in chapter ' + str(current_chapter_number))
                index_url = self.build_index_link_php(int(index_page + 1))
                data = self.get_data_from_web_page(index_url, self.idOverview, False)
            elif correctUrl[0] is False:
                pageData = ['chapter ' + str(correctUrl[0]), 'Not found']
                break
            else:
                not_correct = False
        if not not_correct:
            pageData = self.get_data_from_web_page(self.base_url[:-1] + correctUrl, self.idContent, True)
        self.chapters.append([current_chapter_number, pageData])
        self.q.task_done()

    def progress_bar(self, complete):
        maxi = 50
        if not complete:
            completed = len(self.chapters)
            todo = self.length
            progress = todo - completed
            prog = todo - progress

            percentage = prog /self.length * 100
            percentage = format(percentage, '.0f')

            strg = ''
            maxi = 50
            x = maxi / self.length
            bar_length = 1/x

            if completed > bar_length:
                bar = int(prog / bar_length)
                print('\r[' + '=' * bar, end=' ' * ((maxi - 1) - bar) + ']' + str(percentage) + '%')
                strg += '='
        else:
            print('\r[' + '=' * maxi, end=']' + '100%\n')

    def save_book(self):
        # TODO refactor
        # SaveLocation
        dirpath = os.getcwd()
        pathToLocation = dirpath + '\\Files\\' + self.bookTitle + '\\'

        if not os.path.exists(pathToLocation):
            os.mkdir(pathToLocation)
        saveLocation = pathToLocation + self.bookTitle + '_' + str(self.start) + '_' + str(self.end) + '.epub'
        print("Saving . . .")

        # Saves Your EPUB File
        epub.write_epub(saveLocation, self.book, {})

        # Location File Got Saved
        if pathToLocation == '':
            print("Saved at " + str(os.getcwd()) + ' as "' + self.bookTitle + '_' + str(self.start) + '_'
                  + str(self.end) + '.epub"')
        else:
            print("Saved at " + saveLocation)

        os.startfile(pathToLocation)

        print('runtime: ' + str(time.time() - self.start_time))

    def create_book(self):
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        # Defines CSS Style
        style = 'p {text-align: left;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        # Adds CSS File
        self.book.add_item(nav_css)

    def parse_chapters(self):
        # TODO refactor
        for i in range(len(self.chapters)):
            try:
                chapter_title = self.chapters[i][1][0].get_text()
            except AttributeError as e:
                chapter_title = 'Chapter ' + str(i)

            # Creates a chapter
            c2 = epub.EpubHtml(title=chapter_title, file_name='chap_' + str(self.start + i) + '.xhtml', lang='hr')

            if len(self.chapters[i][1]) > 2 and self.chapters[i][1][2] is True:
                c2.content = self.chapters[i][1][0].encode("utf-8") + self.chapters[i][1][1].encode("utf-8")
            else:
                c2.content = self.chapters[i][1][1].encode("utf-8")
            self.book.add_item(c2)

            # Add to table of contents
            self.book.toc.append(c2)

            # Add to book ordering
            self.book.spine.append(c2)

            print("Parsed Chapter " + str(self.start + i))

    def create_progressbar(self):
        while len(self.chapters) < self.length:
            self.progress_bar(False)
            time.sleep(1)

    def create_threads(self, number_of_threads=5):
        for item in range(self.start, self.end + 1):
            self.q.put(item)

        for x in range(number_of_threads):
            th = threading.Thread(target=self.start_ripping)
            th.daemon = True
            th.start()

    def start(self):
        self.create_threads(5)
        self.create_progressbar()
        self.q.join()
        self.chapters.sort(key=self.sort_by_first_value)
        self.progress_bar(True)
        self.parse_chapters()
        self.create_book()
        self.save_book()

if __name__ == '__main__':
    x = NovelfullThreaded()
    NovelfullThreaded.start(x)
