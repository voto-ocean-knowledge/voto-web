import datetime
import pytz
from feedgen.feed import FeedGenerator


class Update:
    def __init__(self):
        super().__init__()


def get_news():
    updates = []
    for i in range(5):
        date = datetime.datetime.now(tz=pytz.timezone("Europe/Stockholm"))
        date_str = str(date)[:10]
        article = Update()
        article.title = f"{date_str}: {i}"
        article.url = (
            f"https://observations.voiceoftheocean.org/data/updates.html#{date_str}"
        )
        article.content = "blah blah"
        article.id = article.title  # Or: fe.guid(article.url, permalink=True)
        article.author_name = "callum"
        article.author_email = "callum@voice.com"
        article.created_at = date
        updates.append(article)
    return updates


def news_xml(articles):
    fg = FeedGenerator()
    fg.id("https://observations.voiceoftheocean.org/feed.xml")
    fg.title("Voice of the Ocean observations portal data changelog")
    fg.description(
        "An RSS feed to announce changes in Voice of the Ocean datasets and processing"
    )
    fg.author({"name": "Callum Rollo", "email": "callum.rollo@voiceoftheocean.org"})
    fg.logo("https://observations.voiceoftheocean.org/static/favicon.ico")
    fg.link(href="https://observations.voiceoftheocean.org/feed.xml", rel="self")
    fg.link(href="https://observations.voiceoftheocean.org", rel="alternate")
    fg.language("en")
    for article in articles:
        fe = fg.add_entry()
        fe.title(article.title)
        fe.link(href=article.url)
        fe.description(article.content)
        fe.guid(article.id, permalink=False)
        fe.author(name=article.author_name, email=article.author_email)
        fe.pubDate(article.created_at)
    rssfeed = fg.rss_str(pretty=True)
    return rssfeed
