import datetime


def convert_ig_date(date_str):
    # possible formats:
    # 2023-10-19T13:30:33.565 (23)
    # 2023-10-31T15:57:48.39 (22)
    # 2023-10-19T13:30:33 (19)
    # PROBLEM: Unexpected format for IG date: 2023-10-31T15:57:48.39. Returning now
    try:
        if len(date_str) >= 19:
            return datetime.datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
    except:
        print(f"PROBLEM: Unexpected format for IG date: {date_str}. Returning now")
        return datetime.datetime.now()
