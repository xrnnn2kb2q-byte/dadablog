import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from user.models import UserProfile
import hashlib
from django.utils.decorators import method_decorator
from dadablog.tools.logging_dec import logging_check

# 例外コード: 10100 - 10199

# djangoはdecoratorを提供している（method_decorator）関数のデコレーターをメソードのデコレーターに変換できる

# Create your views here.

# FBV (Function)
@method_decorator(logging_check)
def user_views(request,username):

    if request.method != 'POST':
        result = {'code':10103,'error':'POSTでリクエストしてください'}
        return JsonResponse(result)

    user = request.myuser

    # フロントエンドからのファイルデータを取得（ICON更新）
    avatar = request.FILES.get('avatar')
    user.avatar = avatar
    user.save()
    return JsonResponse({'code':200})


# CBV(Class)
# より使いやすい（継承できる）
# 未定義のhttp method　リクエストに対して　405リスポンスをリターンする
class UserViews(View):

    # 個人情報をリクエスト（展示）
    def get(self,request,username=None):
        if username:
            # /v1/users/guoxiaonao
            # 外部攻撃や、username存在してない場合、usernameを検査必要
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                result = {'code':10102,'error':'ユーザーネームは正しくありません'}
                return JsonResponse(result)
            result = {'code':200,'username':username,'data':{
                'info':user.info,
                'sign':user.sign,
                'nickname':user.nickname,
                'avatar':str(user.avatar) # JSONはIMG対象を認識できないため、文字列に変換する必要
            }}
            return JsonResponse(result)

        else:
            # /v1/users
            pass

        result = {'code':200,'username':username,'data':{}}
        return JsonResponse(result)

    # 新規登録や個人情報を更新など
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

    @method_decorator(logging_check)
    def put(self,request,username=None):
        # ユーザー情報を更新する（username, sign, info）
        # /v1/users/guoxiaonao
        json_str = request.body
        json_obj = json.loads(json_str) # 同じように、POST/PUTメソードはrequest.GETで取得できない

        # 外部攻撃/不正アクセスを防ぐため、まずusernameをチェックする
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            result = {'code':10105,'error':'ユーザーネームは正しくありません'}
            return JsonResponse(result)

        # 情報更新
        user.sign = json_obj["sign"]
        user.info = json_obj["info"]
        user.nickname = json_obj["nickname"]
        # 情報保存
        user.save()
        return JsonResponse({'code':200})