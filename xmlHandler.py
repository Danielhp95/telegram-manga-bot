import bs4
from bs4 import BeautifulSoup

BOT_STATE                   = 'bot_state/bot_state.xml'
MANGA_AND_SUBSCRIPTIONS     = 'bot_state/manga_and_subscriptions.xml'
SOURCES                     = 'bot_state/sources.xml'

def add_subscriber_to_manga(manga, chat_id):
    pass

def remove_subscriber_from_manga(manga, chat_id):
    pass

def add_manga_name(manga):
    pass

def set_manga_current_chapter(manga, chapter):
    pass

def add_manga_source(source):
    pass

def set_last_message_id(message_id):
    pass

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


    #Save to file
def write_xml_to_file(beautifulSoup, filename):
    markdown = beautifulSoup.prettify()
    with open(filename,'w+') as f:
        f.write(markdown)
        f.write('\n')


if __name__ == '__main__':
    initialize_bot_state()

