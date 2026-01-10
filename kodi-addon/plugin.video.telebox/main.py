import sys
import xbmcplugin
from resources.lib.router import get_params
from resources.lib.ui import add_item
from resources.lib.api import (
    fetch_channels,
    fetch_groups,
    fetch_media
)

handle = int(sys.argv[1])
params = get_params()
action = params.get("action")

if action is None:
    add_item(handle, "📺 Channels",
             "plugin://plugin.video.telebox/?action=channels")
    add_item(handle, "👥 Groups",
             "plugin://plugin.video.telebox/?action=groups")

elif action == "channels":
    for c in fetch_channels():
        add_item(
            handle,
            c["name"],
            f"plugin://plugin.video.telebox/?action=list&chat_id={c['id']}"
        )

elif action == "groups":
    for g in fetch_groups():
        add_item(
            handle,
            g["name"],
            f"plugin://plugin.video.telebox/?action=list&chat_id={g['id']}"
        )

elif action == "list":
    chat_id = params["chat_id"]
    for m in fetch_media(chat_id):
        add_item(
            handle,
            m["name"],
            m["stream_url"],
            playable=True
        )

xbmcplugin.endOfDirectory(handle)
