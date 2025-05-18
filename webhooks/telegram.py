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

CATALOGS_BY_ID = {
    1: {'id': 1, 'title': 'Хлеб из зеленой гречки без мед'},
    2: {'id': 2, 'title': 'Хлеб из зеленой гречки с мед (кунжут или семечки можно в комментарии)'},
    3: {'id': 3, 'title': 'Хлеб из пророшенной пшеницы без мед'},
    4: {'id': 4, 'title': 'Хлеб Бионан из пророщенной пшеницы с мед (кунжут или семечки можно в комментарии)'},
}


class TelegramWebhookView(HTTPMethodView):
    async def post(self, request):
        data = request.json or {}
        print(f'TelegramWebhookView.post: {data}')

        message = data.get('message')
        callback_data = data.get('callback_query', {}).get('data')

        text, chat_id = None, None

        if message:
            chat_id = message.get('chat', {}).get('id')
        elif data.get('callback_query', {}).get('message', {}).get('chat', {}).get('id'):
            chat_id = data['callback_query']['message']['chat']['id']

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

        if not text and not callback_data:
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': i18n.PLEASE_WRITE
            })

        if good_id := await cache.get(f'bread:selectGood:{chat_id}'):
            if text and text.isdigit():
                basket = await cache.get(f'chatbot:bread:{chat_id}:basket')
                selected_goods = []
                if basket:
                    basket = ujson.loads(basket)
                    selected_goods = basket['goods']

                good = CATALOGS_BY_ID[int(good_id)]
                selected_goods.append({'title': good['title'], 'count': int(text)})

                inline_keyboard = [[{'text': '✅Bыбрать продукт', 'callback_data': 'chooseGoods'}],
                                   [{'text': '🗑Очистить карзинку', 'callback_data': 'clearBasket'}]]

                response_text = 'Товары в корзине:\n\n'
                for g in selected_goods:
                    response_text += f'{g["title"]}: {g["count"]}\n'

                await cache.delete(f'bread:selectGood:{chat_id}')

                return response.json({
                    'method': 'sendMessage',
                    'chat_id': chat_id,
                    'text': response_text,
                    'reply_markup': {
                        'inline_keyboard': inline_keyboard
                    }
                })

            else:
                return response.json({
                    'method': 'sendMessage',
                    'chat_id': chat_id,
                    'text': 'Напишите количество'
                })

        if text and text.startswith('\u2063'):
            return response.json(await on_catalog(chat_id))

        if text and text.startswith('\u2062'):
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
            return response.json({
                'method': 'editMessageText',
                'message_id': data.get('callback_query', {}).get('message', {}).get('message_id') or None,
                'chat_id': chat_id,
                'text': 'Выберите товар',
                'reply_markup': {
                    'inline_keyboard': [
                        [{'text': c['title'], 'callback_data': f'selectGood:{c["id"]}'}] for c in CATALOGS
                    ]
                }
            })
        elif callback_data and callback_data.startswith('selectGood'):
            await cache.set(f'bread:selectGood:{chat_id}', callback_data.split(':')[1])
            return response.json({
                'method': 'sendMessage',
                'chat_id': chat_id,
                'text': 'Напишите количество'
            })

        return response.json({})
