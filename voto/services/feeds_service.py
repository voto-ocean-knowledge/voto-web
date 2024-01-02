import datetime
import pytz
from feedgen.feed import FeedGenerator
from pathlib import Path
import yaml

updates_dir = Path(__file__).parent.parent.parent.parent.absolute() / "data_updates"


class Update:
    def __init__(self):
        super().__init__()


def get_news():
    updates = []
    update_files = list(updates_dir.glob("*.yml"))
    update_files.sort(reverse=True)
    for fn in update_files:
        with open(fn) as fin:
            yml = yaml.safe_load(fin)
        date_str = yml["date"]
        parts = date_str.split("-")
        date = datetime.datetime(
            int(parts[0]), int(parts[1]), int(parts[2])
        ).astimezone(pytz.timezone("Europe/Stockholm"))
        article = Update()
        article.title = f"{date_str}: {yml['title']}"
        article.url = (
            f"https://observations.voiceoftheocean.org/data/updates.html#{date_str}"
        )
        article.content = yml["content"]
        article.id = article.title  # Or: fe.guid(article.url, permalink=True)
        article.author_name = "Callum Rollo"
        article.author_email = "callum.rollo@voiceoftheocean.org"
        article.created_at = date
        updates.append(article)
    return updates


def news_xml(articles):
    fg = FeedGenerator()
    fg.id("https://observations.voiceoftheocean.org/feed.xml")
    fg.title("Voice of the Ocean observations portal data change log")
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


if __name__ == "__main__":
    articles = get_news()
    news_xml(articles)
