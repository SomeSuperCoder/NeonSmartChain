import requests
import urllib.parse
import config


def send_json_to_path(data, path, node_ip):
    response = requests.post(concatenate_url(node_ip, config.node_port, path), json=data)
    return response.text


def get_json_from_path(path, node_ip):
    response = requests.get(concatenate_url(node_ip, config.node_port, path))
    return response.json()


def broadcast_json_to_url(data, url, node_list):
    try:
        for node_ip in list(set(node_list)):
            send_json_to_path(data, url, node_ip)
        return True
    except:
        return False


def concatenate_url(ip, port, path):
    url_components = ('http', f'{ip}:{port}', path, '', '', '')
    complete_url = urllib.parse.urlunparse(url_components)
    return complete_url
