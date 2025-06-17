class SpaceApiEntry:
    @staticmethod
    def create_netz39():
        entry = SpaceApiEntry(
            space="Netz39",
            logo="https://wiki.netz39.de/_media/resources:public_relations:logo:netz39_logo_2013-07-11.png",
            url="https://www.netz39.de/",
            address="Leibnizstr. 32, 39104 Magdeburg, Germany",
            lat=52.119561,
            lon=11.629398,
            icon_open="https://www.netz39.de/open.png",
            icon_closed="https://www.netz39.de/closed.png"
        )
        entry.add_contact("email", "kontakt@netz39.de", is_issue_channel=True)
        entry.add_contact("twitter", "@netz39", is_issue_channel=True)
        entry.add_contact("ml", "list@netz39.de", is_issue_channel=True)
        entry.add_contact("jabber", "lounge@conference.jabber.n39.eu")
        entry.add_contact("discord", "https://discord.netz39.de/")
        entry.add_contact("github", "https://github.com/Netz39")
        entry.add_contact("mastodon", "https://machteburch.social/@netz39")
        entry.add_contact("youtube", "https://www.youtube.com/@Netz39De")        
        entry.add_contact("instagram", "https://www.instagram.com/netz_39/")

        entry.add_feed("blog", "rss", "https://www.netz39.de/feed.xml")
        entry.add_feed("calendar", "ical", "https://www.netz39.de/feed/eo-events/events.ics")

        return entry

    TEMPLATE = {
        "api": "0.13",
        "state": {
            "open": True,
            "lastchange": 0,
            "trigger_person": "",
            "message": "",
        },
        "contact": {},
        "issue_report_channels": [],
        "feeds": {}
    }

    def __init__(self, space, logo, url, address, lat, lon, icon_open, icon_closed):
        self.data = self.TEMPLATE.copy()
        self.data.update({
            "space": space,
            "logo": logo,
            "url": url,
            "location": {
                "address": address,
                "lat": lat,
                "lon": lon
            },
            "state": {
                "icon": {
                    "open": icon_open,
                    "closed": icon_closed
                }
            }
        })

    def add_contact(self, key, value, is_issue_channel=False):
        self.data["contact"][key] = value
        if is_issue_channel:
            self.data["issue_report_channels"].append(key)

    def add_feed(self, feed, schema, url):
        self.data["feeds"][feed] = {
            "type": schema,
            "url": url
        }

    def set_is_open(self, is_open):
        self.data["state"]["open"] = is_open

    def set_lastchange(self, lastchange):
        self.data["state"]["lastchange"] = lastchange

    def is_open(self):
        return self.data["state"]["open"]