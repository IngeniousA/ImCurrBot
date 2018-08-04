import appsettings
import telebot
import imcurrdata
import os
from pathlib import Path
from flask import Flask, request
bot = telebot.TeleBot(appsettings.token)
server = Flask(__name__)


@bot.message_handler(commands=["info"])
def infomsg(message):
    bot.send_message(message.chat.id, appsettings.info)


@bot.message_handler(commands=["help", "start"])
def getcmdlist(message):
    bot.send_message(message.chat.id, appsettings.start)
    imcurrdata.init(message.chat.id)


@bot.message_handler(content_types=["document"])
def recfile(message):
    fileid = message.document.file_id
    file = bot.get_file(fileid)
    name, ext = os.path.splitext(file.file_path)
    buffer = bot.download_file(file.file_path)
    newname = imcurrdata.randstr(10) + ext
    with open(appsettings.cache + "\\" + newname, 'wb') as new_file:
        new_file.write(buffer)
    imcurrdata.setfile(message.chat.id, newname)
    bot.reply_to(message, "Cool! Now send me the key!\nEnter /start command to cancel")


@bot.message_handler(content_types=["text"])
def keyproc(message):
    if message.text != "/start":
        if imcurrdata.getfile(message.chat.id) != "0":
            if len(message.text) < 5 or len(message.text) > 32:
                bot.reply_to(message, "The key must have from 5 to 32 chars.")
                return
            imcurrdata.setkey(message.chat.id, message.text)
            bot.send_message(message.chat.id, "Processing...")
            resfilename = imcurrdata.launch(message.chat.id)
            bot.send_message(message.chat.id, "Done!")
            res = open(resfilename, 'rb')
            bot.send_document(message.chat.id, res)
            imcurrdata.clear(message.chat.id)


@bot.message_handler(commands=["id"])
def getid(message):
    bot.send_message(message.chat.id, str(message.chat.id))


@server.route('/' + appsettings.token, methods=['POST'])
def getmessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://<DOMAIN>/' + appsettings.token)
    return "!", 200


if __name__ == '__main__':
    cachedir = Path(appsettings.cache)
    if not cachedir.is_dir():
        os.makedirs(appsettings.cache)
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
