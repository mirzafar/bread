import traceback

import httpx

from settings import settings

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


async def on_catalog(chat_id: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            await client.post(
                url=f'{settings["tg_api_url"]}/bot{settings["tg_token"]}/sendMediaGroup',
                json={
                    'media': [
                        {
                            'type': 'photo',
                            'media': settings['base_url'] + img
                        } for img in CATALOG_IMAGES
                    ],
                    'chat_id': chat_id
                }
            )
    except (Exception,):
        traceback.print_exc()

    return {
        'method': 'sendMessage',
        'text': CATALOG_TITLE,
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
    }


