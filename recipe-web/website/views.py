import importlib
import random
import json
import requests
import pymysql.cursors
from PIL import Image
import numpy as np
from django.shortcuts import render
from .models import ImageFile
local_settings = importlib.import_module(".local_settings", "recipe-web")

def index(request):
    return render(request, 'website/index.html')

def recipes(request):
    if not request.method == 'POST':
        return render(request, 'website/index.html')
    image = ImageFile()
    image.title = request.FILES['pic'].name
    image.data = request.FILES['pic']
    # image.save()
    file_name = image.data

    img_json = trans_image_to_json(file_name)

    # flask製のAPIにjsonを投げ、検出結果を取得する
    recipe_detector_url = local_settings.FOOD_URL
    response = requests.post(recipe_detector_url, data=img_json)

    # TODO: 今回は単一食材だが、いずれは複数食材のリストが返ってくる
    ingredients_json = json.loads(response.text)
    ingredients_list = list(ingredients_json)
    ingredient = ingredients_list[0]
    search_word = trans_ing_to_search_word(ingredient)
    print('検出結果:', ingredient)

    recipe_json = search(search_word)
    context = json.loads(recipe_json)
    return render(
        request,
        'website/recipes.html',
        context,
    )

def search(S):
    # cf. search("たまねぎ")
    connection = pymysql.connect(host='localhost',
                                 user='ingre',
                                 password='ingreingre',
                                 db='ingre',
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()

    ingr_search = "SELECT recipe_id FROM ingr WHERE name like %s"
    recipe_search = "SELECT title,imgurl,howto FROM recipe WHERE recipe_id=%s"
    get_all_ingr = "SELECT name,quantity FROM ingr WHERE recipe_id=%s"

    res = {}

    cursor.execute(ingr_search,'%'+S+'%')
    recipe_ids = cursor.fetchall()
    random.shuffle(recipe_ids)
    recipe_id = recipe_ids.pop()["recipe_id"]

    cursor.execute(recipe_search,recipe_id)
    recipe_info = cursor.fetchone()
    res["title"] = recipe_info["title"]
    res["img"] = recipe_info["imgurl"]
    res["howto"] = list(recipe_info["howto"].split("¥;"))

    cursor.execute(get_all_ingr,recipe_id)
    recipe_ingrs = cursor.fetchall()
    res["ingr"] = []

    for ingr in recipe_ingrs:
        res["ingr"].append((ingr["name"],ingr["quantity"]))

    jsonstring = json.dumps(res, ensure_ascii=False)

    cursor.close()
    connection.close()

    return jsonstring


def trans_image_to_json(file_name):
    '''
    画像-> NumPy array-> json に変換
    '''
    image_size = 50
    img = Image.open(file_name)
    img = img.convert("RGB")
    img = img.resize((image_size, image_size))
    img_nparray = np.asarray(img)
    img_list = img_nparray.tolist()
    img_json = json.dumps(img_list)

    return img_json

def trans_ing_to_search_word(ingredient):
    '''
    recipe-detectorから英語で返ってきた食材名を
    レシピ検索に合わせた日本語に変換
    '''
    ings = [
        'carrot',
        'onion',
        'radish',
        'tomato',
        'cabbage',
    ]
    words = [
        'にんじん',
        'たまねぎ',
        '大根',
        'トマト',
        'キャベツ',
    ]

    result = ''
    try:
        index = ings.index(ingredient)
        result = words[index]
    except:
        pass

    return result

