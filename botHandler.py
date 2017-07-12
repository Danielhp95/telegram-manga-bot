import json
import requests
import linkCreator
import Levenshtein as lev
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
#print('level = ' + str(logger.getEffectiveLevel() == logging.DEBUG))

TOKEN = "334385148:AAGp8vXViO_kw_pcKr3rMRQCE46LV7Xkmn4"
URL   = "https://api.telegram.org/bot{}/".format(TOKEN)
processed_message_ids = set()

"""
getUpdates functions
"""
def get_url(url):
    params = {'allowed_updates' : 'nessages'}
    res = requests.get(url, data=params)
    content = res.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates():
    url = URL + "getUpdates"
    js = get_json_from_url(url)
    return js

"""
sendMessage functions
"""

"""
Sends a message to input chat with input text
"""
def send_message(chat=None,text='EMPTY MESSAGE'):
    params = {'chat_id' : chat, 'text' : text}
    url = URL + 'sendMessage'
    res = requests.post(url, data=params)

def action_send_help_message(chat=None):
    # TODO:  write help message
    help_message = 'Write message'
    send_message(chat=chat,text=help_message)

"""
Util functions
"""
def formatLinks(links):
    num_links = len(links)
    txt1 = 'There are {} links for this chapter\n'.format(num_links)
    link_txt = [link + '\n' for link in links]
    return txt1 + ''.join(link_txt)

"""
Every time getUpdates is called, all the messages in the last 24 hours are returned.
In order to avoid missing messages, all of them are read every time getUpdates returns
a value.  We filter out the proccessed messages via message id to avoid re-processing
already proccessed messages.
"""
def process_multiple_updates(updates):
    num_updates = len(updates['result'])
    unprocessed_updates = [u for u in updates['result'] \
                           if u['message']['message_id'] not in processed_message_ids]
    for update in unprocessed_updates:
        # Check if message contains text visible to bot
        if 'text' in update['message']:
            process_single_update(update)
            # Mark this message as processed
            # Add message id TODO
            processed_message_ids.add(update['message']['message_id'])
        


"""
Multiplexer for all bot functionalities
Activation: /mangaka
Current functionalities:
    - Link to latest chapter
    - Link to any previous chapter.
    - Alert when new episode has been released by any of the subscribed manga.
    - Help, sends list of commands back to user.
"""
def process_single_update(update):
    logger.debug('Single update:')
    logger.debug('Message id: %i', update['message']['message_id'])

    message = update['message']['text']
    space_sep_message = messge.split(' ', 1)
    logger.debug('Message text: %s', message)
    logger.debug('Space_separated: %s', space_sep_message[0])
    activation_threshold = 1
    activation_trigger = lev.distance(str(space_sep_message[0]), '/mangaka') <= activation_threshold

    if activation_trigger:
        logger.debug('Activation triggered')
        chat_id = update['message']['chat']['id'] # Chat (group or private) where message was sent
        
        # If message is empty, send help message
        if len(space_sep_message) == 1:
            action_send_help_message(chat_id)
            return

        # If message requests 'subscribe' <mang_name> subscribe to manga
        first_word = message.rsplit(' ', 1)
        if first_word == 'subscribe':
            # Send message saying that subscription was successful. Find latest chapter
            manga_name = message.split(' ',  2)[2] # ['/mangaka','subscribe',manga_name]
            xmlHandler.add_subscriber_to_manga(manga_name)

        # If message requests <manga_name> <chapter> send links
        message = space_sep_message[1]
        manga_and_chapter   = message.rsplit(' ', 1)
        manga_name, chapter = manga_and_chapter[0], manga_and_chapter[1]
        action_retrieve_manga_chapter(manga_name, chapter)
        return
"""
    Sends a list of links of manga chapters from the input manga and chapter number
"""
def action_retrieve_manga_chapter(manga_name, chapter):
        chapter = chapter if chapter != 'latest' else linkCreator.findLatestChapter(manga_name)
        logger.info('Manga: %s. Chapter: %s', manga_name, chapter)

        links = linkCreator.linkAllSources(manga_name, chapter)
        send_message(chat=chat_id,text=formatLinks(links))


        
process_multiple_updates(get_updates())
