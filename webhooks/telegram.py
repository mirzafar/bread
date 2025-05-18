from sanic import response
from sanic.views import HTTPMethodView

from core import i18n
from settings import settings

# data = {
#     'update_id': 929199204,
#     'message': {
#         'message_id': 136300,
#         'from': {'id': 702160070, 'is_bot': False, 'first_name': 'Mirzafar',
#                  'username': 'm1rzafar', 'language_code': 'en'},
#         'chat': {'id': 702160070, 'first_name': 'Mirzafar', 'username': 'm1rzafar',
#                  'type': 'private'}, 'date': 1747564438, 'text': 'dawd'
#     }
# }
CATALOG_TITLE = (f'1) Хлеб из зеленой гречки без мед\n'
                 f'2) Хлеб из зеленой гречки с мед (кунжут или семечки можно в комментарии)\n'
                 f'3) Хлеб из пророшенной пшеницы без мед\n'
                 f'4) Хлеб Бионан из пророщенной пшеницы с мед (кунжут или семечки можно в комментарии)')

CATALOG_IMAGES = [
    '/static/images/pic1.jpg',
    '/static/images/pic2.jpeg',
    '/static/images/pic3.jpg',
    '/static/images/pic4.jpeg'
]


class TelegramWebhookView(HTTPMethodView):
    async def post(self, request):
        data = request.json or {}
        print(f'TelegramWebhookView.post: {data}')

        message = data.get('message')

        if message and message.get('chat', {}).get('type') == 'private':
            pass
        else:
            return response.json({})

        text, chat_id = None, None

        if message:
            chat_id = message.get('chat', {}).get('id')

        if message and message.get('text') == '/start':
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': i18n.GREETING_BOT,
                'reply_markup': {
                    'keyboard': [
                        ['\u2063📔Каталог'],
                        ['\u2062📦Заказать'],
                        ['\u2062🗃Мои заказы'],
                    ],
                    'resize_keyboard': True,
                    'one_time_keyboard': True,
                    'selective': True
                }
            })

        if message and message.get('text'):
            text = message['text']

        elif message and message.get('caption'):
            text = message['caption']

        if not text:
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': i18n.PLEASE_WRITE
            })

        if text.startswith('\u2063'):
            return response.json({
                'method': 'sendMediaGroup',
                'media': [
                    {
                        'type': 'photo',
                        'media': settings['base_url'] + img,
                        'caption': CATALOG_TITLE,
                        'parse_mode': 'HTML'
                    } for img in CATALOG_IMAGES
                ],
                'chat_id': chat_id,
                'reply_markup': {
                    'keyboard': [
                        ['\u2063📔Каталог'],
                        ['\u2062📦Заказать'],
                        ['\u2062🗃Мои заказы'],
                    ],
                    'resize_keyboard': True,
                    'one_time_keyboard': True,
                    'selective': True
                }
            })

        return response.json({})
