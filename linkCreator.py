import requests
import time


# Map from domain name to URL for each manga site, formatting occurs within lambda functions
SOURCES = {"mangafreak" : lambda name,chapter: "http://www3.mangafreak.net/Read1_{}_{}".format(name.replace(' ','_'),chapter),
           "mangasee" : lambda name,chapter: "http://mangaseeonline.us/read-online/{}-chapter-{}-page-1.html".format(name.replace(' ','-'),chapter),
           "mangadeep" : lambda name,chapter: "http://www.mangadeep.com/{}/{}".format(name.replace(' ','_'),chapter),
           "readonepiece" : lambda name, chapter: "http://ww1.readonepiece.com/chapter/{}-chapter-{}/".format(name.replace(' ','-'),chapter)
          }

manga_and_current_chapter = {"One Piece" : 871}

"""
Params:
    source: domain name, must be member of SOURCES.
    name:   name of the manga.
    chapter: chapter to read

"""
def checkIfChapterExists(source,name,chapter):
    url = SOURCES[source](name,chapter)
    response = requests.get(url)
    if response.status_code == 200:
        print("Chapter exists")
    else:
        print("Chapter DOES NOT exists")
    return response.status_code == 200

def createLinkToChapter(source,name,chapter):
    exists = checkIfChapterExists(source,name,chapter)
    url = SOURCES[source](name,chapter) if exists else None
    return url

def linkAllSources(name,chapter):
    return [link(name,chapter) for source, link in SOURCES.items() if checkIfChapterExists(source,name,chapter)]

# Checks if any source in SOURCES has the input chapter for input manga name
def pollSources(name,chapter):
    return any([checkIfChapterExists(source,name,chapter) for source in SOURCES])

"""
Main feature of telegram bot. Finds out when a new manga chapter is coming out for all
subscribed manga
"""
def busyPollSourcesForNextChapter():
    while True:
        for manga, current_chapter in manga_and_current_chapter.items():
            new_chapter_released = pollSources(manga, current_chapter + 1)
            if new_chapter_released:
                # USE LOGGING
                # Send message to group saying that new chaoter has been found
                manga_and_current_chapter[manga] = current_chapter + 1
            else:
                # Use logging, no chapter came out.
                pass
        time.sleep(4)

busyPollSourcesForNextChapter()


