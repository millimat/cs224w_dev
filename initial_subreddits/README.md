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
- `Submissions and Comments to Tables.ipynb` will write all submissions and comments whose PushShift files are in the desired directory into .tsv files. Submission and comment files contain author; subreddit/post/comment/ids; upvotes, downvotes, scores, and gold; creation timestamps; and associated text for NLP. 
