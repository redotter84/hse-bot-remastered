def check_whitelist(whitelist_path: str, msg: str) -> bool:
    msg = msg.lower()
    with open(whitelist_path) as whitelist:
        for line in whitelist:
            word = line.strip()
            if word in msg:
                return True
    return False


def is_important(msg: str) -> bool:
    whitelists = ['whitelists/urls.txt', 'whitelists/hw.txt', 'whitelists/test.txt', 'whitelists/important.txt']
    for wl in whitelists:
        if check_whitelist(wl, msg):
            return True
    return False

