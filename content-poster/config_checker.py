from loggers import events
try:
    import ujson as json
except ImportError:
    events.warning('UJSON not installed, using default JSON library, consider installing it via pip')
    import json
from datetime import datetime
from pytz import all_timezones


def check_config():
    with open('data.json', 'rb') as f:
        try:
            data = json.load(f)
        except ValueError:
            events.critical('[CONFIG] Error parsing config')
            exit()
    if data.get('disable_config_check', False):
        return

    try:
        data['page']
        data['ratings']
        data['token']
        data['chat']
        now = datetime.utcnow()
        last_post_time = now.replace(hour=int(data['post_time'][0].split(':')[0]),
                                     minute=int(data['post_time'][0].split(':')[1]))
        for pt in data['post_time'][1:]:
            pt = now.replace(hour=int(pt.split(':')[0]), minute=int(pt.split(':')[1]))
            if pt < last_post_time:
                last_post_time = last_post_time.strftime('%H:%M')
                pt = pt.strftime('%H:%M')
                events.error(f'[CONFIG] Wrong post time order ({last_post_time} > {pt})')
                exit()
            last_post_time = pt
        if data['timezone'] not in all_timezones:
            events.error(f'[CONFIG] {data["timezone"]} is not a valid timezone')
            exit()

    except KeyError as e:
        events.error(f'[CONFIG] {e.args[0]} not defined')
        exit()
    except TypeError:
        events.error('[CONFIG] Wrong post time format')
        exit()


if __name__ == '__main__':
    check_config()
