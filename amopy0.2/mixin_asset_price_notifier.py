from fake_builtin import *  # Valid only for development, ignored in production

# Settings for Amo
settings = {
    # Config (Required)
    "config": {
        "runtime": "amopy0.2",
        "timeout": 30,
        "memory": 128,
    },
    # Default profile (Optional)
    "profile": {
        "title": "加密货币价格提醒",
        "description": "每小时检查一次价格，根据条件发送提醒消息",
    },
    # Script Author (Optional)
    "author": {
        "name": "ZHN",
        "contact": "Mixin ID: 37297553",
        # "amo-uid": "",  # AMO.RUN USER ID, 若填写，可获得相应电力值的分成。
    },
    # Arguments (Optional, depends on script)
    "arguments": {
        "asset_id": {
            "label": "资产ID",
            "type": "string",
            "value": "c94ac88f-4671-3976-b60a-09064f1811e8",  # default is XIN
            "hint": "",
            "required": True,
        },
        "asset_name": {
            "label": "资产名称",
            "type": "string",
            "value": "XIN",  # default is XIN
            "hint": "Mixin",
            "required": True,
        },
        ">": {
            "label": "大于提醒",
            "type": "number",
            "value": 350,  # default
            "hint": "价格大于此值时发送提醒（单位: USD）",
        },
        "<": {
            "label": "小于提醒",
            "type": "number",
            "value": 300,  # default
            "hint": "价格小于此值时发送提醒（单位: USD）",
        },
    },
    # Triggers (Optinal, Set default triggers to facilitate users to quickly deploy Amo)
    "triggers": {
        "schedule": {
            "enable": False,
            "expr": "0 * * * *",  # every hour
        }
    },
}

""" ASSET IDS:
XIN = "c94ac88f-4671-3976-b60a-09064f1811e8"
"""


def main():
    # get price
    data = mixin.api.network_read_historical_price(args["asset_id"])
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

    gt = args.get(">")
    if gt and price_usd > float(gt):

        mmsg = cf_owl_pack_mmmsg(
            "text", f"{args['asset_name']} 当前价格: {price_usd:.3f} USD (> {gt} USD)"
        )
        cf_owl_sendme_mmmsgs([mmsg])
        return

    lt = args.get("<")
    if lt and price_usd < float(lt):
        mmsg = cf_owl_pack_mmmsg(
            "text", f"{args['asset_name']} 当前价格: {price_usd:.3f} USD (< {lt} USD)"
        )
        cf_owl_sendme_mmmsgs([mmsg])
        return


main()
