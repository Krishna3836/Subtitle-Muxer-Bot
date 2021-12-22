
import time
import os

from translation import Translation
from config import Config
from pyrogram import Client, filters
from helper_func.progress_bar import progress_bar
from helper_func.dbhelper import Database as Db
from plugins.forcesub import handle_force_subscribe
import re
import requests
from urllib.parse import quote, unquote
db = Db()

@Client.on_message(filters.document & filters.private)
async def save_doc(bot, message, cb=False):
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    me = await bot.get_me()
    chat_id = message.from_user.id
    start_time = time.time()
    downloading = await bot.send_message(chat_id, 'Downloading your File!')
    download_location = await bot.download_media(
        message = message,
        file_name = Config.DOWNLOAD_DIR+'/',
        progress = progress_bar,
        progress_args = (
            'Initializing',
            downloading,
            start_time
        )
    )

    if download_location is None:
        return bot.edit_message_text(
            text = 'Downloading Failed!',
            chat_id = chat_id,
            message_id = downloading.message_id
        )

    await bot.edit_message_text(
        text = Translation.DOWNLOAD_SUCCESS.format(round(time.time()-start_time)),
        chat_id = chat_id,
        message_id = downloading.message_id
    )

    tg_filename = os.path.basename(download_location)
    try:
        og_filename = message.document.filename
    except:
        og_filename = False

    if og_filename:
        #os.rename(Config.DOWNLOAD_DIR+'/'+tg_filename,Config.DOWNLOAD_DIR+'/'+og_filename)
        save_filename = og_filename
    else :
        save_filename = tg_filename

    ext = save_filename.split('.').pop()
    filename = str(round(start_time))+'.'+ext

    if ext in ['srt','ass']:
        os.rename(Config.DOWNLOAD_DIR+'/'+tg_filename,Config.DOWNLOAD_DIR+'/'+filename)
        db.put_sub(chat_id, filename)
        if db.check_video(chat_id):
            text = 'Subtitle file downloaded successfully.\nChoose your desired muxing!\n[ /softmux , /hardmux ]'
        else:
            text = 'Subtitle file downloaded.\nNow send Video File!'

        await bot.edit_message_text(
            text = text,
            chat_id = chat_id,
            message_id = downloading.message_id
        )

    elif ext in ['mp4','mkv']:
        os.rename(Config.DOWNLOAD_DIR+'/'+tg_filename,Config.DOWNLOAD_DIR+'/'+filename)
        db.put_video(chat_id, filename, save_filename)
        if db.check_sub(chat_id):
            text = 'Video file downloaded successfully.\nChoose your desired muxing.\n[ /softmux , /hardmux ]'
        else :
            text = 'Video file downloaded successfully.\nNow send Subtitle file!'
        await bot.edit_message_text(
            text = text,
            chat_id = chat_id,
            message_id = downloading.message_id
        )

    else:
        text = Translation.UNSUPPORTED_FORMAT.format(ext)+f'\nFile = {tg_filename}'
        await bot.edit_message_text(
            text = text,
            chat_id = chat_id,
            message_id = downloading.message_id
        )
        os.remove(Config.DOWNLOAD_DIR+'/'+tg_filename)

@Client.on_message(filters.video & filters.private)
async def save_video(bot, message, cb=False):
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    me = await bot.get_me()

    chat_id = message.from_user.id
    start_time = time.time()
    downloading = await bot.send_message(chat_id, 'Downloading your File!')
    download_location = await bot.download_media(
        message = message,
        file_name = Config.DOWNLOAD_DIR+'/',
        progress = progress_bar,
        progress_args = (
            'Initializing',
            downloading,
            start_time
            )
        )

    if download_location is None:
        return bot.edit_message_text(
            text = 'Downloading Failed!',
            chat_id = chat_id,
            message_id = downloading.message_id
        )

    await bot.edit_message_text(
        text = Translation.DOWNLOAD_SUCCESS.format(round(time.time()-start_time)),
        chat_id = chat_id,
        message_id = downloading.message_id
    )

    tg_filename = os.path.basename(download_location)
    try:
        og_filename = message.document.filename
    except:
        og_filename = False
    
    if og_filename:
        save_filename = og_filename
    else :
        save_filename = tg_filename
    
    ext = save_filename.split('.').pop()
    filename = str(round(start_time))+'.'+ext
    os.rename(Config.DOWNLOAD_DIR+'/'+tg_filename,Config.DOWNLOAD_DIR+'/'+filename)
    
    db.put_video(chat_id, filename, save_filename)
    if db.check_sub(chat_id):
        text = 'Video file downloaded successfully.\nChoose your desired muxing.\n[ /softmux , /hardmux ]'
    else :
        text = 'Video file downloaded successfully.\nNow send Subtitle file!'
    await bot.edit_message_text(
            text = text,
            chat_id = chat_id,
            message_id = downloading.message_id
            )


@Client.on_message(filters.text & filters.regex('^http'))
async def save_url(bot, message, cb=False):
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    me = await bot.get_me()
    chat_id = message.from_user.id
    save_filename = None

    if "|" in message.text:
        if len(message.text.split('|')) ==2 :
            save_filename = message.text.split('|')[1].strip()
            url = message.text.split('|')[0].strip()
    else :
        url = message.text.strip()

    if save_filename and len(save_filename)>60:
        return await client.sendMessage(chat_id, Chat.LONG_CUS_FILENAME)

    r = requests.get(url, stream=True, allow_redirects=True)
    if save_filename is None :
        if 'content-disposition' in r.headers.keys() :
            regx = 'filename="(.*?)"'
            res = re.search(regx, str(r.headers))
            if res :
                save_filename = res.group(1)
            else :
                #removing argumets from url!
                if '?' in url:
                    url = ''.join(url.split('?')[0:-1])
                save_filename = url.split('/')[-1]
                save_filename = unquote(save_filename)
        else :
            if '?' in url:
                url = ''.join(url.split('?')[0:-1])
            save_filename = url.split('/')[-1]
            save_filename = unquote(save_filename)

    sent_msg = await bot.send_message(chat_id, 'Preparing Your Download')
    ext = save_filename.split('.')[-1]
    if ext not in ['mp4','mkv'] :
        return await sent_msg.edit(Chat.UNSUPPORTED_FORMAT.format(ext))

    size = None
    if 'content-length' in r.headers.keys() :
        size = int(r.headers['content-length'])

    if not size :
        return await sent_msg.edit(Chat.FILE_SIZE_ERROR)
    if size>(2*1000*1000*1000) :
        return await sent_msg.edit(Chat.MAX_FILE_SIZE)

    if not os.path.exists(Config.DOWNLOAD_DIR) :
        os.mkdir(Config.DOWNLOAD_DIR)

    current = 0
    start = time.time()
    filename = str(round(start))+'.'+ext

    logging.info(url)

    with requests.get(url, stream=True, allow_redirects=True) as r :
        with open(os.path.join(Config.DOWNLOAD_DIR,filename), 'wb') as f :
            for chunk in r.iter_content(chunk_size=1024*1024) :
                if (chunk) :
                    written = f.write(chunk)
                    #current += 1024*1024
                    current += written
                    await progress_bar(current, size, 'Downloading Your File!', sent_msg, start)

    logging.info(save_filename)

    try:
        await sent_msg.edit(
            Translation.DOWNLOAD_SUCCESS.format(round(time.time()-start))
            )
    except:
        pass

    db.put_video(chat_id, filename, save_filename)
    if db.check_sub(chat_id) :
        text = 'Video File Downloaded.\nChoose your desired muxing\n[ /softmux , /hardmux ]'
    else :
        text = 'Video File Downloaded.\nNow send Subtitle file!'
    try:
        await sent_msg.edit(text)
    except:
        pass

