import os


def check_whitelist(whitelist_path: str, original: str) -> bool:
    msg = ''
    for c in original.lower():
        if c.isalpha() or c == '-':
            msg += c
        else:
            msg += ' '
    text = msg.split()
    with open(whitelist_path) as whitelist:
        for line in whitelist:
            word = line.strip()
            if word in text:
                return True
    return False


def is_important(msg: str) -> bool:
    prefix = 'whitelists/'
    for wl in os.listdir(prefix):
        try:
            if check_whitelist(prefix + wl, msg):
                return True
        except Exception as e:
            print(f'Error: {e}')
    return False
