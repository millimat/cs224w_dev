Create networks of subreddits.

Before using:
- install Stanford SNAP (https://snap.stanford.edu/snappy/)
- install BeautifulSoup (pip install beautifulsoup4)
- install Markdown (https://pypi.python.org/pypi/Markdown)

Data:
- http://files.pushshift.io/reddit/subreddits/
    - Download, unzip, and rename to subreddits.json
- http://files.pushshift.io/reddit/submissions/
    - Download desired submissions, unzip, place in their own folder
 
Outputs:
- python parse_subreddits.py -> graph with >1M nodes representing subreddits. No edges. Node attributes:
    - \# of subscribers (subscribers, int)
    - \# UTC timestamp of creation date (created_utc, int)
    - Plaintext of subreddit description (description, str)
    - Subreddit ID (id, str)
    - Language (lang, str)
    - Subreddit ID in PushShift dataset (name, str)
    - Plaintext of brief description (public_description, str)
    - Text shown to users about to make a submission (submit_text, str)
    - HTML title tag (title, str)
    - Subreddit name, e.g. /r/politics/ (url, str)
    - Space-separated list of subreddits mentioned in this one's description (desc_subreddits, str)
- python add_mention_links.py -> creates directed edges between nodes based on description mentions
- python parse_submissions.py -> create multimodal network with modes of subreddits and nodes of submissions. Node attributes in submission modes:
    - `archived` (`int`): 1 if post archived, 0 otherwise
    - `created_utc` (`int`): UTC timestamp for post
    - `distinguished` (`int`): 1 if mod has chosen to highlight the fact that post was made by mod; 0 otherwise
    - `edited` (`int`): 1 if post was edited, 0 otherwise
    - `gilded` (`int`): Amount of gold post has received
    - `is_self` (`int`): 1 if post is a text/self-post, 0 otherwise
    - `num_comments` (`int`): number of comments on post
    - `over_18` (`int`): 1 if post marked as containing adult content, 0 otherwise
    - `pinned` (`int`): 1 if post was pinned by a mod, 0 otherwise
    - `retrieved_on` (`int`): UTC timestamp for date of post retrieval
    - `score` (`int`): Post score    
    - `id` (`str`): Reddit post id. `t3_` + `id` is the ID of the submission in the PushShift dataset. `reddit.com/` + `id` will link to the post on Reddit.
    - `author` (`str`): username that created post, converted to lowercase
    - `permalink` (`str`): Where to access the post; prepend `https://reddit.com` to `permalink` field to access post
    - `selftext` (`str`): Plaintext of self post, stripped of Markdown and converted to lowercase ascii
    - `title` (`str`): Title of post, lowercase ascii
    - `url` (`str`): URL of post content, for non-self posts
