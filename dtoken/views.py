import time
import jwt
from django.http import JsonResponse
from django.shortcuts import render
from user.models import UserProfile
import json
import hashlib
from django.conf import settings

# 例外コード　10200 - 10299
# Create your views here.

def tokens(request):

    if request.method != 'POST':
        result = {'code':10200,'error':'POSTでリクエストしてください'}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str) # dictに変換する（序列化）
    username = json_obj['username']
    password = json_obj['password']
    # ユーザーネームとパスワードをチェックする
    try:
        user = UserProfile.objects.get(username=username)
    except Exception as e:
        result = {'code':10201,'error':'ユーザーネームまたはパスワードは正しくありません'}
        return JsonResponse(result)

    p_m = hashlib.md5()
    p_m.update(password.encode())
    if p_m.hexdigest() != password:
        result = {'code':10202,'error':'ユーザーネームまたはパスワードは正しくありません'}
        return JsonResponse(result)

    # 会話状態を記録する（ログイン状態の保持）
    token = make_token(username)
    # 生成したtokenはbyteで、encode()で文字列に統一する
    result = {'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)

# jwtでtokenを生成する　有効期限は一日間
def make_token(username,expire=3600*24):
    # settings.py にて定義(123456)
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'username':username,'exp':now_t+expire} # 暗号化するデータと有効期限を設定
    return jwt.encode(payload_data,key,algorithm='HS256')