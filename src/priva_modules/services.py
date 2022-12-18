import requests
import json

# tor proxies
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

def test(onion_addr: str, node_id: int):
    return requests.get('http://{}/find_successor?succ_node_id={}'.format(onion_addr, node_id), proxies=proxies).text

def find_successor(onion_addr: str,  self_addr: str, node_id: int):
    res = requests.post('http://{}/find_successor'.format(onion_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
    return res.json()

def join(onion_addr: str,  self_addr: str, node_id: int):
    res = requests.post('http://{}/join'.format(onion_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
    return res.json()

def get_predecessor(onion_addr: str):
    res = requests.get('http://{}/get_predecessor'.format(onion_addr), proxies=proxies)
    return res.json()

def notify(boot_addr: str,  self_addr: str, node_id: int):
    res = requests.post('http://{}/notify'.format(boot_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
    return res.text

def ping(onion_addr: str) -> int:
    res = requests.get('http://{}/ping'.format(onion_addr), proxies=proxies)
    return res.status_code

def send_message(onion_addr: str, tag: str, msg: str):
    res = requests.post('http://{}/message'.format(onion_addr), json={'user_id':tag, 'msg': msg}, proxies=proxies)
    return res.text

def send_connect(onion_addr: str, self_addr:str, tag: str):
    res = requests.post('http://{}/connect'.format(onion_addr), json={'user_id':tag, "onion_addr": self_addr}, proxies=proxies)
    return res.json()