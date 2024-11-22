import time
import requests
import json
import os

# 企业微信机器人webhook地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1"

# VPN映射文件路径
MAPPING_FILE = "vpn_mapping.json"

def load_vpn_mapping():
    """Load VPN mapping from JSON file if it exists"""
    try:
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load mapping file: {e}")
    return {}

def read_status_file(filename):
    clients = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("CLIENT_LIST"):
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    clients[parts[1]] = parts[2]
    return clients

def get_client_info(client_name, vpn_mapping):
    """Get friendly client info from mapping"""
    # Try to find .ovpn files with and without case sensitivity
    possible_files = [
        f"{client_name}.ovpn",
        f"{client_name.lower()}.ovpn",
        f"{client_name.upper()}.ovpn"
    ]
    
    for filename in possible_files:
        if filename in vpn_mapping:
            info = vpn_mapping[filename]
            location_str = f"[{info['location']}] " if info['location'] else ""
            return f"{location_str}{info['user']} ({filename})"
    
    # Fallback to original name if no mapping found
    return client_name

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
    vpn_mapping = load_vpn_mapping()
    
    print(f"Loaded {len(vpn_mapping)} VPN mappings")
    
    while True:
        current_clients = read_status_file(filename)
        
        # 检查新登录的用户
        for client, ip in current_clients.items():
            if client not in previous_clients:
                client_info = get_client_info(client, vpn_mapping)
                message = f"{client_info} 已登录 OpenVPN。登录IP: {ip}"
                send_webhook(message)
        
        # 检查登出的用户
        for client in previous_clients:
            if client not in current_clients:
                client_info = get_client_info(client, vpn_mapping)
                message = f"{client_info} 已从 OpenVPN 登出。"
                send_webhook(message)
        
        previous_clients = current_clients
        time.sleep(10)  # 每10秒检查一次

if __name__ == "__main__":
    status_file = "/run/openvpn-server/status-server.log"
    monitor_openvpn_status(status_file)
