import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from user.models import UserProfile
import hashlib


# 例外コード: 10100 - 10199

# Create your views here.

# FBV (Function)
def user_views(request):

    if request.method == 'GET':
        pass

    elif request.method == 'POST':
        pass

# CBV(Class)
# より使いやすい（継承できる）
# 未定義のhttp method　リクエストに対して　405リスポンスをリターンする
class UserViews(View):

    # def get(self,request):
    #
    #     return JsonResponse({'code':200, 'msg':'test'})

    def post(self,request):

        # POST式リクエストではGETでデータ取得できない　→ request.bodyにてデータ取得
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj["username"]
        email = json_obj["email"]
        password_1 = json_obj["password_1"]
        password_2 = json_obj["password_2"]
        phone = json_obj["phone"]

        # パラメーター検査
        if password_1 != password_2:
            result = {'code':10100,'error':'パスワード一致ではありません'}
            return JsonResponse(result)

        # ユーザーネーム可用か
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            result = {'code':10101,'error':'ユーザーネームは既に存在しています'}
            return JsonResponse(result)

        # result = {'code':10100,'error':'The username is already exsited'}
        # return JsonResponse(result)

        # UserProfile　データ挿入(パスワードをMD5/hashにて保存)
        p_m = hashlib.md5()
        p_m.update(password_1.encode()) # byte式必要

        # 新規ユーザー登録
        UserProfile.objects.create(
            username=username,
            nickname=username,
            password=p_m.hexdigest(),
            email=email,
            phone=phone,
        )

        result = {'code':200,'username':username,'data':{}} # 他の必要なデータあればdataに追加
        return JsonResponse(result)
