#!/usr/bin/env python
import os
from six.moves import cPickle
import argparse
import time
import datetime
import logging
parser = argparse.ArgumentParser(description='Coom')
parser.add_argument('--log_level',dest='log_level', type=int, nargs='?', choices=[logging.NOTSET,logging.DEBUG,logging.INFO,logging.WARNING,logging.ERROR,logging.CRITICAL],
                   help='Determine log level Debug = 10 & CRITICAL = 50  [default=30]')
args = parser.parse_args()

from six import text_type

import tensorflow as tf
with open(os.path.join("save", 'config.pkl'), 'rb') as f:
    saved_args = cPickle.load(f)
with open(os.path.join("save", 'chars_vocab.pkl'), 'rb') as f:
    chars, vocab = cPickle.load(f)
from model import Model
model = Model(saved_args, training=False)
sess = tf.Session()
tf.global_variables_initializer().run(session=sess)
saver = tf.train.Saver(tf.global_variables())
ckpt = tf.train.get_checkpoint_state("save")
saver.restore(sess, ckpt.model_checkpoint_path)

def sample(prime):
        if prime == '':
                prime = chars[0]
        data = model.sample(sess, chars, vocab, 150, prime,
                               1).encode('utf-8')
        return data.decode("utf-8")




# bruhbot.py
import discord
from dotenv import load_dotenv
load_dotenv()
global startime
global homechannels
global automodes
global counters
startime = datetime.datetime.now()
TOKEN = os.getenv('DISCORD_TOKEN')
SUPERUSER = int(os.getenv('DISCORD_USER'))
client = discord.Client()

logging.basicConfig(filename=startime.strftime("logs/%Y-%m-%d_%H:%M:%S.log"),level=args.log_level)
logging.info("started at: "+startime.strftime("%Y-%m-%d[%H:%M:%S]"))

def make_message(prime):
    answer = sample(prime)
    answa = answer.split('\n')
    for i in answa :
        if(len(i.split(",")) == 3):
            answer = i
            break
    answa = answer.split(",")
    answer = answa[0][1:-1]+ " said: "
    if '#' not in answer or '\n' in answer:
        return
    answad = answa[2][1:].split(':')
    if len(''.join(answad)) < 2:
        return
    answer += ''.join(answad)
    logging.debug(answer)
    return answer

@client.event
async def on_ready():
    global homechannels #idk how
    global automodes #global vars work
    global counters #sue me
    for guild in client.guilds:
        logging.info("connected to:"+guild.name+', '+str(guild.id)+"\n")
    homechannels = [None] * len(client.guilds)
    automodes = [False] * len(homechannels)
    counters = [0] * len(homechannels)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!elf"):
        while(True):
            answer = make_message(message.content[4:])
            if answer != None :
                break
        await message.channel.send(answer)
        return
    if message.content == "elf!calibrate" and (message.author.id == SUPERUSER or message.author.permissions_in(message.channel).manage_messages):
        homechannels[client.guilds.index(message.guild)] = message.channel
        automodes[client.guilds.index(message.guild)] = True
        await message.channel.send("```Glasses:On\nPants:Off\nYep, it's gamer time.```")
    if message.content == "elf!automode" and ( message.author.id == SUPERUSER or message.author.permissions_in(message.channel).manage_messages):
        if automodes[homechannels.index(message.channel)]==True :
            automodes[homechannels.index(message.channel)] = False
            await message.channel.send('Barbecue Shoes: Off')
        else :
            automodes[homechannels.index(message.channel)] = True
            await message.channel.send('Barbecue Shoes: On')
    if True : #too fucking lazy to remove the tabs here fuck you dipshits
        if message.channel in homechannels and automodes[homechannels.index(message.channel)]:
            if counters[homechannels.index(message.channel)]==7:
                answer = make_message(message.content)
                await message.channel.send(answer)
                counters[homechannels.index(message.channel)] = 0
            else:
                counters[homechannels.index(message.channel)]+=1
    if message.content.startswith("elf!echo") and message.author.id == SUPERUSER:
        logging.info("echoed :"+message.content[9:])
        for i in homechannels :
            if i != None :
                await i.send(message.content[9:])
    if message.content.startswith("elf!uptime"):
        uptime = time.gmtime((datetime.datetime.now()-startime).total_seconds())
        logging.info("uptime called for "+time.strftime("%H:%M",uptime))
        await message.channel.send(time.strftime("```up for %H hours %M minutes```",uptime))
    if message.content.startswith("elf!sleeptime") and message.author.id == SUPERUSER:
        logging.info('shut down normally at '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        await message.channel.send('***AAAAAAAAAA THE PAIN NOOOOOOOOOOOOOOOOOOOOOOOOOOO AAAAAAAAA***')
        time.sleep(2)
        await message.channel.send("ok I'll go to bed mom")
        quit()
client.run(TOKEN)
