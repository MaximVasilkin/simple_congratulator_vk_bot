from random import choice
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin
import io


class BasePostcard:
    """
    Базовый класс для наследования.

    Параметр text_data - словарь с текстовыми данными для создания поздравления.

    Ключи - заголовки абзацев текста (порядок важен).
    Значения - кортеж подходящих абзацев к данному заголовку (порядок не важен).

    Пример:

    {'Поздравляю с': ('праздником', 'этим замечательным днём'),
     'Желаю': ('счастья и радости', 'здоровья и успеха')}
    """

    text_data = {}

    def __init__(self,
                 image_path: str,
                 text_position: tuple[int, int],
                 text_max_size: tuple[int, int],
                 font_path: str,
                 font_color: str | tuple[int, int, int],
                 align: str = 'center',
                 anchor: str = 'mm',
                 font_scale_step: int = 3,
                 font_coefficient: int | float = 1.55):

        """
        :param image_path: путь к изображению, пустому шаблону открытки
        :param text_position: кортеж с координатами в пикселях (X, Y) центра свободного места под текст
        :param text_max_size: разрешение в пикселях свободного места под текст
        :param font_path: путь к файлу шрифта
        :param font_color: желаемый цвет надписи
        :param align: выравнивание по XY
        :param anchor: выравнивание привязки текста
        :param font_scale_step: шаг уменьшения размера шрифта с целью его адаптации.
        Большой шаг ускоряет работу адаптации, но может адаптироваться под свободное место неточно (не впритык)
        :param font_coefficient: коэффициент размера шрифта. Подбирается индивидуально под каждый шрифт.
        """

        self.image_path = image_path
        self.text_position = text_position
        self.text_max_size = text_max_size
        self.max_width, self.max_height = text_max_size
        self.font_path = font_path
        self.font_color = font_color
        self.align = align
        self.anchor = anchor
        self.font_scale_step = font_scale_step
        self.font_coefficient = font_coefficient

    def __enter__(self):
        self.file = io.BytesIO()
        self.create_postcard().save(self.file, format='JPEG')
        self.file.seek(0)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def create_text(self) -> str:
        """
        Метод возвращает случайное поздравление в виде одной строки (на основе данных из self.text_data).
        """
        congratulation = ''
        for k, v in self.text_data.items():
            congratulation += f'{k} {choice(v)}! '
        return congratulation + 'Ура!'

    def adaptive_text(self, text: str, draw: ImageDraw) -> (str, ImageFont):
        """
        Метод адаптивно разбивает текст поздравления на строки и подбирает размер шрифта.

        :param text: текст поздравления в виде одной строки.
        :param draw: объект ImageDraw, созданный на основе объекта Image (шаблона открытки).
        :return: поздравление в виде многострочной строки
        и шрифт, адаптированного размера под свободное место (self.text_max_size).
        """
        font_max_size = int((((self.max_width * self.max_height) // len(text)) ** 0.5) * self.font_coefficient)
        words = text.split(' ')
        while True:
            stringed_text = ''
            font = ImageFont.truetype(self.font_path, font_max_size)
            for word in words:
                word = f'{word} '
                horizontal_start, vertical_start, horizontal_end, vertical_end = draw.multiline_textbbox(
                    (0, 0),
                    stringed_text + word,
                    font=font,
                    anchor=self.anchor,
                    align=self.align,
                )
                width = horizontal_end - horizontal_start
                height = vertical_end - vertical_start

                if height > self.max_height:
                    font_max_size -= self.font_scale_step
                    break
                if width > self.max_width:
                    word = f'\n{word}'
                stringed_text += word
            else:
                return stringed_text, font

    def create_postcard(self) -> JpegImagePlugin.JpegImageFile:
        """
        Метод создаёт открытку со случайным поздравлением:
        Создаёт случайный текст;
        Адаптирует размер текста под картинку-шаблон;
        Добавляет текст на картинку.
        :return: изображение открытки
        """
        text = self.create_text()
        with Image.open(self.image_path) as image:
            draw = ImageDraw.Draw(image)
            text, font = self.adaptive_text(text, draw)
            draw.multiline_text(
                self.text_position,
                text,
                font=font,
                fill=self.font_color,
                anchor=self.anchor,
                align=self.align,
            )
            return image


class NewYearPostCard(BasePostcard):
    text_data = {'С Новым Годом,': ('с новым счастьем',
                                    '365 новых дней. 365 новых шансов',
                                    'наслаждайтесь каждым его моментом',
                                    'примите мои искренние поздравления',
                                    'годом Дракона',
                                    'новый старт начинается сегодня',
                                    'и пусть самые лучшие сюрпризы будут у вас впереди'),

                 'Желаю': ('много новых достижений, крепкого здоровья и любви, пусть задуманное сбудется',
                           'чтобы этот год подарил много поводов для радости и счастливых моментов',
                           'чтобы будущий год принес столько радостей, сколько дней в году, '
                           'и чтобы каждый день дарил вам улыбку и частичку добра',
                           'вам прекрасного года, полного здоровья и благополучия',
                           'чтобы Дракон принёс в вашу семью любовь, мудрость, взаимопонимание и счастье',
                           'всем в Новом году быть здоровыми, красивыми, любимыми и успешными',
                           'чтобы сбылось все то, что вы пожелали. Все цели были достигнуты, '
                           'а планы перевыполнены. Всё плохое и неприятное осталось в уходящем году'),

                 'И пусть': ('Новый год принесёт много радостных и счастливых дней',
                             'каждый новый миг наступающего года приносит в дом '
                             'счастье, везение, уют и теплоту',
                             'всё, что мы планировали, обязательно сбудется',
                             'наступающий год станет самым плодотворным годом в вашей жизни',
                             'год будет полон ярких красок, приятных впечатлений и радостных событий',
                             'этот год будет ВАШИМ годом',
                             'Новый год принесёт всё, о чём вы мечтаете, и немного больше')}


new_year_blue_postcard = NewYearPostCard(image_path='templates/1.jpg',
                                         text_position=(600, 577),
                                         text_max_size=(915, 896),
                                         font_path='fonts/majestic.ttf',
                                         font_color=(0, 0, 0),
                                         anchor='mm',
                                         align='center',
                                         font_scale_step=3,
                                         font_coefficient=1.55)
