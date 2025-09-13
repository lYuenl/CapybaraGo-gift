import requests
from PIL import Image
from io import BytesIO
import json
import ddddocr
import threading
import time
import os

def GetCaptchaID():
    url = "https://prod-mail.habbyservice.com/Capybara/api/v1/captcha/generate"
    response = requests.post(url)
    CaptchaID_dict = json.loads(response.text)
    CaptchaID = CaptchaID_dict["data"]["captchaId"]
    return CaptchaID

def GetCaptcha(captcha_id):
    captcha_url = f"https://prod-mail.habbyservice.com/Capybara/api/v1/captcha/image/{captcha_id}"
    res = requests.get(captcha_url)
    if res.status_code == 200:
        image = Image.open(BytesIO(res.content))
        captcha = str(ocr.classification(image)).upper()
        return captcha
    else:
        print("取得驗證碼失敗，HTTP 狀態碼：", res.status_code)
        os._exit(1)

def main(user_id):
    while True:
        try:
            url = "https://prod-mail.habbyservice.com/Capybara/api/v1/giftcode/claim"
            captcha_id = GetCaptchaID()
            captcha = GetCaptcha(captcha_id)
            payload = {
                "userId": user_id,
                "giftCode": gift_code,
                "captcha": captcha,
                "captchaId": captcha_id
            }

            response = requests.post(url, json = payload)
            response_dict = json.loads(response.text)
            response_code = response_dict["code"]
            #response_message = response_dict["message"]

            msg_map = {
                0: "已成功兌換獎勵!",
                20002: "驗證碼錯誤",
                20003: "UserID輸入錯誤",
                20401: "兌換碼錯誤",
                20403: "兌換碼已過期",
                20407: "已領取過此獎勵"
            }
            
            if msg_map.get(response_code):
                users[user_id]["msg"] = msg_map[response_code]
            else:
                users[user_id]["msg"] = response.text

            if response_code == 20002:
                continue
            elif response_code == 20401 or response_code == 20403:
                print(f"[伺服器訊息]: {msg_map[response_code]}")
                os._exit(1)
            else:
                break
            time.sleep(1)
            
        except Exception as e:
            print(str(e))
            time.sleep(1)
            break

if __name__ == "__main__":
    ocr = ddddocr.DdddOcr(show_ad = False)
    thread_list = []
    users = {
    "userid1": {"username": "username1", "msg": ""},
    "userid2": {"username": "username2", "msg": ""},
    "userid3": {"username": "username3", "msg": ""}
    }

    gift_code = input("請輸入兌換序號：")
    for user in users:
        t = threading.Thread(target = main, args = (user,))
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    for user_id in users:
        print(f"{users[user_id]['username']} - 兌換結果: {users[user_id]['msg']}")

    print("\n所有用戶已兌換完成")