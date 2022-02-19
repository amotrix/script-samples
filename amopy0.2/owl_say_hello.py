""" Front Matter of Script Settings
# TOML format (https://en.wikipedia.org/wiki/TOML)

[author] # Optional
name = "github.com/amotrix"
contact = "https://github.com/amotrix"

[sample] # Optinal. sample properties
title = "猫头鹰说你好"
description = "通过猫头鹰机器人向自己发送一条文本消息"

[amo] # Required. For user to create amo

[amo.config] # Required
runtime = "amopy0.2" # Required
timeout = 10         # Required, Options: 10, 30, 60
memory = 128         # Required

[amo.profile] # Optional. Amo default profile
title = "猫头鹰说你好"
description = "通过猫头鹰递信向自己发送一条文本消息。需先添加猫头鹰递信机器人（7000102034）为好友"

[amo.arguments] # Optional, depends on script logic
# argument name: customized
# argument properties:label, type, value, hint, required
#       required properties: label, type
[amo.arguments.what]
label = "说什么"
type = "string"
value = "你好👋"
hint = ""
required = true
"""

from fake_builtin import *  # Valid only for development, ignored in production


def main():
    owl = extensions.owl
    msg = owl.pack_mixin_messenger_message("text", args["what"])
    owl.send_me_mixin_messenger_messages([msg])


main()
