from discord.ext import commands
from os import getenv
import traceback
import discord
import html
import re
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
from google.cloud import texttospeech_v1beta1 as texttospeech

client = discord.Client()
Text_Channel = 0

# Initial
@client.event
async def on_ready():
    global Voice_State
    print('Login!!!')
    Voice_State = 0

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
    if message.author.id != 718763604110999572:
        if bl_ja_en == "ja-JP":
            file = ssml_to_speech(ssml, "voice.mp3", "ja-JP",'ja-JP-Wavenet-B')
        else:
            file = ssml_to_speech(ssml, "voice.mp3", "en_US",'en-US-Wavenet-C')
    voiceChannel.play(FFmpegPCMAudio(file))

token = getenv('DISCORD_BOT_TOKEN')
client.run(token)