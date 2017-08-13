import json
import requests
import xmlHandler
import linkCreator
import logging
logging.basicConfig(level=logging.INFO)
logging.disable(logging.DEBUG)
logger = logging.getLogger('caca')
#print('level = ' + str(logger.getEffectiveLevel() == logging.DEBUG))

TOKEN = "334385148:AAGp8vXViO_kw_pcKr3rMRQCE46LV7Xkmn4"
URL   = "https://api.telegram.org/bot{}/".format(TOKEN)
ALLOWED_ACTIONS = ['help','get','subscribe']

"""
getUpdates functions
"""
def get_url(url, last_message_id):
    res = requests.get(url, params=dict(offset=str(last_message_id),timeout=60))
    content = res.content.decode("utf8")
    return content

def get_json_from_url(url, last_message_id):
    content = get_url(url, last_message_id)
    js = json.loads(content)
    return js

def get_updates(last_message_id):
    url = URL + "getUpdates"
    js = get_json_from_url(url, last_message_id)
    return js

"""
sendMessage functions
"""

"""
Sends a message to input chat with input text
"""
def send_message(chat=None,text='EMPTY MESSAGE'):
    url = URL + 'sendMessage'
    res = requests.post(url, params=dict(chat_id=chat, text=text))

def action_send_help_message(chat=None):
    help_message = """Yo, here are the list of possible commands:
    /mangaka get <manga name> <manga chapter> 
        (i.e /mangaka get one piece 874)
    /mangaka subscribe <manga name> 
        (i.e /mangaka subscribe berserk)
    /mangaka help 
        (to send this message) """

    send_message(chat=chat,text=help_message)

def action_send_non_understood_message(user_name, chat_id):
    non_understood_message = '{}, no me hables con la boca llena'.format(user_name)
    send_message(chat=chat_id,text=non_understood_message)

"""
    Sends a list of links of manga chapters from the input manga and chapter number
"""
def action_retrieve_manga_chapter(manga_name, chapter, chat_id):
        chapter = chapter if chapter != 'latest' else linkCreator.findLatestChapter(manga_name)
        logger.info('Manga: %s. Chapter: %s', manga_name, chapter)

        links = linkCreator.linkAllSources(manga_name, chapter)
        send_message(chat=chat_id,text=formatLinks(links, manga_name, chapter))


"""
Util functions
"""
def formatLinks(links, manga_name, chapter):
    num_links = len(links)
    txt1 = 'There are {} links for {} chapter {}\n'.format(num_links, manga_name, chapter)
    link_txt = [link + '\n' for link in links]
    return txt1 + ''.join(link_txt)



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
    space_sep_message = message.split(' ', 1)
    logger.debug('Message text: %s', message)
    logger.debug('Space_separated: %s', space_sep_message[0])
    activation_threshold = 1
    activation_trigger = str(space_sep_message[0]) == '/mangaka'

    if activation_trigger:
        logger.debug('Activation triggered')
        chat_id = update['message']['chat']['id'] # Chat (group or private) where message was sent
        
        # If message is empty, send help message
        if len(space_sep_message) == 1:
            action_send_help_message(chat_id)
            return


        parameters = message.split(' ',1)[1] # [/mangaka, parameters]
        action = parameters.split(' ',1)[0]
        if action not in ALLOWED_ACTIONS or action == 'help': # If actions is non valid
            action_send_help_message(chat_id)
            return

        action_parms = parameters.split(' ',1)[1] # [parameters]
        # If message requests 'subscribe' <mang_name> subscribe to manga
        if action == 'subscribe':
            # Send message saying that subscription was successful. Find latest chapter
            manga_name = action_parms[0] # ['subscribe',manga_name]
            xmlHandler.add_subscriber_to_manga(manga_name)

        # If message requests 'get' <manga_name> <chapter> send links
        elif action == 'get':
            manga_and_chapter   = action_parms.rsplit(' ', 1) # ['get',manga_name, chapter] THIS IS BAD CODE FOR FK SAKE
            print('action params {}'.format(action_parms))
            print(manga_and_chapter)
            manga_name, chapter = manga_and_chapter[0], manga_and_chapter[1]
            action_retrieve_manga_chapter(manga_name, chapter, chat_id)
        else:
            user_name = update['message']['from']['first_name']
            action_send_non_understood_message(user_name, chat_id)

"""
Every time getUpdates is called, all the messages in the last 24 hours are returned.
In order to avoid missing messages, all of them are read every time getUpdates returns
a value.  We filter out the proccessed messages via message id to avoid re-processing
already proccessed messages.
"""
def process_multiple_updates(updates, last_processed_id):
    # Exit if there are no requests
    if len(updates['result']) == 0:
        return last_processed_id

    for update in updates['result']:
        # Check if message contains text visible to bot
        try:
            if 'text' in update['message']:
                process_single_update(update)
        except KeyError:
            logger.debug(update)
    return updates['result'][-1]['update_id'] + 1 # TODO, revise this decision of increasing by one here

"""
    This is the top-most level function.
    Uses getUpdates() to probe the API and updates last message id whilst serving updates
"""
def long_poll_get_updates():
    while True:
        last_processed_id = int(xmlHandler.get_last_message_id())
         
        unprocessed_id = last_processed_id
        updates = get_updates(unprocessed_id)

        new_last_processed_id = process_multiple_updates(updates, last_processed_id)

        xmlHandler.set_last_message_id(new_last_processed_id)
        logger.info('Set of updates has been processed last message processed id: {}'.format(new_last_processed_id))


if __name__ == '__main__':
    long_poll_get_updates()
