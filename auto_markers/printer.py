class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def header_string(prompt):
    return bcolors.HEADER + prompt + bcolors.ENDC


def blue_string(prompt):
    return bcolors.OKBLUE + prompt + bcolors.ENDC


def green_string(prompt):
    return bcolors.OKGREEN + prompt + bcolors.ENDC


def warning_string(prompt):
    return bcolors.WARNING + prompt + bcolors.ENDC


def fail_string(prompt):
    return bcolors.FAIL + prompt + bcolors.ENDC


def bold_string(prompt):
    return bcolors.BOLD + prompt + bcolors.ENDC


def underline_string(prompt):
    return bcolors.UNDERLINE + prompt + bcolors.ENDC
