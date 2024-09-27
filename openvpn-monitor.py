import time
import requests
import json

# 企业微信机器人webhook地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXX"

def read_status_file(filename):
    clients = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("CLIENT_LIST"):
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    clients[parts[1]] = parts[2]
    return clients

def send_webhook(message):
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        }
    }
    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print(f"Failed to send webhook: {response.text}")

def monitor_openvpn_status(filename):
    previous_clients = {}
    while True:
        current_clients = read_status_file(filename)
        
        # 检查新登录的用户
        for client, ip in current_clients.items():
            if client not in previous_clients:
                message = f"{client} 已登录 OpenVPN。登录IP: {ip}"
                send_webhook(message)
        
        # 检查登出的用户
        for client in previous_clients:
            if client not in current_clients:
                message = f"{client} 已从 OpenVPN 登出。"
                send_webhook(message)
        
        previous_clients = current_clients
        time.sleep(10)  # 每10秒检查一次

if __name__ == "__main__":
    status_file = "/run/openvpn-server/status-server.log"
    monitor_openvpn_status(status_file)
