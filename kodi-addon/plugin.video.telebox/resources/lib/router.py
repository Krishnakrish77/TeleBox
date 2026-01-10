import xbmcplugin
import xbmcgui
import sys
from resources.lib.api import get_channels, get_groups, get_messages

PLUGIN_HANDLE = int(sys.argv[1])

def show_main_menu():
    menu_items = [
        {"label": "Channels", "callback": show_channels},
        {"label": "Groups", "callback": show_groups},
    ]
    for item in menu_items:
        list_item = xbmcgui.ListItem(label=item["label"])
        url = f"{sys.argv[0]}?action={item['label'].lower()}"
        xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

def show_channels():
    channels = get_channels()
    for c in channels:
        list_item = xbmcgui.ListItem(label=c["name"])
        list_item.setInfo("video", {"title": c["name"]})
        url = f"{sys.argv[0]}?action=show_messages&chat_id={c['id']}"
        xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

def show_groups():
    groups = get_groups()
    for g in groups:
        list_item = xbmcgui.ListItem(label=g["name"])
        list_item.setInfo("video", {"title": g["name"]})
        url = f"{sys.argv[0]}?action=show_messages&chat_id={g['id']}"
        xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=url, listitem=list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

def show_messages(chat_id):
    messages = get_messages(int(chat_id), limit=50)
    for m in messages:
        label = m["text"] if m["text"] else "Media"
        list_item = xbmcgui.ListItem(label=label)
        if m["media"]:
            list_item.setProperty("IsPlayable", "true")
            url = f"{sys.argv[0]}?action=play&chat_id={chat_id}&msg_id={m['id']}"
            xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url=url, listitem=list_item, isFolder=False)
        else:
            xbmcplugin.addDirectoryItem(handle=PLUGIN_HANDLE, url="#", listitem=list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
