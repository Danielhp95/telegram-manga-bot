import requests
import time
import bs4
from bs4 import BeautifulSoup
import xmlHandler
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Extra source for one piece
# "readonepiece" : lambda name, chapter: "http://ww1.readonepiece.com/chapter/{}-chapter-{}/".format(name.replace(' ','-').lower(),chapter)

"""
Params:
    source: domain name, must be member of SOURCES.
    name:   name of the manga.
    chapter: chapter to read
"""
def checkIfChapterExists(source, manga_name, chapter):
    url = createLink(source, manga_name, chapter) 
    # Checks for chapter existence
    chapter_exists = urlExists(url)
    chapter_exists &= urlContainsMangaChapter(url,source)
    # End checks

    chapter_state = 'EXISTS' if chapter_exists else 'ABSENT'
    logger.info("{} {} {} in {}".format(manga_name, chapter, chapter_state, source.source_name.string))
    return chapter_exists

# creates a link in string format. May need further thought to integrate more sources
def createLink(source, manga_name, chapter):
    link = source.link.string
    sep = source.separator.string
    if source.source_name.string == 'mangadeep' and manga_name.lower() == 'one piece':
        manga_name = 'one_peice' # Super hacky way to get mangadeep to work
    final_link = link.format(manga_name.replace(' ',sep).lower(),chapter)
    return final_link


"""
    Checks for chapter existence
"""
def urlExists(url):
    response = requests.get(url)
    return response.status_code == 200

def urlContainsMangaChapter(url, source):
    if source.find('existence_check') is None:
        return True # If there are no checks, we assume manga exists

    logger.debug('Check that source {} contains manga chapter'.format(source.source_name.string))
    tag_name   = source.existence_check.target_tag.string  
    attr_name  = source.existence_check.attr_name.string  
    attr_value = source.existence_check.attr_value.string  
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml")
    manga_page_exists = soup.find(tag_name, {attr_name : attr_value})
    return manga_page_exists is not None

"""
    Input:
        - manga_name: name of manga to retrieve
        - chapter: chapter number to retrieve
"""
def linkAllSources(manga_name,chapter):
    sources = xmlHandler.get_sources_for_manga(manga_name)
    return [createLink(source, manga_name, chapter) for source in sources if checkIfChapterExists(source, manga_name, chapter)]

def findLatestChapter(manga_name):
    latest_chapter = xmlHandler.get_manga_latest_chapter(manga_name)
    return int(latest_chapter)

# Checks if any source in SOURCES has the input chapter for input manga name
def pollSources(manga_name,chapter):
    return any([checkIfChapterExists(source,name,chapter) for source in xmlHandler.get_sources_for_manga(manga_name)])

"""
Main feature of telegram bot. Finds out when a new manga chapter is coming out for all
subscribed manga
"""
#TODO: link new_chapter released to aciion_send_chapter_release_message()
def busyPollSourcesForNextChapter():
    sleeping_frequence_seconds = 4
    while True:
        mangas = xmlHandler.get_all_mangas()
        for manga in mangas:
            cur_chap = int(manga.latest_chapter.string)
            manga_name = manga.manga_name.string
            logger.info('START polling for %s chapter %i', manga_name,cur_chap + 1)
            new_chapter_released = pollSources(manga_name, current_chapter + 1)
            if new_chapter_released:
                # USE LOGGING
                # Send message to group saying that new chaoter has been found
                print('caca')
            else:
                # Use logging, no chapter came out.
                print('caca')
                pass
        logger.info('FINISHED polling round.')
        time.sleep(sleeping_frequence_seconds)

if __name__ == '__main__':
    print(linkAllSources('one piece',874))
    #busyPollSourcesForNextChapter()
