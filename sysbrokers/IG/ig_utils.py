import datetime


def convert_ig_date(date_str):
    # possible formats:
    # 2023-10-19T13:30:33.565
    # 2023-10-19T13:30:33
    try:
        if len(date_str) == 23:
            return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except:
        print(f"PROBLEM: Unexpected format for IG date: {date_str}. Returning now")
        return datetime.datetime.now()
