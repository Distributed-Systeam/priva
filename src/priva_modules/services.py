import requests
import json
from requests.adapters import HTTPAdapter, Retry

s = requests.Session()
retries = Retry(total=3,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))

# tor proxies
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

def test(onion_addr: str, node_id: int):
    try:
        s.get('http://{}/find_successor?succ_node_id={}'.format(onion_addr, node_id), proxies=proxies).text
    except Exception as e:
        print('== SERVICE ** test ** ERROR: {}'.format(e))

def find_successor(onion_addr: str,  self_addr: str, node_id: int):
    try:
        res = s.post('http://{}/find_successor'.format(onion_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
        return res.json()
    except Exception as e:
        print('== SERVICE ** find_successor ** ERROR: {}'.format(e))
        return None

def join(onion_addr: str,  self_addr: str, node_id: int):
    try:
        res = s.post('http://{}/join'.format(onion_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
        return res.json()
    except Exception as e:
        print('== SERVICE ** join ** ERROR: {}'.format(e))
        return None

def get_predecessor(onion_addr: str):
    try:
        res = s.get('http://{}/get_predecessor'.format(onion_addr), proxies=proxies)
        return res.json()
    except Exception as e:
        print('== SERVICE ** get_predecessor ** ERROR: {}'.format(e))
        return None

def notify(boot_addr: str,  self_addr: str, node_id: int):
    try:
        res = s.post('http://{}/notify'.format(boot_addr), json={'node_id': node_id, "onion_addr": self_addr}, proxies=proxies)
        return res.text
    except Exception as e:
        print('== SERVICE ** notify ** ERROR: {}'.format(e))
        return 'Error notifying'

def ping(onion_addr: str) -> int:
    try:
        res = s.get('http://{}/ping'.format(onion_addr), proxies=proxies)
        return res.status_code
    except Exception as e:
        print('== SERVICE ** ping ** ERROR: {}'.format(e))
        return 666

def send_message(onion_addr: str, tag: str, msg: str):
    try:
        res = s.post('http://{}/message'.format(onion_addr), json={'user_id':tag, 'msg': msg}, proxies=proxies)
        return res.text
    except Exception as e:
        print('== SERVICE ** send_message ** ERROR: {}'.format(e))
        return 'Error sending message'

def send_connect(onion_addr: str, self_addr:str, tag: str):
    try:
        res = s.post('http://{}/connect'.format(onion_addr), json={'user_id':tag, "onion_addr": self_addr}, proxies=proxies)
        return res.json()
    except Exception as e:
        print('== SERVICE ** send_connect ** ERROR: {}'.format(e))
        return None