import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from time import sleep
from requests.exceptions import ReadTimeout
from socket import timeout
from urllib3.exceptions import ReadTimeoutError
from create_postcard import new_year_blue_postcard
from keyboards import keyboard_get_postcard


class VkBot:
    def __init__(self, token: str, public_id: int):
        self.bot = vk_api.VkApi(token=token, api_version='5.199')
        self.upload = vk_api.VkUpload(self.bot)
        self.public_id = public_id

    def write_msg(self, user_id, message='', attachment='', keyboard=''):
        self.bot.method('messages.send', {'user_id': str(user_id),
                                          'message': message,
                                          'attachment': attachment,
                                          'keyboard': keyboard,
                                          'random_id': 0
                                          })

    def start_polling(self):
        long_poll = VkBotLongPoll(self.bot, self.public_id)
        while True:
            try:
                for event in long_poll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        message = event.message
                        peer_id = message['peer_id']

                        with new_year_blue_postcard as f:
                            result = self.upload.photo_messages(f, peer_id)[0]

                        attachment = f"photo{result['owner_id']}_{result['id']}_{result['access_key']}"
                        self.write_msg(peer_id, attachment=attachment, keyboard=keyboard_get_postcard)

            except (ReadTimeout, timeout, ReadTimeoutError):
                sleep(1)


def start_vk_bot(token: str, public_id: int):
    bot = VkBot(token, public_id)
    bot.start_polling()
