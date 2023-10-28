import json
import openai
import tweepy
import os


def lambda_handler(event=None, context=None):
    try:
        account = event["body"].split("=")[1]
        account = account.replace('"id"', "")
        account = account.split("-")[0]
    except Exception as e:
        print(str(e))
        return {
            "statusCode": 200,
            "body": json.dumps({"message": str(e)}),
        }

    # .envファイルからTwitter APIの認証キーを読み込む
    CONSUMER_KEY = os.environ["CONSUMER_KEY"]
    CONSUMER_SECRET = os.environ["CONSUMER_SECRET"]
    ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = os.environ["ACCESS_TOKEN_SECRET"]
    CHATGPT_API_KEY = os.environ["CHATGPT_API_KEY"]

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    tweets = api.user_timeline(screen_name=account, count=100, tweet_mode="extended")
    tweet_str = " ".join([tweet.full_text for tweet in tweets])

    openai.api_key = CHATGPT_API_KEY

    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.1,
        messages=[
            {"role": "system", "content": "あなたはプロの性格診断士です。"},
            {"role": "system", "content": "次のツイートを分析して、優しく褒めてください。"},
            {"role": "user", "content": tweet_str},
        ],
    )

    if res["choices"]:
        message = res.choices[0]["message"]["content"].strip()
        print(message)
    else:
        print("No response from GPT-3 API.")

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST,GET,PUT,DELETE",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps({"message": message}),
    }


if __name__ == "__main__":
    lambda_handler()
