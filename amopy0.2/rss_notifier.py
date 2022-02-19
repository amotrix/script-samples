""" Front Matter of Script Settings
# TOML format (https://en.wikipedia.org/wiki/TOML)

[author] # Optional
name = "github.com/amotrix"
contact = "https://github.com/amotrix"

[sample] # Optinal. sample properties
title = "RSS新文章通知"
description = "解析指定的RSS地址，当有新文章时发送通知"

[amo] # Required. For user to create amo

[amo.config] # Required
runtime = "amopy0.2" # Required
timeout = 30         # Required, Options: 10, 30, 60
memory = 128         # Required

[amo.profile] # Optional. Amo default profile
title = "Pando Blog"
description = "每小时检查一次RSS地址，过滤出新文章，发送提醒消息"

[amo.arguments] # Optional, depends on script logic
# argument name: customized
# allowed argument properties: label, type, value, hint, required
# required: label, type
[amo.arguments.url]
label = "RSS地址"
type = "string"
value = "https://docs.pando.im/blog/rss"
required = true
[amo.arguments.region]
label = "地区"
type = "string"
value = "tokyo"
hint = "seoul, tokyo, london, hongkong, virginia. default is tokyo"
required = true

[amo.triggers] # Optinal, Set default triggers to facilitate users to quickly deploy Amo
# allowed trigger type: schedule
[amo.triggers.schedule]
enable = true
expr = "0 * * * *" # (cron expression) every hour at minute 0
"""

from fake_builtin import *  # Valid only for development, ignored in production

amostorage = extensions.amo_storage
owl = extensions.owl


def text_compact(text, keep_multi_empty_lines=False):
    """紧凑化文本
    去掉换行，去掉多余空格
    """
    if not text:
        return ""

    if not keep_multi_empty_lines:
        text = regex_sub(r"\s+?(\S)", r" \1", text)
    else:
        text = regex_sub(r"[\t\f\v ]+?([\S\r\n])", r" \1", text)
        text = regex_sub(r"\r", r"\n", text)
        text = regex_sub(r"\n+", r"\n", text)

    text = text.strip()
    return text


def render_article_text(article):
    author = article.get("authors")
    author = author if author else ""
    text = (
        author
        + "《"
        + article["title"]
        + "》\n"
        + text_compact(article["content_value"])
        + "\n"
        + strftime(article["pub_uts"] + 8 * 3600, "%m-%d %H:%M")
        + " UTC+8\n"
        + article["link"]
    )
    return text


def filter_out_new(article_urls: list, data_file_name):
    if not article_urls:
        return []

    if amostorage.is_same(data_file_name, list(article_urls)):
        return []  # same data, no new articles

    old_urls = amostorage.read_data(data_file_name)
    if not old_urls:
        return article_urls

    new_urls = set(article_urls) - set(old_urls)
    return list(new_urls)


def main(url, region):
    data_file_name = "article.urls"

    log("getting rss...")
    parsed = extensions.feed.parse(url, region)
    if not parsed:
        log("No parsed data from url")
        return

    articles = {}
    for item in parsed["items"]:
        articles[item["link"]] = item
        # log(item["title"])

    article_urls = list(articles.keys())
    log(f"{len(articles)} articles")
    if len(articles) == 0:
        return

    log("filters...")
    new_urls = filter_out_new(article_urls, data_file_name)
    log(f"{len(new_urls)} new articles")
    if len(new_urls) == 0:
        return

    msgs = []
    log("render message text...")
    for url in new_urls:
        txt = render_article_text(articles[url])
        msg = owl.pack_mixin_messenger_message("text", txt)
        msgs.append(msg)

    log("sending mmsgs...")
    owl.send_me_mixin_messenger_messages(msgs)

    log("store current article urls")
    amostorage.write_data(article_urls, data_file_name)


main(args["url"], args["region"])
