def rchop(s, ending):
    return s[: -len(ending)] if s.endswith(ending) else s


def lchop(s, beginning):
    return s[len(beginning) :] if s.startswith(beginning) else s


def ordinal_en(n: int):
    # https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
    return f'{n}{"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]}'


def ordinal_fr(n: int):
    if n == 1:
        return "1er"
    return f"{n}è"


def arrival_time_en(time_in_seconds: int):
    if time_in_seconds == 0:
        return "Here"

    time_in_mins = time_in_seconds // 60
    if time_in_mins == 0:
        return ""

    return str(time_in_mins) + (" min" if time_in_mins == 1 else " mins")
