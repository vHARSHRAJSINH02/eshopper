import pytz
import jwt
from datetime import datetime,timedelta


def generate_token(user):
    
    current_timezone = pytz.timezone('asia/kolkata')
    current_time = datetime.now(current_timezone)
    expire_time = current_time + timedelta(hours=5)
    payload = {
        'user_id':user.id,
        'exp':datetime.timestamp(expire_time)
    }
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    g_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return g_token

def expire_token(user):
    
    current_timezone = pytz.timezone('asia/kolkata')
    current_time = datetime.now(current_timezone)
    expire_time = current_time + timedelta(seconds=1)
    payload = {
        'user_id':user.id,
        'exp':datetime.timestamp(expire_time)
    }
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    g_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return g_token

def generate_delivery_token(d_user):
    
    current_timezone = pytz.timezone('asia/kolkata')
    current_time = datetime.now(current_timezone)
    expire_time = current_time + timedelta(hours=5)
    payload = {
        'user_id':d_user.d_id,
        'exp':datetime.timestamp(expire_time)
    }
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    g_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return g_token


def expire_delivery_token(d_user):
    
    current_timezone = pytz.timezone('asia/kolkata')
    current_time = datetime.now(current_timezone)
    expire_time = current_time + timedelta(seconds=1)
    payload = {
        'user_id':d_user.d_id,
        'exp':datetime.timestamp(expire_time)
    }
    secret_key = 'django-insecure-p(bqgp(bqf4k4zz&=awxgo&9!numh0%xk(o*ijwqs!6lip-567'
    g_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return g_token