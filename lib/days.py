import datetime
import pytz
from dateutil import relativedelta

tz = pytz.timezone('Asia/Shanghai')


def get_now():
    return datetime.datetime.now(tz=tz)


def get_now_str(fmt='%Y-%m-%d %H:%M:%S'):
    return get_now().strftime(fmt)


def get_now_packstr(fmt='%Y%m%d%H%M%S'):
    return get_now_str(fmt=fmt)


def get_today():
    return get_now().date()


def get_today_str(fmt='%Y-%m-%d'):
    return get_today().strftime(fmt)


def get_today_packstr(fmt='%Y%m%d'):
    return get_today_str(fmt=fmt)


def get_first_day_of_month():
    now = get_now()
    first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return first_day


def get_first_day_of_last_month():
    first_day = get_first_day_of_month()
    return first_day - relativedelta.relativedelta(months=1)


def get_first_day_of_next_month():
    first_day = get_first_day_of_month()
    return first_day + relativedelta.relativedelta(months=1)


def get_last_day_of_month():
    first_day_next_month = get_first_day_of_next_month()
    return first_day_next_month - relativedelta.relativedelta(days=1)


def get_last_day_of_last_month():
    first_day = get_first_day_of_month()
    return first_day - relativedelta.relativedelta(days=1)


get_last_month = get_first_day_of_last_month


def get_delta_day(days=0):
    now = get_now()
    delta = now + relativedelta.relativedelta(days=days)
    return delta


def get_delta_date(*args, **kwargs):
    now = get_now()
    delta = now + relativedelta.relativedelta(*args, **kwargs)
    return delta


def get_day(string=None):
    if string is None:
        return get_today()
    if isinstance(string, str):
        return datetime.datetime.strptime(string, '%Y-%m-%d')
    return string


def get_month(string=None):
    if string is None:
        return get_first_day_of_month()
    if isinstance(string, str):
        return datetime.datetime.strptime(string, '%Y-%m')
    return string


def is_same_year(date1, date2):
    return date1.year == date2.year


def is_same_month(date1, date2):
    return date1.year == date2.year and \
           date1.month == date2.month


def is_same_day(date1, date2):
    return date1.year == date2.year and \
           date1.month == date2.month and \
           date1.day == date2.day


if __name__ == '__main__':
    pass
