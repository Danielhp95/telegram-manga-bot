#!/usr/bin/env python
import os
import bs4
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
DESIGN CHOICE: all functions that return a value return a string.
"""

BOT_STATE                   = 'bot_state/bot_state.xml'
MANGA_AND_SUBSCRIPTIONS     = 'bot_state/manga_and_subscriptions.xml'
SOURCES                     = 'bot_state/sources.xml'

def get_all_mangas():
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    return root.find_all('manga')

def add_subscriber_to_manga(manga_name, chat_id):
    # Opening file
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    manga = find_manga_by_name_from_list(root.find_all('manga'),manga_name)

    if manga is None:
        return False

    new_sub_tag = root.new_tag('subscriber')
    new_sub_tag.string = str(chat_id)
    manga.subscribers.append(new_sub_tag)

    write_xml_to_file(root,MANGA_AND_SUBSCRIPTIONS)
    return True

def get_subscribers_for_manga(manga_name):
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    manga = find_manga_by_name_from_list(root.find_all('manga'),manga_name)
    subs_tags = manga.find_all('subscriber')
    return [sub.string for sub in subs_tags]

#TODO not done yet.
def remove_subscriber_from_manga(manga_name, chat_id):
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    manga = find_manga_by_name_from_list(root.find_all('manga'),manga_name)
    subscriber_list = manga.subscribers.findChildren()
    
    extracted_sub = None
    for sub in subscriber_list:
        if sub.string == str(chat_id):
            extracted_sub = sub.extract()
    return extracted_sub is not None 
    
    

"""
    Adds a new manga in xml to the file specified in MANGA_AND_SUBSCRIPTIONS
    <mangas>
        <manga>
            <name>
            <latest_chapter>
            <subscribers>
                <subscriber>...
            </subscribers> 
        </manga>
        ...
    </mangas>
"""
# TODO: Make sure every call uses latest_chapter
def add_manga(manga_name=None, latest_chapter=None):
    if manga_name is None:
        raise  ValueError('Manga name must be present')
    
    # Openning File
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    
    # Create tags for name, chapter and subscribers
    name_tag = root.new_tag('manga_name') # If we called  it 'name' it would clash with beautiful soup notation
    name_tag.string = manga_name

    latest_chapter_tag = root.new_tag('latest_chapter')
    # If last chapter is not present, leave tag open
    if latest_chapter is not None:
        logger.info('Latest chapter of {} set to {}'.format(manga_name, latest_chapter))
        latest_chapter_tag.string = str(latest_chapter)
    
    # Subscribers are specified as chat ids
    subscribers_tag = root.new_tag('subscribers')

    new_manga_tag = root.new_tag('manga')

    # Append new tags to BeautifulSoup object
    new_manga_tag.append(name_tag)
    new_manga_tag.append(latest_chapter_tag)
    new_manga_tag.append(subscribers_tag)
    # Append to root tag
    root.mangas.append(new_manga_tag)

    #Write to file
    write_xml_to_file(root, MANGA_AND_SUBSCRIPTIONS)

def set_manga_latest_chapter(manga_name, latest_chapter):
    # Openning File
    root = open_file(MANGA_AND_SUBSCRIPTIONS)

    # Finding the manga and changing the latest chapter value
    manga = find_manga_by_name_from_list(root.find_all('manga'),manga_name)
    manga.latest_chapter.string = str(latest_chapter)
    write_xml_to_file(root, MANGA_AND_SUBSCRIPTIONS) 

def get_manga_latest_chapter(manga_name):
    root = open_file(MANGA_AND_SUBSCRIPTIONS)
    manga = find_manga_by_name_from_list(root.find_all('manga'),manga_name)
    return manga.latest_chapter.string

"""
    Adds a new source in xml to the file specified in SOURCES
    <sources>
        <source>
            <source_name>
            <link>
            <separator>
            <existance_check>
                <target_tag>...
                <attr_name>...
                <attr_value>...
            </existance_check> 
        </source>
        ...
    </sources>
"""
# TODO: Make sure every call uses latest_chapter

# Valid_mangas input serves to identify which mangas can be retrieved from source
def add_manga_source(name=None, generic_link=None, valid_mangas='all', separator=None,
                     target_tag=None, attr_name=None, attr_value=None):
    if name is None or generic_link is None or separator is None:
        raise ValueError('Both the name of the source and the generic link and separator must be set')

    root = open_file(SOURCES)

    new_source_tag = root.new_tag('source')
    new_source_tag['valid_mangas'] = valid_mangas

    source_name_tag = root.new_tag('source_name')
    source_name_tag.string = name

    source_link_tag = root.new_tag('link')
    source_link_tag.string = generic_link

    source_separator_tag = root.new_tag('separator')
    source_separator_tag.string = separator

    if target_tag is not None and attr_name is not None and attr_value is not None:
        source_existance_check_tag = root.new_tag('existence_check')

        source_existance_target_tag = root.new_tag('target_tag')
        source_existance_target_tag.string = target_tag

        source_existance_attr_name  = root.new_tag('attr_name')
        source_existance_attr_name.string = attr_name

        source_existance_attr_value = root.new_tag('attr_value')
        source_existance_attr_value.string = attr_value

        source_existance_check_tag.append(source_existance_target_tag)
        source_existance_check_tag.append(source_existance_attr_name)
        source_existance_check_tag.append(source_existance_attr_value)

        new_source_tag.append(source_existance_check_tag)

    new_source_tag.append(source_name_tag)
    new_source_tag.append(source_link_tag)
    new_source_tag.append(source_separator_tag)

    root.sources.append(new_source_tag)
    logger.debug('New source added, current number of sources: {}'.format(len(root.find_all('source'))))
    write_xml_to_file(root, SOURCES)

def get_sources_for_manga(manga_name):
    root = open_file(SOURCES)

    # Given a source tag, checks if it is valid for this manga
    source_for_manga = lambda source: source.name == 'source' and (source['valid_mangas'] == manga_name or source['valid_mangas'] == 'all')
    d = root.sources.find_all('source')
    source_tags = root.sources.find_all(source_for_manga)
    return source_tags
    #return [(source.source_name.string, source.link.string, source.separator.string) for source in source_tags]

def set_last_message_id(message_id):
    root = open_file(BOT_STATE)
    root.bot_state.last_message_id.string = str(message_id)
    write_xml_to_file(root,BOT_STATE)
    pass

def get_last_message_id():
    root = open_file(BOT_STATE)
    return root.bot_state.last_message_id.string



"""
    Utils functions
"""

# Finds a manga by it's manga_name field given a list of mangas
def find_manga_by_name_from_list(mangas, name_to_find):
    for manga in mangas:
        if manga.manga_name.string == name_to_find:
            return manga
    logger.debug('Manga {} not found'.format(name_to_find))
    return None

# Opens xml file into a beautifulSoup object
def open_file(filename):
    f = open(filename, 'r')
    root = BeautifulSoup(f, features='xml')
    f.close()
    return root

# Writes content to filename
def write_xml_to_file(beautifulSoup, filename):
    markdown = str(beautifulSoup) #beautifulSoup.prettify()
    with open(filename,'w+') as f:
        f.write(str(markdown))
        f.write('\n')


"""
    Initialization functions in case files are destroyed.
"""
def initialize_bot_state():
    state = bs4.BeautifulSoup('<bot_state></bot_state>',features='xml')
    last_message_id = state.new_tag('last_message_id')
    last_message_id.string = '0'
    state.bot_state.append(last_message_id)
    number_of_chats = state.new_tag('number_of_chats')
    number_of_chats.string = '0'
    state.bot_state.append(number_of_chats)
    write_xml_to_file(state, BOT_STATE)

def initialize_manga_and_subscriptions():
    mangas = bs4.BeautifulSoup('<mangas></mangas>',features='xml')
    write_xml_to_file(mangas, MANGA_AND_SUBSCRIPTIONS)

def initialize_sources():
    mangas = bs4.BeautifulSoup('<sources></sources>',features='xml')
    write_xml_to_file(mangas, SOURCES)

    # Minimal sources
    add_manga_source(name='mangafreak', generic_link='http://www3.mangafreak.net/Read1_{}_{}', valid_mangas='all', separator='_')
    add_manga_source(name='mangasee',   generic_link='http://mangaseeonline.us/read-online/{}-chapter-{}-page-1.html', valid_mangas='all', separator='-')
    add_manga_source(name='mangapanda', generic_link='http://mangapanda.com/{}/{}', valid_mangas='all', separator='-', target_tag='img', attr_name='name', attr_value='img')
    add_manga_source(name='mangadeep',  generic_link='http://www.mangadeep.com/{}/{}/', valid_mangas='all', separator='_', target_tag='img', attr_name='class', attr_value='manga-page')

def initialize_directory():
    os.mkdir("bot_state/")

def initialize_xml_files():
    initialize_directory()
    initialize_bot_state()
    initialize_sources()
    initialize_manga_and_subscriptions()

if __name__ == '__main__':
    initialize_xml_files()
    add_manga('one piece')
    set_manga_latest_chapter('one piece', 871)
