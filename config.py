from os import getenv
from dataclasses import dataclass

TOKEN = getenv("TOKEN")


@dataclass
class BotVars:
    auto_mode = False
    last_user: int


BANNED_ACT = (
    "stalcraft",
    "dota",
    "unturned",
    "genshin"
)

LEAVE_PHRASES = (
    "Ливай с позором",
    "Ну и ну! Вы разочаровывать Админ...",
    "Ай ай ай...",
    "Стыдно...",
    "Я всё вижу",
    "Не стыдно?",
    "Мда...",
    "Ууууууу..."
)

FURRY_GIFS = (
    "https://media1.tenor.com/m/OdwnulLcB2QAAAAC/boy-kisser-boykisser.gif",
    "https://media1.tenor.com/m/ApvDbPlv5QQAAAAd/furry-speech-bubble.gif",
    "https://media.tenor.com/B2M6WmpKEbgAAAAi/wypher-wypher-furry.gif",
    "https://media.tenor.com/xfjPfTgUss4AAAAi/%D0%B2%D1%8B%D0%BD%D0%BE%D1%81%D0%BA%D0%B0.gif",
    "https://media1.tenor.com/m/mE8Gx_H9diUAAAAd/felix-re-zero.gif",
    "https://media.tenor.com/7WHr_kslu7YAAAAi/speech-bubble.gif",
    "https://media1.tenor.com/m/sKYL8xJnZ80AAAAC/furry-speech-bubble.gif",
    "https://media1.tenor.com/m/wRoOiqFr_zsAAAAd/speech-bubble.gif",
    "https://media1.tenor.com/m/LCMpd3PhRc4AAAAC/mauzymice-mauzy.gif",
    "https://media1.tenor.com/m/uCBrR1Ftyw8AAAAC/mauzymice-furry.gif",
    "https://media1.tenor.com/m/XfEzqwaKnrAAAAAC/goobysart-speech-bubble.gif",
    "https://media1.tenor.com/m/SRX8X6DNF6QAAAAd/nerd-nerd-emoji.gif",
    "https://media1.tenor.com/m/A10Ds1kmFiYAAAAC/astolfo-bounce.gif",
    "https://media1.tenor.com/m/FMbMWe3KZcoAAAAC/speech-bubble-astolfo.gif",
    "https://media1.tenor.com/m/k0Gd9hRepxIAAAAC/felix-felix-argyle.gif",
    "https://media1.tenor.com/m/Pmpev0kM7cAAAAAd/bubble-chat.gif",
    "https://media1.tenor.com/m/68DCMWIgtoQAAAAC/speech-bubble-spoofity.gif",
    "https://media1.tenor.com/m/eZmpodNvgM0AAAAd/kotodama-honoka-ichinose.gif",
    "https://media1.tenor.com/m/kxGEDdoj_V8AAAAC/speech-bubble.gif",
    "https://media.tenor.com/yc5c_g6nqSQAAAAi/speech-bubble.gif",
    "https://media.tenor.com/wf658iKnCb4AAAAi/boykisser-speech-bubble.gif",
    "https://media1.tenor.com/m/aD2ZpPn0cRoAAAAd/lil-nas-x-nickb.gif",
    "https://media.tenor.com/BQg6GSZlc2cAAAAi/speech-bubble-boykisser.gif",
    "https://media.tenor.com/YriUpNFGHrwAAAAi/british-speech-bubble-union-jack-speech-bubble.gif",
    "https://media1.tenor.com/m/T_aCl5WZuCUAAAAd/typh-speech-bubble.gif",
    "https://media.tenor.com/Ey5SH20te_sAAAAi/astolfo-astolfo-cry.gif",
    "https://media.tenor.com/1t7kwTWdRZwAAAAi/speech-bubble.gif",
    "https://media1.tenor.com/m/pPd2u3Q-5_UAAAAC/dentedhead-speech-bubble.gif",
    "https://media.tenor.com/x3rEyRVF5foAAAAi/femboy.gif",
    "https://media1.tenor.com/m/F7XO6oCD6OYAAAAC/bubble-speech.gif",
    "https://media1.tenor.com/m/38lg308nWwAAAAAd/astolfo.gif",
    "https://media.tenor.com/mvlqHDBxTGIAAAAi/speech-bubble-sticker.gif",
    "https://media.tenor.com/4uoycZ1iHT4AAAAi/sigma-sigma-male.gif",
    "https://media1.tenor.com/m/A9NyR7aOC0AAAAAC/boy-kisser.gif",
    "https://media.tenor.com/J4Vqv0tnx9EAAAAi/boykisser-speechbubble.gif",
    "https://media1.tenor.com/m/A0EQeZSGFGkAAAAd/speech-bubble-spoofity.gif",
    "https://media1.tenor.com/m/ZlBGpo6701gAAAAC/furry-speech-bubble.gif",
    "https://media1.tenor.com/m/uwxBWjdN21AAAAAC/speech-bubble.gif",
    "https://media.tenor.com/CGm6cZhxOD8AAAAi/speech-bubble-angry-birds.gif",
    "https://media.tenor.com/Wvo8PVqcPc8AAAAi/astolfo-speech-bubble.gif",
    "https://media.tenor.com/BZzEyd1L_YkAAAAi/cyware-mushroom.gif",
    "https://media.tenor.com/R6bU6t0XAtwAAAAi/maidcore-text-bubble.gif",
    "https://media1.tenor.com/m/b7mnVHUXvsAAAAAd/speech-bubble-ishowspeed.gif",
    "https://media.tenor.com/VR6a6oiVCrUAAAAi/speech-bubble-text-bubble.gif",
    "https://media.tenor.com/ngvhXt1-2LwAAAAi/speech-bubble-nails.gif",
    "https://media.tenor.com/Yig89b1rWPUAAAAi/kag-game.gif",
    "https://media1.tenor.com/m/_7ETUjaoWTAAAAAC/tinyrockspeechbubble-tiny-rock.gif",
    "https://media.tenor.com/-HiIbXp5-10AAAAi/asuka-evangelion.gif",
    "https://media.tenor.com/hxw80CyON5kAAAAi/dekma-bubble-speech.gif",
    "https://media.tenor.com/EGgaN-eGfi8AAAAi/speech-bubble.gif",
    "https://media.tenor.com/NR0I3ULSvtUAAAAi/speech-bubble.gif",
    "https://media.tenor.com/YYtLdkW9ezAAAAAi/speech-bubble.gif",
    "https://media.tenor.com/1MjnMrderxEAAAAi/speech-bubble-bubble-speech.gif",
    "https://media1.tenor.com/m/hdSN5IoLDtAAAAAd/speech-bubble-discord.gif",
    "https://media.tenor.com/gU9oiJ3hM-IAAAAi/furry-bubble-speech-furry.gif",
    "https://media.tenor.com/Ztn5_pUWuDIAAAAi/speech-bubble-wholesome.gif",
    "https://media.tenor.com/AAIzHtfqhCcAAAAi/necoarc-speech-bubble.gif",
    "https://media.tenor.com/kMfGoKMAu5UAAAAM/femboy-speech-bubble.gif",
    "https://media.tenor.com/X-DsxqW6spIAAAAM/omega-kerfus-kerfus.gif",
    "https://media.tenor.com/R7ngRxy3HxQAAAAM/%D0%B1%D0%B0%D0%B1%D0%BB-%D1%81%D0%BF%D0%B8%D1%87-%D1%80%D0%BE%D0%B1%D0%BB%D0%BE%D0%BA%D1%81.gif",
    "https://media.discordapp.net/attachments/1246098340320383026/1246101514217459773/9012542136709979816.gif?ex=66ed8078&is=66ec2ef8&hm=dfc0e0d9d6925d300331ee64cef24e8512303a8738c0a413287cbc1e66e484ea&="
)

EMOJIS = (
    "✖️",
    "❌",
    "❎"
)

GENA = "https://media1.tenor.com/m/lqpA3Xs8rxMAAAAd/%D0%B1%D0%B0%D1%80%D0%B1%D0%BE%D1%81%D0%BA%D0%B8%D0%BD%D1%8B-%D0%B5%D0%B4%D0%B0.gif"

STALCRAFT_FACE = "https://tenor.com/view/stalcraft-%D1%81%D0%BD%D1%8E%D1%81-minecraft-gif-19986730"

HELP = """Каждый день в 17:00 всем выдаётся 
1 попытка увеличить свой писюн. Для этого
нужно использовать команду !dick. Рандом
выдаёт числа от -5 до 10 см. За запуск
Доты, Unturned и т.д. твой писюн
уменьшается на 3 см.

Команды:
!dick - изменяет размер писюна
!attempts - выводит количество попыток
!stats - выводит глобальный топ игроков
!stalcraft - скидывает лицо из сталкрафта
!auto on/off - включает режим автоматической
ответки на гифки и картинки (выключить может 
только тот, кто включил или сам отключается
через 30 минут)
!furry - скидывает furry talking гифку
(также срабатывает если поставить на любое
сообщение '❎', '❌' или '✖️')

Алиасы:
!dick - penis, d, p
!attempts - a, att, atts, try, tries
!stats - top, stat
!stalcraft - sc, face
!furry - f, t, talk, talking"""
