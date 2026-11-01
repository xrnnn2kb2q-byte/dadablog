import jwt
from django.conf import settings
from django.http import JsonResponse
from user.models import UserProfile


def logging_check(func):

    def wrap(request,*args,**kwargs):
        # tokenを取得(headerから取得)  request.META.get('HTTP_AUTHORIZATION')
        token = request.META.get('HTTP_AUTHORIZATION')
        # 失敗：code:403, error: ログインしてください
        if not token:
            result = {'code':403,'error':'ログインしてください'}
            return JsonResponse(result)

        # tokenを検証(jwt)
        try:
            res = jwt.decode(token,settings.JWT_TOKEN_KEY,algorithm='HS256')
        except Exception as e:
            print('jwt decode error is %s' % e)
            result = {'code':403,'error':'ログインしてください'}
            return JsonResponse(result)

        # ログインしているユーザーを取得
        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user
        return func(request,*args,**kwargs)

    return wrap