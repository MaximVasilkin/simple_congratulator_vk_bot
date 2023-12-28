import io
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from time import sleep
from requests.exceptions import ReadTimeout
from socket import timeout
from urllib3.exceptions import ReadTimeoutError
from postcard import new_year_blue_postcard
from keyboards import keyboard_get_postcard
from redis_db import redis_storage
import logging
from statuses import ResultStatus


def logging_decorator(old_func):
    def new_func(*args, **kwargs):
        try:
            return old_func(*args, **kwargs), ResultStatus.ok
        except Exception as error:
            message = f'\nОшибка в функции/методе {old_func.__name__} \n ' \
                      f'args: {str(args)} \n kwargs: {str(kwargs)}\n'

            logging.exception(str(error) + message)
            return None, ResultStatus.error
    return new_func


class VkBot:
    def __init__(self, token: str, public_id: int):
        logging.basicConfig(level=logging.WARNING,
                            filename='vk_bot.log',
                            format='\n\n%(asctime)s %(levelname)s %(message)s',
                            filemode='a')

        self.bot = vk_api.VkApi(token=token, api_version='5.199')
        self.upload = vk_api.VkUpload(self.bot)
        self.public_id = public_id

    @logging_decorator
    def send_message(self, user_id, message='', attachment='', keyboard=''):
        self.bot.method('messages.send', {'user_id': str(user_id),
                                          'message': message,
                                          'attachment': attachment,
                                          'keyboard': keyboard,
                                          'random_id': 0
                                          })

    @logging_decorator
    def get_image_link(self, text_hash):
        return redis_storage.get(text_hash)

    @logging_decorator
    def add_image_link(self, text_hash, link):
        return redis_storage.set(text_hash, link)

    @logging_decorator
    def create_and_upload_image(self, peer_id, postcard, text, text_hash):
        with io.BytesIO() as file:
            postcard.create_postcard(text).save(file, format='JPEG')
            file.seek(0)
            result = self.upload.photo_messages(file, peer_id)[0]
        link = f"photo{result['owner_id']}_{result['id']}_{result['access_key']}"
        #  благодаря декоратору, данный метод в случае ошибки не поднимет исключение. Просто не добавит запись в БД
        self.add_image_link(text_hash, link)
        # ссылка вернётся, даже если её не удалось добавить в БД
        return link

    def get_or_create_postcard(self, peer_id, postcard):
        random_congratulation,  hash_congratulation = new_year_blue_postcard.create_text()
        image_link, status = self.get_image_link(hash_congratulation)
        # при неполадке с БД возвращаем None, не пытаясь выгрузить картинку в интернет
        if status == ResultStatus.error:
            return
        return image_link or self.create_and_upload_image(peer_id=peer_id,
                                                          postcard=postcard,
                                                          text=random_congratulation,
                                                          text_hash=hash_congratulation)[0]

    def send_postcard(self, peer_id, postcard, message=''):
        link = self.get_or_create_postcard(peer_id, postcard)
        if not link:
            link = ''
            message = 'Небольшие сетевые неполадки &#128030;. ' \
                      'Пожалуйста, повторите попытку &#129303;'
        self.send_message(user_id=peer_id, message=message, attachment=link, keyboard=keyboard_get_postcard)

    def start_polling(self):
        long_poll = VkBotLongPoll(self.bot, self.public_id)
        while True:
            try:
                for event in long_poll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        message = event.message
                        peer_id = message['peer_id']
                        self.send_postcard(peer_id, new_year_blue_postcard)

            except (ReadTimeout, timeout, ReadTimeoutError):
                sleep(15)


def start_vk_bot(token: str, public_id: int):
    bot = VkBot(token, public_id)
    bot.start_polling()
