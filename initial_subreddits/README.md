Create basic network of subreddits.

Before using:
- install Stanford SNAP (https://snap.stanford.edu/snappy/)
- install BeautifulSoup (pip install beautifulsoup4)
- install Markdown (https://pypi.python.org/pypi/Markdown)

Data:
- http://files.pushshift.io/reddit/subreddits/
  Download, unzip, and rename to subreddits.json

Outputs:
- python parse_subreddits.py -> graph with >1M nodes representing subreddits. No edges. Node attributes:
    - # of subscribers (subscribers, int)
    - # UTC timestamp of creation date (created_utc, int)
    - Plaintext of subreddit description (description, str)
    - ID in pushshift database (id, str)
    - Language (lang, str)
    - Another ID? (name, str)
    - Plaintext of brief description (public_description, str)
    - Text shown to users about to make a submission (submit_text, str)
    - HTML title tag (title, str)
    - Subreddit name, e.g. /r/politics/ (url, str)
    - Space-separated list of subreddits mentioned in this one's description (desc_subreddits, str)
- python add_mention_links.py -> creates directed edges between nodes based on description mentions
  

