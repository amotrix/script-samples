from fake_builtin import *

# Settings for Amo
#   JSON format
settings = {
    # Config (必需)
    "config": {
        "runtime": "amopy0.2",  # Options: amopy0.2
        "timeout": 30,  # Unit: Second. Options: 10,30,60
        "memory": 128,  # Unit: MB, Options: 128
    },
    # Script Author （可选）
    "author": {
        "name": "string",  # Limit 50 chars
        "contact": "string",  # Limit 150 chars
    },
    # Arguments （可选，根据程序需要）
    "arguments": {
        "apy>": {
            "label": "年化收益率大于",
            "type": "number",
            "value": 1,  # default
            "hint": "年收益率超过此阈值的资产",
            "hehe": "for test.",
        },
        "vol>": {
            "label": "APY波动大于",
            "type": "number",
            "value": 0,  # default
            "hint": "资产年收益率（距上次推送后）的变化幅度",
        },
    },
    # Triggers （可选，设置默认触发器，方便快速部署阿莫）
    "triggers": {"schedule": {"enable": False, "expr": "*/20 * * * *"}},
}


def filter_markets(markets: list, asset_symbols="*", apy_threshold=0, floating_point=0):
    """
    - parameters
        - asset_symbols, example: "USDT,BTC,ETH". default is "*" means all assets
        - asset_symbols, percentage number, 0~100.

    - return
        asset_apy_mapping
    """
    log("filtering...")

    # filter by asset symbol
    keep_assets = None
    if asset_symbols != "*":
        keep_assets = [x.strip().upper() for x in asset_symbols.split(",")]

    # calc supply apy
    asset_apy_mapping = {}
    for item in markets:
        symbol = item["symbol"].upper()
        # filter by assets
        if keep_assets is not None:
            if symbol not in keep_assets:
                continue
        # apy number
        supply_apy = float(item["supply_apy"])
        percent = int(supply_apy * 10000) / 100
        # filter by apy threshold
        if percent > apy_threshold:
            asset_apy_mapping[symbol] = percent

    if len(asset_apy_mapping) == 0:
        return asset_apy_mapping  # {}

    # filter by floating_point
    # any assets apy floating greater than point, will notice
    will_notice = True
    if floating_point > 0:
        will_notice = False
        # read last data
        last_assets_apy = cf_amostorage_read(data_file_name)
        if last_assets_apy:
            for symbol in last_assets_apy:
                if symbol in asset_apy_mapping:
                    if (
                        abs(asset_apy_mapping[symbol] - last_assets_apy[symbol])
                        > floating_point
                    ):
                        will_notice = True
                        break

    if will_notice:
        return asset_apy_mapping
    else:
        return {}


def send_mixin_msg(text):
    log("send mixin message")
    text = env["TITLE"] + "\n" + text
    msg = cf_owl_pack_mmmsg("text", text)
    cf_owl_sendme_mmmsgs([msg])


def render_report(asset_apy_mapping):
    def get_emoji(percent):
        if percent < 4:
            return ""
        if percent < 8:
            return "🧧"
        if percent < 15:
            return "🤑🤑"
        # bigger
        return "💥💥💥"

    lines = []
    for symbol in asset_apy_mapping:
        percent = asset_apy_mapping[symbol]
        line = f"{symbol} {percent}% {get_emoji(percent)}"
        lines.append(line)
    report_text = "\n".join(lines)

    return report_text


def get_pando_rings_markets_data() -> list:
    log("Get markets data from pando rings ...")
    api_base_url = "https://rings-api.pando.im/api/v1/"
    url = api_base_url + "markets/all"
    rsp = cf_httpget_pando_api(url)
    # log(rsp)
    return rsp["json"]["data"]


def main():
    markets = get_pando_rings_markets_data()
    asset_apy_mapping = filter_markets(markets, "*", args["apy>"], args["vol>"])
    if len(asset_apy_mapping) == 0:
        log("no matched assets")
        return
    log(f"matched {len(asset_apy_mapping)}")

    text = render_report(asset_apy_mapping)
    send_mixin_msg(text)

    # save changed asset_apy_mapping
    try:
        cf_amostorage_write(asset_apy_mapping, data_file_name)
        log("Saved current apy")
    except Exception as e:
        log(str(e))


data_file_name = "pando_rings_supply_apy.json"
main()
