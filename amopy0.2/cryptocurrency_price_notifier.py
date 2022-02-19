""" Front Matter of Script Settings
# TOML format (https://en.wikipedia.org/wiki/TOML)

[author] # Optional
name = "github.com/amotrix"
contact = "https://github.com/amotrix"

[sample] # Optinal. sample properties
title = "加密货币价格提醒"
description = "当加密货币价格达到指定值时发送通知"

[amo] # Required. For user to create amo

[amo.config] # Required. Amo resource
runtime = "amopy0.2" # Required
timeout = 30         # Required, Options: 10, 30, 60
memory = 128         # Required

[amo.profile] # Optional. Amo default profile
title = "XIN 价格提醒"
description = "每小时检查一次价格，根据条件发送提醒消息（通过猫头鹰机器人发送，请添加 7000102034 为好友）"

[amo.arguments] # Optional, depends on script logic
# argument name: customized
# allowed argument properties: label, type, value, hint, required
# required: label, type
[amo.arguments.asset_id]
label = "资产ID"
type = "string"
value = "c94ac88f-4671-3976-b60a-09064f1811e8" # default is XIN
hint = "可使用 Mixin 机器人 7000103061 查询资产ID"
required = true
[amo.arguments.asset_name]
label = "资产名称"
type = "string"
value = "XIN"
required = true
[amo.arguments.gt]
label = "大于提醒"
type = "number"
value = 350
hint = "价格大于此值时发送提醒（单位: USD）"
[amo.arguments.lt]
label = "小于提醒"
type = "number"
value = 300
hint = "价格小于此值时发送提醒（单位: USD）"


[amo.triggers] # Optinal, Set default triggers to facilitate users to quickly deploy Amo
# allowed trigger type: schedule
[amo.triggers.schedule]
enable = true
expr = "0 * * * *" # (cron expression) every hour at minute 0
"""
from fake_builtin import *  # Valid only for development, ignored in production

mixinapi = packages.mixin.api
owl_pack_msg = extensions.owl.pack_mixin_messenger_message
owl_send_msgs = extensions.owl.send_me_mixin_messenger_messages


""" ASSET IDS:
XIN = "c94ac88f-4671-3976-b60a-09064f1811e8"
"""


def main():
    # get price
    data = mixinapi.network_read_historical_price(args["asset_id"])
    """e.g.
    data = {
        "data": {
            "type": "ticker",
            "price_btc": "0.00836181958312329566619627153687",
            "price_usd": "348.55438028859089896608051425045079",
        }
    }"""

    price_usd = float(data["data"]["price_usd"])
    log(f"{args['asset_name']} price in usd: {price_usd}")

    gt = args.get("gt")
    if gt and price_usd > float(gt):

        mmsg = owl_pack_msg(
            "text", f"{args['asset_name']} 当前价格: {price_usd:.3f} USD (> {gt} USD)"
        )
        owl_send_msgs([mmsg])
        return

    lt = args.get("lt")
    if lt and price_usd < float(lt):
        mmsg = owl_pack_msg(
            "text", f"{args['asset_name']} 当前价格: {price_usd:.3f} USD (< {lt} USD)"
        )
        owl_send_msgs([mmsg])
        return


main()
