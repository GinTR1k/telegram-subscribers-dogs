from environs import Env

env = Env()
env.read_env()


class Config:
    DEBUG = env.bool('DEBUG', False)
    LOGGER_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    SENTRY_DSN = env('SENTRY_DSN', '')

    with env.prefixed('DATABASE_'):
        DATABASE_URI = env('URI', '') or 'postgres://{user}:{password}@{host}:{port}/{database}'.format(
            user=env('USER'),
            password=env('PASSWORD'),
            host=env('HOST'),
            port=env('PORT', 5432),
            database=env('NAME'),
        )

    with env.prefixed('TELEGRAM_'):
        TELEGRAM_BOT_TOKEN = env('BOT_TOKEN')
        TELEGRAM_OWNERS_USER_IDS = env.list('OWNERS_USER_IDS', [], subcast=int)

    POLLING_CHANNELS_INTERVAL = env.int('POLLING_CHANNELS_INTERVAL', 60 * 5)

    MESSAGE_ONE_DOG_LEFT = 'Какой-то пёс отписался от канала %s'
    MESSAGE_FROM_TWO_TO_FOUR_DOGS_LEFT = '%s пса отписались от канала %s'
    MESSAGE_MANY_DOGS_LEFT = '%s псов отписались от канала %s'
    MESSAGE_ONE_DOG_JOINED = 'Один пёс подписался на канал %s'
    MESSAGE_FROM_TWO_TO_FOUR_DOGS_JOINED = '%s пса подписались на канал %s'
    MESSAGE_MANY_DOGS_JOINED = '%s псов подписались на канал %s'
