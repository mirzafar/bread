import ujson
from sanic import response
from sanic.views import HTTPMethodView

from core import i18n
from core.cache import cache
from data.catalog import on_catalog

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

# callback = {
#     'update_id': 238283914,
#     'callback_query': {
#         'id': '3015754537387908053',
#         'from': {
#             'id': 702160070, 'is_bot': False,
#             'first_name': 'Mirzafar', 'username': 'm1rzafar',
#             'language_code': 'en'},
#         'message': {'message_id': 94,
#                     'from': {
#                         'id': 7166723089,
#                         'is_bot': True,
#                         'first_name': 'ХлебоДоставка',
#                         'username': 'Bread_delivery_bot'},
#                     'chat': {
#                         'id': 702160070,
#                         'first_name': 'Mirzafar',
#                         'username': 'm1rzafar',
#                         'type': 'private'},
#                     'date': 1747586030,
#                     'text': 'Карзинка пусто. Для добавление товара нажмите кнопку "✅Bыбрать продукт"',
#                     'reply_markup': {
#                         'inline_keyboard': [
#                             [{
#                                 'text': '✅Bыбрать продукт',
#                                 'callback_data': 'chooseGoods'}]]}},
#         'chat_instance': '-8321419619944981968', 'data': 'chooseGoods'}}

CATALOGS = [
    {'id': 1, 'title': 'Хлеб из зеленой гречки без мед'},
    {'id': 2, 'title': 'Хлеб из зеленой гречки с мед (кунжут или семечки можно в комментарии)'},
    {'id': 3, 'title': 'Хлеб из пророшенной пшеницы без мед'},
    {'id': 4, 'title': 'Хлеб Бионан из пророщенной пшеницы с мед (кунжут или семечки можно в комментарии)'},
]


class TelegramWebhookView(HTTPMethodView):
    async def post(self, request):
        data = request.json or {}
        print(f'TelegramWebhookView.post: {data}')

        message = data.get('message')
        callback_data = data.get('callback_query', {}).get('data')

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

        if not text or not callback_data:
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': i18n.PLEASE_WRITE
            })

        if text.startswith('\u2063'):
            return response.json(await on_catalog(chat_id))

        if text.startswith('\u2062'):
            basket = await cache.get(f'chatbot:bread:{chat_id}:basket')
            if basket:
                basket = ujson.loads(basket)

            inline_keyboard = [[{'text': '✅Bыбрать продукт', 'callback_data': 'chooseGoods'}]]
            if basket:
                response_text = 'Товары в корзине:\n\n'
                inline_keyboard.append([{'text': '🗑Очистить карзинку', 'callback_data': 'clearBasket'}])
                for g in basket['goods']:
                    response_text += f'{g["title"]}: {g["count"]}\n'
            else:
                response_text = 'Карзинка пусто. Для добавление товара нажмите кнопку "✅Bыбрать продукт"'

            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': response_text,
                'reply_markup': {
                    'inline_keyboard': inline_keyboard
                }
            })

        if callback_data and callback_data == 'chooseGoods':
            print('--->>')
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': 'Выберите',
                'reply_markup': {
                    'inline_keyboard': [
                        [{'text': c['title'], 'callback_data': f'selectedGood:{c["id"]}'}] for c in CATALOGS
                    ]
                }
            })

        return response.json({})
