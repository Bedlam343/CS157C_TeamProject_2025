def print_error(msg):
  print(f"\033[31m{msg}\033[0m")

def print_success(msg):
  print(f"\033[32m{msg}\033[0m")

def blue_text(text):
  return f"\033[34m{text}\033[0m"

def bold_text(text):
  return f"\033[1m{text}\033[0m"

def bold_underline(text):
  return "\033[1m\033[4m" + text +  "\033[0m"