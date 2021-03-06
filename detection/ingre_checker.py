'''
食材画像判定
コンソール上で画像ファイルを引数にして実行してresult.htmlを生成する
参考書籍: Pythonによるスクレイピング&機械学習 開発テクニック BeautifulSoup,scikit-learn,TensorFlowを使ってみよう
src: gyudon-checker.py
'''


import ingre_cnn as ingre
import sys, os
from PIL import Image
import numpy as np

# コマンドラインからファイル名を得る、引数がなければ終了
if len(sys.argv) <= 1:
    print("ingre-checker.py (ファイル名)")
    quit()

image_size = 50
categories = [
    'carrot',
    'onion',
    'radish',
    'tomato',
    'cabbage',
]

# 入力画像をNumpyに変換 --- (※2)
X = []
files = []
for fname in sys.argv[1:]:
    img = Image.open(fname)
    img = img.convert("RGB")
    img = img.resize((image_size, image_size))
    in_data = np.asarray(img)
    print('in_data', in_data)
    X.append(in_data)
    files.append(fname)
X = np.array(X)

# CNNのモデルを構築 --- (※3)
model = ingre.build_model(X.shape[1:])
model.load_weights("./models/ingredient-cnn-model.hdf5")

# データを予測 --- (※4)
html = ""
pre = model.predict(X)
for i, p in enumerate(pre):
    y = p.argmax()
    print("+ 入力:", files[i])
    print("| 食材名:", categories[y])
    html += """
        <h3>入力:{0}</h3>
        <div>
          <p><img src="{1}" width=300></p>
          <p>食材名:{2}</p>
        </div>
    """.format(os.path.basename(files[i]),
        files[i],
        categories[y])

# レポートを保存 --- (※5)
html = "<html><body style='text-align:center;'>" + \
    "<style> p { margin:0; padding:0; } </style>" + \
    html + "</body></html>"
with open("result.html", "w") as f:
    f.write(html)


