from os import getenv
from bot import start_vk_bot


if __name__ == '__main__':
    start_vk_bot(token=getenv('token'),
                 public_id=int(getenv('public_id')))
