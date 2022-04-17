import requests
import json
from tqdm import tqdm
from datetime import datetime
from time import sleep

token_ya = ' '
token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
user_vk = '552934290'


def get_vk(user, token):
    url_vk = "https://api.vk.com/method/photos.get"
    params = {
        'owner_id': user_vk,
        'album_id': 'profile',
        'access_token': token_vk,
        'extended': 1,
        'count': 5,
        'v': 5.131,
    }
    res = requests.get(url_vk, params=params).json()

    l_photos = {}
    jsonphotos = []
    exp_1 = 0
    exp_2 = 0
    exp_3 = 0
    for item in res["response"]["items"]:
        for photo in item["sizes"]:
            if photo["height"] >= exp_1:
                exp_2 += 1
                exp_1 = photo["height"]
        if str(item["likes"]["count"]) + ".jpg" in l_photos.keys():
            likes = str(item["likes"]["count"]) + '_' + str(datetime.fromtimestamp(item["date"]).date()) + ".jpg"
            l_photos[likes] = item["sizes"][exp_2]
            jsonphotos.append({"file_name": likes, "size": item["sizes"][exp_2]["type"]})
            exp_3 += 1
            exp_1 = 0
            exp_2 = 0
        else:
            likes = str(item["likes"]["count"]) + ".jpg"
            l_photos[likes] = item["sizes"][exp_2]
            jsonphotos.append({"file_name": likes, "size": item["sizes"][-1]["type"]})
            exp_3 += 1
            exp_1 = 0
            exp_2 = 0

    with open('jsonphotos.json', 'w') as outfile:
        json.dump(jsonphotos, outfile)
    return l_photos


def get_ya(l_photos):
    headers = {
        "Content-Type": "application/json",
        'Authorization': 'OAuth {}'.format(token_ya)
    }
    url_ya = "https://cloud-api.yandex.net/v1/disk/resources/"
    params_1 = {'path': 'Фото из Вконтакте'}
    folder = requests.put(url=url_ya, params=params_1, headers=headers)
    if folder.status_code == 201:
        print("Папка создана!")
    else:
        print("Произошла ошибка: ", folder.status_code)
    for i in tqdm(l_photos):
        sleep(.1)
        params_2 = {"path": "Фото из Вконтакте" + "/" + str(i),
                  'url': l_photos[i]['url']
        }
        url_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload/"
        file = requests.post(url=url_upload, params=params_2, headers=headers)
        if file.status_code == 202:
            print("Фото загружено!")
        else:
            print("Произошла ошибка: ", file.status_code)


if __name__ == '__main__':

    q = input("Введите токен Яндекса: ")
    w = input("Введите токен Вконтакте: ")
    e = input("Введите ID пользователя Вконтакте: ")
    l_photos = get_vk(user_vk, token_vk)
    get_ya(l_photos)
