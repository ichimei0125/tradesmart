from datetime import datetime

def datetime_to_str(date:datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')