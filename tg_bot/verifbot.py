from pyrogram import Client
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)
from pyrogram.enums import ParseMode
from pyrogram import filters
import localization
from secrets import choice
import os
import requests


class Answers:
    def __init__(self):
        self.promptOne = None
        self.promptTwo = None
        self.promptThree = None
        self.promptFour = ""
        self.promptFive = None

    def serialize(self):
        data = {
            "promptOne": self.promptOne,
            "promptTwo": self.promptTwo,
            "promptThree": self.promptThree,
            "promptFour": self.promptFour,
            "promptFive": self.promptFive
        }
        return data


class State:
    def __init__(self, lang="en"):
        self.loc: localization.Localization = localization.Localization(lang)
        self.prompt = 0
        self.custom_user = None
        self.answers = Answers()
        self.custom_message = False
        self.pk = None
        self.started = False


USERS: dict[int, State] = {}
SENTENCES = [
    "Mr. Choco is going to visit his friend",
    "Who knows why and why",
    "The strongest group in Telegram",
    "You're The Best",
    "love",
    "Waiting to join you",
    "What a verification bot come on",
    "Abundant livelihood"
]
ADMINS = [5733045846, 1674341520, 867531681]
CONFIRMED = set()
if os.environ.get("DYNO"):
    BASEURL = ""
else:
    BASEURL = "http://127.0.0.1:8000/payment/{}"
client = Client(
    "botter",
    api_id=1,
    api_hash="b6b154c3707471f5339bd661645ed3d6",
    bot_token="5919985885:AAEdWkjQBIAmZsesvrgXKxbAMLOieMQxXOM"
)


@client.on_message(filters=filters.command(["start"]))
def start(client: Client, message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or ""
    loc = message.from_user.language_code
    print(f"Received /start from {user_id} :: {name} :: {username} :: loc=={loc}")
    state = State()
    state.started = True
    USERS[user_id] = state
    keyboard = [
        [InlineKeyboardButton(state.loc.get("okbutton"), callback_data="ok")]
    ]
    message.reply_text(
        state.loc.get("user_welcome"),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN
    )


@client.on_message(filters=filters.command(["en", "heb"]))
def handler(client: Client, message: Message):
    user_id = message.from_user.id
    state = USERS.get(user_id)
    if not state:
        if "en" in message.text:
            state = State()
        else:
            state = State("heb")
        USERS[user_id] = state
    else:
        state.loc = localization.Localization(message.text)


@client.on_callback_query()
def handler(client: Client, query: CallbackQuery):
    query.answer()
    user_id = query.from_user.id
    state = USERS.get(user_id)
    if not state:
        state = State()
        USERS[user_id] = state
    if not state.started and query.data not in ["note_custom", "note_diss", "note_approve"] and "verif" not in query.data:
        query.message.reply_text(
            state.loc.get("startPrompt")
        )
        return
    if query.data == "ok":
        sentence = choice(SENTENCES)
        query.edit_message_text(
            state.loc.get("promptOne").format(sentence=sentence),
            parse_mode=ParseMode.MARKDOWN
        )
        state.prompt = 1
    elif query.data == "skip":
        query.edit_message_text(
            state.loc.get("textPrompt")
        )
        state.prompt = 4
    elif "verif" in query.data:
        info = query.data.split("_")
        by = info[2]
        pk = int(info[1])
        state.pk = pk
        url = BASEURL.format(f"verif/{pk}/")
        data = requests.get(url).json()["data"]
        if not data:
            query.edit_message_text(
                state.loc.get("datanotfound")
            )
            return
        if pk in CONFIRMED:
            query.edit_message_text(
                state.loc.get("alreadyconf")
            )
            return
        query.edit_message_text(
            state.loc.get("verifinfo"),
            parse_mode=ParseMode.MARKDOWN
        )
        query.message.reply_photo(
            photo=data["photo1"]
        )
        query.message.reply_video(
            video=data["video"]
        )
        query.message.reply_photo(
            photo=data["photo2"]
        )
        if data["link"]:
            query.message.reply_text(
                data["link"]
            )
        query.message.reply_text(
            data["text"]
        )
        buttons = [
            [
                InlineKeyboardButton(state.loc.get("optionone"), callback_data="note_approve"),
                InlineKeyboardButton(state.loc.get("optiontwo"), callback_data="note_diss")
            ],
            [
                InlineKeyboardButton(state.loc.get("custommsg"), callback_data="note_custom")
            ]
        ]
        query.message.reply_text(
            state.loc.get("optionselect"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        state.custom_user = int(by)
    elif "note" in query.data:
        tostate = USERS.get(state.custom_user)
        if not tostate:
            tostate = State()
        try:
            if state.pk in CONFIRMED:
                query.edit_message_text(
                    state.loc.get("alreadyconf")
                )
                return
            if query.data == "note_approve":
                client.send_message(
                    state.custom_user,
                    tostate.loc.get("approvenote")
                )
                CONFIRMED.add(state.pk)
            elif query.data == "note_diss":
                client.send_message(
                    state.custom_user,
                    tostate.loc.get("dissnote")
                )
                CONFIRMED.add(state.pk)
            elif query.data == "note_custom":
                query.edit_message_text(
                    state.loc.get("noteprompt")
                )
                state.custom_message = True
        except Exception as e:
            print(f"Error sending note to {state.custom_user}. Reason: {e}")
            query.edit_message_text(
                state.loc.get("notificationfailed")
            )
        if "custom" not in query.data:
            query.edit_message_text(
                state.loc.get("usernotified")
            )


@client.on_message()
def handler(client: Client, message: Message):
    user_id = message.from_user.id
    state = USERS.get(user_id)
    if not state:
        state = State()
        message.reply_text(
            state.loc.get("startPrompt")
        )
        return
    if state.custom_message:
        if state.pk in CONFIRMED:
            query.edit_message_text(
                state.loc.get("alreadyconf")
            )
            state.custom_message = False
            return
        if not (text := message.text):
            message.reply_text(
                state.loc.get("textWarn")
            )
            return
        client.send_message(
            state.custom_user,
            text
        )
        state.custom_message = False
        message.reply_text(
            state.loc.get("usernotified")
        )
        return
    if state.prompt == 1:
        if not (photo := message.photo):
            message.reply_text(
                state.loc.get("repromptPhoto")
            )
            return
        state.answers.promptOne = photo.file_id

        message.reply_text(
            state.loc.get("videoprompt"),
            parse_mode=ParseMode.MARKDOWN
        )
        state.prompt = 2
        return
    elif state.prompt == 2:
        if not (video := message.video):
            message.reply_text(
                state.loc.get("repromptVideo")
            )
            return
        state.answers.promptTwo = video.file_id

        message.reply_text(
            state.loc.get("promptTwo"),
            parse_mode=ParseMode.MARKDOWN
        )
        state.prompt = 3
        return
    elif state.prompt == 3:
        skipbutton = [[InlineKeyboardButton(state.loc.get("menu_skip"), callback_data="skip")]]
        if not (photo := message.photo):
            message.reply_text(
                state.loc.get("repromptPhoto")
            )
            return
        state.answers.promptThree = photo.file_id
        message.reply_text(
            state.loc.get("promptThree"),
            reply_markup=InlineKeyboardMarkup(skipbutton)
        )
        state.prompt = 4
    elif state.prompt == 4:
        skipbutton = [[InlineKeyboardButton(state.loc.get("menu_skip"), callback_data="skip")]]
        if not (link := message.text):
            message.reply_text(
                state.loc.get("linkwarn"),
                reply_markup=InlineKeyboardMarkup(skipbutton)
            )
            return
        state.answers.promptFour = link
        message.reply_text(
            state.loc.get("textPrompt")
        )
        state.prompt = 5
    elif state.prompt == 5:
        if not (text := message.text):
            message.reply_text(
                state.loc.get("textWarn")
            )
            return
        state.answers.promptFive = text
        url = BASEURL.format("verifadd/")
        data = state.answers.serialize()
        res = requests.post(url, data=data).json()["id"]
        button = [[InlineKeyboardButton(state.loc.get("check"), callback_data=f"verif_{res}_{user_id}")]]
        message.reply_text(
            state.loc.get("thanks")
        )
        old = state
        state = State()
        state.loc = old.loc
        USERS[user_id] = state
        for admin in ADMINS:
            state = USERS.get(admin)
            if not state:
                state = State()
                USERS[admin] = state
            try:
                client.send_message(
                    admin,
                    state.loc.get("newverifinfo"),
                    reply_markup=InlineKeyboardMarkup(button)
                )
            except Exception as e:
                print(f"Error while sending info to {admin}. Reason: {e}")


client.run()
