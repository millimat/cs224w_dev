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
    - `created_utc` (`int`): UTC timestamp of creation date
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
- `Submissions and Comments to Tables.ipynb` will use the output of `parse_subreddit.py` and the PushShift comment/submission data to write all relevant submission and comment data into tab-separated .txt files. Submission and comment files contain: author; subreddit/post/comment/ids; upvotes, downvotes, scores, and gold; creation timestamps; and associated text for NLP.
- `Tables to Post-Comment TNEANets.ipynb` will use the .txt files to create one TNEANet per subreddit containing nodes for all of the comments and posts captured from that subreddit. Node attributes:
    - `score` (`int`): Comment or post score
    - `gilded` (`int`): Number of times post or comment received Reddit Gold
    - `created_utc` (`int`): Post or comment creation timestamp; seconds after Jan 01 1970 00:00 UTC
    - `author` (`str`): Reddit username of post or comment author, in lowercase
    - `text` (`str`): Title of post (plaintext) or text of comment (markdown)
    - `id` (`str`): Reddit ID of the post (starts with `t3_`) or comment (starts with `t1_`)
- `Tables to User-User Graphs.ipynb` will use the .txt files to create two TNEANets and two TNGraphs representing comments between users on Reddit. The TNEANets contain one directed edge from comment author to comment recipient (parent commenter or parent poster) for each comment captured in the .txt table. The TNGraphs disallow multi-edges, so if user A has made multiple comments in response to user B, there will only be one A->B edge. The `_nodelete` TNEANet does not create a node for the `[deleted]` placeholder user, nor does it add edges for any comments whose author or recipient is `[deleted]` or whose text is `[deleted]` or `[removed]`. The `_nodelete` TNGraph does not create a node for the `[deleted]` placeholder user, but it does add edges for comments whose text is `[deleted]` or `[removed]`.
    - TNEANet node attributes:
        - `username` (`str`): The user the node represents
    - TNEANet edge attributes:
        - `score` (`int`)
        - `gilded` (`int`)
        - `created_utc` (`int`)
        - `comment_id` (`str`)
        - `subreddit` (`str`)
