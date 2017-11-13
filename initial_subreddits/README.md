Create networks of subreddits.

Before using:
- install Stanford SNAP (https://snap.stanford.edu/snappy/)
- install BeautifulSoup (pip install beautifulsoup4)
- install Markdown (https://pypi.python.org/pypi/Markdown)

Data:
- http://files.pushshift.io/reddit/subreddits/
    - Download; leave as `subreddits.gz`
- http://files.pushshift.io/reddit/submissions/
    - Download bz2 files for desired submissions; leave zipped; place in their own folder
- http://files.pushshift.io/reddit/comments/
    - Download bz2 files for comments from same time frame as submissions; leave zipped; place in their own folder
 
Outputs:
- `python parse_subreddits.py` -> graph with approx. 1M nodes representing subreddits. No edges. Node attributes:
    - `created_utc` (`int`): UTC timestamp of craetion date
    - `subscribers` (`int`): \# of subscribers to subreddit
    - `description` (`str`): Plaintext of subreddit description
    - `id` (`str`): `t5_` + `id` is equal to the `name` field.
    - `lang` (`str`): Subreddit language. Most subreddits are in English (`en`).
    - `name` (`str`): Subreddit's identifier in the PushShift dataset.
    - `public_description` (`str`): Plaintext of brief subreddit description.
    - `submit_text` (`str`): Text shown to users about to make a submission.
    - `title` (`str`): HTML title tag.
    - `url` (`str`): Subreddit name, e.g. `/r/politics`
    - `desc_subreddits` (`str`): Space-separated list of subreddits mentioned in this subreddit's `description` field.
- `python add_mention_links.py` -> creates directed edges between nodes based on description mentions
- `python parse_submissions.py` -> create multimodal network with modes of subreddits and nodes of submissions. Node attributes in submission modes:
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
    - `id` (`str`): Reddit post id. `t3_` + `id` is the ID of the submission in the PushShift dataset. Prepend `https://reddit.com/` + `id` to link to the post on Reddit.
    - `author` (`str`): username that created post, converted to lowercase
    - `permalink` (`str`): Where to access the post; prepend `https://reddit.com` to `permalink` field to access post
    - `selftext` (`str`): Plaintext of self post, stripped of Markdown and converted to lowercase ascii
    - `title` (`str`): Title of post, lowercase ascii
    - `url` (`str`): URL of post content, for non-self posts
- `python parse_comments.py` -> Augment multimodal network from `parse_submissions.py` with modes of comments and crossnets/edges representing comment hierarchy. Node attributes in comment modes:
    - `controversiality` (`int`): Indicator for a comment's controversiality. 0 if not flagged as controversial by reddit; 1 if flagged controversial.
    - `retrieved_on` (`int`): UTC timestamp for date of comment retrieval into PushShift dataset.
    - `distinguished` (`int`): 1 if mod has chosen to highlight the fact that comment was made by mod; 0 otherwise
    - `ups` (`int`): Number of upvotes on comment.
    - `downs` (`int`): Number of downvotes on comment.
    - `score` (`int`): Comment score.
    - `archived` (`int`): 1 if comment archived, 0 otherwise
    - `created_utc` (`int`): UTC timestamp for date of comment posting
    - `gilded` (`int`): Amount of gold the comment has received
    - `edited` (`int`): 1 if edited, 0 otherwise
    - `name` (`str`): Comment ID in PushShift dataset. Begins with `t1_`.
    - `body` (`str`): Plaintext of comment text.
    - `subreddit_id` (`str`): PushShift ID of subreddit in which comment was made; begins with `t5_`
    - `link_id` (`str`): PushShift ID of submission on which comment appears; begins with `t3_`
    - `parent_id` (`str`): PushShift ID of "parent" of comment. If comment was top-level, this is equal to `link_id`; otherwise, it is equal to the `name` of the comment to which this one is a reply
    - `author` (`str`): Username that created the post, in lowercase
    
