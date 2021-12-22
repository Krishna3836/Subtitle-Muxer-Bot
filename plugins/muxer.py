from pyrogram import Client, filters
from helper_func.progress_bar import progress_bar
from helper_func.dbhelper import Database as Db
from helper_func.mux import softmux_vid, hardmux_vid
from config import Config
from plugins.forcesub import handle_force_subscribe
import time
import os
db = Db()
from database.adduser import AddUser
@Client.on_message(filters.command('softmux') & filters.private)
async def softmux(bot, message, cb=False):
    await AddUser(bot, message)
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    me = await bot.get_me()

    chat_id = message.from_user.id
    og_vid_filename = db.get_vid_filename(chat_id)
    og_sub_filename = db.get_sub_filename(chat_id)
    text = ''
    if not og_vid_filename :
        text += 'First send a Video File\n'
    if not og_sub_filename :
        text += 'Send a Subtitle File!'

    if not (og_sub_filename and og_vid_filename) :
        await bot.send_message(chat_id, text)
        return

    text = 'Your File is Being Soft Subbed. This should be done in few seconds!'
    sent_msg = await bot.send_message(chat_id, text)

    softmux_filename = await softmux_vid(og_vid_filename, og_sub_filename, sent_msg)
    if not softmux_filename:
        return

    final_filename = db.get_filename(chat_id)
    os.rename(Config.DOWNLOAD_DIR+'/'+softmux_filename,Config.DOWNLOAD_DIR+'/'+final_filename)

    start_time = time.time()
    try:
        await bot.send_document(
                chat_id, 
                progress = progress_bar, 
                progress_args = (
                    'Uploading your File!',
                    sent_msg,
                    start_time
                    ), 
                document = os.path.join(Config.DOWNLOAD_DIR, final_filename),
                caption = final_filename
                )
        text = 'File Successfully Uploaded!\nTotal Time taken : {} seconds'.format(round(time.time()-start_time))
        await sent_msg.edit(text)
    except Exception as e:
        print(e)
        await bot.send_message(chat_id, 'An error occured while uploading the file!\nCheck logs for details of the error!')

    path = Config.DOWNLOAD_DIR+'/'
    os.remove(path+og_sub_filename)
    os.remove(path+og_vid_filename)
    try :
        os.remove(path+final_filename)
    except :
        pass

    db.erase(chat_id)


@Client.on_message(filters.command('hardmux') & filters.private)
async def hardmux(bot, message, cb=False):
    await AddUser(bot, message)
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    me = await bot.get_me()
    
    chat_id = message.from_user.id
    og_vid_filename = db.get_vid_filename(chat_id)
    og_sub_filename = db.get_sub_filename(chat_id)
    text = ''
    if not og_vid_filename :
        text += 'First send a Video File\n'
    if not og_sub_filename :
        text += 'Send a Subtitle File!'
    
    if not (og_sub_filename or og_vid_filename) :
        return await bot.send_message(chat_id, text)
    
    text = 'Your File is Being Hard Subbed. This might take a long time!'
    sent_msg = await bot.send_message(chat_id, text)

    hardmux_filename = await hardmux_vid(og_vid_filename, og_sub_filename, sent_msg)
    
    if not hardmux_filename:
        return
    
    final_filename = db.get_filename(chat_id)
    os.rename(Config.DOWNLOAD_DIR+'/'+hardmux_filename,Config.DOWNLOAD_DIR+'/'+final_filename)
    
    start_time = time.time()
    try:
        await bot.send_video(
                chat_id, 
                progress = progress_bar, 
                progress_args = (
                    'Uploading your File!',
                    sent_msg,
                    start_time
                    ), 
                video = os.path.join(Config.DOWNLOAD_DIR, final_filename),
                caption = final_filename
                )
        text = 'File Successfully Uploaded!\nTotal Time taken : {} seconds'.format(round(time.time()-start_time))
        await sent_msg.edit(text)
    except Exception as e:
        print(e)
        await client.send_message(chat_id, 'An error occured while uploading the file!\nCheck logs for details of the error!')
    
    path = Config.DOWNLOAD_DIR+'/'
    os.remove(path+og_sub_filename)
    os.remove(path+og_vid_filename)
    try :
        os.remove(path+final_filename)
    except :
        pass
    db.erase(chat_id)

