""" Front Matter of Script Settings
# TOML format (https://en.wikipedia.org/wiki/TOML)

[author] # Optional
name = "github.com/amotrix"
contact = "https://github.com/amotrix"

[sample] # Optional. sample properties
title = "关注 Twitter 更新"
description = "关注指定的推特账号，递送新推文"

[amo] # Required. For user to create amo

[amo.config] # Required
runtime = "amopy0.2" # Required
timeout = 30         # Required, Options: 10, 30, 60
memory = 128         # Required

[amo.profile] # Optional. Amo default profile
title = "Twitter@xiaolai"
description = "每20分钟检查一次推特更新。通过猫头鹰递信(7000102034)推送更新。"

[amo.arguments] # Optional, depends on script logic
# argument name: customized
# argument properties: label, type, value, hint, required, options
#   required properties: label, type, value
#   argument type: string, number, boolean, selection, mixin_assets
#   options format: [ ["label",value"], ... ]

[amo.arguments.user_id]
label = "用户 ID"
type = "string"
value = "61356505"
required = true
hint = "是一串数字，不是用户名称"

[amo.arguments.retweeted]
label = "包含转发"
type = "boolean"
value = true
required = true

[amo.arguments.replied]
label = "包含回复"
type = "boolean"
value = true
required = true

[amo.triggers] # Optional, Set default triggers to facilitate users to quickly deploy Amo
# allowed trigger type: schedule
[amo.triggers.schedule]
enable = true
expr = "*/20 * * * *" # (cron expression)
"""

from ._fake_builtin import *  # Valid only for development, ignored in production

amostorage = extensions.amo_storage
owl = extensions.owl
twitter = extensions.twitter


def push_tweets(tweets, title):
    log(f"push {len(tweets)} tweets")

    # tweet = { url, pub_ts,lang, content, attributes, public_metrics, possibly_sensitive, images, polls}

    # sort tweets by pub_ts
    tweets.sort(key=lambda tweet: tweet["pub_ts"], reverse=False)

    # render messages
    msgs = []
    for tweet in tweets:
        text = title + "\n" + tweet["content"] + "\n" + tweet["url"]
        text += "\n" + packages.timeutils.time_to_readable(tweet["pub_ts"])[2:-3]
        msg = owl.pack_mixin_messenger_message("text", text)
        msgs.append(msg)

    owl.send_me_mixin_messenger_messages(msgs)


def main(title, user_id, include_retweeted, include_replied):
    data_file_name = "latest_tweet_ts"

    tweets = twitter.get_user_latest_tweets(user_id)
    if not tweets:
        log("no tweets")
        return

    data = amostorage.read_data(data_file_name)
    latest_tweet_ts = data if data else 0

    # filter out new tweets
    new_tweets = []
    new_latest_tweet_ts = latest_tweet_ts
    for tweet in tweets:
        pub_ts = tweet["pub_ts"]
        if pub_ts > latest_tweet_ts:
            new_tweets.append(tweet)
            # record new latest tweet ts
            if pub_ts > new_latest_tweet_ts:
                new_latest_tweet_ts = pub_ts

    if not include_retweeted:
        # filter retweeted # "attributes": {"referenced_type": "retweeted"}
        new_tweets = [
            tweet
            for tweet in new_tweets
            if tweet.get("attributes", {}).get("referenced_type") != "retweeted"
        ]

    if not include_replied:
        # filter replied # "attributes": {"referenced_type": "replied_to"}
        new_tweets = [
            tweet
            for tweet in new_tweets
            if tweet.get("attributes", {}).get("referenced_type") != "replied_to"
        ]

    if not new_tweets:
        log("no new tweets")
        return

    push_tweets(new_tweets, title)

    amostorage.write_data(new_latest_tweet_ts, data_file_name)


main(env["TITLE"], args["user_id"], args["retweeted"], args["replied"])
