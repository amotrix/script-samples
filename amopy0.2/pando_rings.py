""" Front Matter of Script Settings
# TOML format (https://en.wikipedia.org/wiki/TOML)

[author] # Optional
name = "github.com/amotrix"
contact = "https://github.com/amotrix"

[sample] # Optional. sample properties
title = "Pando Rings 资产供给收益率播报"
description = "定时检查 Pando Rings 资产供给收益率，根据设置的参数过滤后，发送播报"

[amo] # Required. For user to create amo

[amo.config] # Required. Amo resource
runtime = "amopy0.2" # Required
timeout = 30         # Required, Options: 10, 30, 60
memory = 128         # Required

[amo.profile] # Optional. Amo default profile
title = "PandoRingsAPY"
description = "定时检查 Pando Rings 资产供给收益率，并根据所设条件发送播报。通过猫头鹰递信(7000102034)发送"

[amo.arguments] # Optional, depends on script logic
# argument name: customized
# argument properties: label, type, value, hint, required, options
#   required properties: label, type, value
#   argument type: string, number, boolean, selection, mixin_assets
#   options format: [ ["label",value"], ... ]

[amo.arguments.symbols]
label = "指定资产"
type = "string"
value = "USDT"
hint = "留空则默认包含所有资产。多个资产之间用空格或逗号分隔。例如：BTC USDT PUSD"


[amo.arguments.apy_gt]
label = "收益率阈值"
type = "number"
value = 1
hint = "百分比数值。收益率超过此值时发送提醒"


[amo.triggers] # Optional, Set default triggers to facilitate users to quickly deploy Amo
# allowed trigger type: schedule
[amo.triggers.schedule]
enable = false
expr = "18 * * * *" # (cron expression) every hour at minute 18
"""

from ._fake_builtin import *  # Valid only for development, ignored in production

rings = extensions.foxone.pando_rings
owl = extensions.owl


def get_emoji(percent):
    if percent < 4:
        return ""
    if percent < 8:
        return "🧧"
    if percent < 15:
        return "🤑🤑"
    # bigger
    return "💥💥💥"


def main(title, symbols, apy_gt):
    markets = rings.get_markets_all()["data"]

    if symbols:
        symbols = symbols.replace(" ", ",").replace("，", ",").split(",")
        symbols = [s.upper() for s in symbols]
    apy_gt = float(apy_gt)

    asset_lines = []
    for item in markets:
        symbol = item["symbol"].upper()
        # filter by symbol
        if symbols and symbol not in symbols:
            continue

        supply_apy = float(item["supply_apy"])
        percent = int(supply_apy * 10000) / 100
        # filter by apy
        if percent == 0:
            continue
        if percent < apy_gt:
            continue

        # render asset line
        asset_apy = f"{symbol} {percent}% {get_emoji(percent)}"
        asset_lines.append(asset_apy)

    # notice me
    if not asset_lines:
        return
    report = "\n".join(asset_lines)
    report = f"{title}\n{report}"
    #
    msg = owl.pack_mixin_messenger_message("text", report)
    owl.send_me_mixin_messenger_messages([msg])


main(env["TITLE"], args["symbols"], args["apy_gt"])
