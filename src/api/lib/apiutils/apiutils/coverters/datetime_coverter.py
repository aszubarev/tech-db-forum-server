from datetime import datetime


class DatetimeConverter(object):

    @staticmethod
    def to_str_with_z(dt: datetime) -> str:

        utcoffset_str = str(dt.astimezone().utcoffset())
        utcoffset_hour = utcoffset_str.split(':')[0]

        if len(utcoffset_hour) == 1:
            replace_offset_str = f"+0{utcoffset_hour}:00"
        else:
            replace_offset_str = f"+{utcoffset_hour}:00"
        return dt.astimezone().isoformat().replace(replace_offset_str, 'Z')