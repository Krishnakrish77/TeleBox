import xbmcgui
import xbmcplugin

def add_item(handle, label, url, playable=False):
    li = xbmcgui.ListItem(label=label)

    if playable:
        li.setProperty("IsPlayable", "true")

    xbmcplugin.addDirectoryItem(
        handle=handle,
        url=url,
        listitem=li,
        isFolder=not playable
    )
