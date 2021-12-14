from discord.ext import commands
from os import getenv
import traceback
import discord
import asyncio
import html
import re
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
from google.cloud import texttospeech_v1beta1 as texttospeech

client = discord.Client()
TEXT_CHANNEL_ENV = getenv('TEXT_CHANNEL')
TEXT_CHANNEL_ve = int(TEXT_CHANNEL_ENV)
DND_CHANNEL = 889433349951733770
Text_Channel = 0

# Initial
@client.event
async def on_ready():
    global Voice_State
    print('Login!!!')
    Voice_State = 0

# チャンネル入退室時の通知処理
@client.event
async def on_voice_state_update(member, before, after):

    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botRoom = client.get_channel(TEXT_CHANNEL_ve)

        # 入室通知（画面共有に反応しないように分岐）
        if after.channel is not None and after.channel is not before.channel:
            if before.channel is None:
                if after.channel.id != DND_CHANNEL:
                    await botRoom.send( member.name + " が参加しました！")
        if before.channel is not None and after.channel is None:
            if len(before.channel.members) == 0: 
                await botRoom.send("ボイチャに誰もいなくなりました")

@client.event
async def on_voice_state_update(member, before, after):
    global Voice_State
    if Voice_State == 1 and after.channel is None:
        if member.id != client.user.id:
            if member.guild.voice_client.channel is before.channel:
                if len(member.guild.voice_client.channel.members) == 1:
                    await asyncio.sleep(1)
                    await member.guild.voice_client.disconnect()

# メッセージに反応
@client.event
async def on_message(message):
    global voiceChannel
    global Text_Channel
    global Voice_State

    if message.content == '/connect':
        voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
        await message.channel.send('読み上げBotが参加しました')
        print(message.channel.id)
        Text_Channel = message.channel.id
        Voice_State = 1
        return
    elif message.content == '/disconnect' and message.channel.id == Text_Channel:
        voiceChannel.stop()
        await message.channel.send('読み上げBotが退出しました')
        await voiceChannel.disconnect()
        Voice_State = 0
        return

    if message.channel.id == Text_Channel and message.author != client.user and Voice_State == 1:
        play_voice(message.content)
    else:
        return

def detect_ja(text):
    print(len(text))
    print(text[0])
    for i in range(len(text)):
        if len(re.findall("[亜-熙ぁ-んァ-ヶ]",text[i])) > 0:
             return "ja-JP"
    return "en-US"

# テキストをSSMLを変換する関数
def text_to_ssml(text):
    escaped_lines = html.escape(text)
    ssml = "{}".format(
        escaped_lines.replace("\n", '')
    )
    print(ssml)
    return ssml

# SSMLをGoogle TTS APIに渡してMP3で返す関数
def ssml_to_speech(ssml, file, language_code, wavenet_jpen):
    ttsClient = texttospeech.TextToSpeechClient()
    print(ttsClient)
    print(type(ttsClient))
    for key, value in ttsClient.__dict__.items():
        print(key, ':', value)
    synthesis_input = texttospeech.SynthesisInput(text=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code, name=wavenet_jpen, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=0.9
    )
    response = ttsClient.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(file, "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file " + file)
    return file

#音声ファイルを再生してボイスチャンネルに投げる関数（メイン関数としてまとめてる）
def play_voice(text):
    bl_ja_en = detect_ja(text)
    ssml = text_to_ssml(text)
    if bl_ja_en == "ja-JP":
        file = ssml_to_speech(ssml, "voice.mp3", "ja-JP",'ja-JP-Wavenet-B')
    else:
        file = ssml_to_speech(ssml, "voice.mp3", "en_US",'en-US-Wavenet-C')
    voiceChannel.play(FFmpegPCMAudio(file))

token = getenv('DISCORD_BOT_TOKEN')
client.run(token)