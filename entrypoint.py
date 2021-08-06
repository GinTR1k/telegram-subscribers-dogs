import asyncio

from app.app import App

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = App()

    try:
        loop.run_until_complete(app.start())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        app.logger.exception(e)
    finally:
        loop.run_until_complete(app.stop())
