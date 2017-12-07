import snap
import json
import re
import gzip
import utils.progress as progress
from markdown import markdown
from bs4 import BeautifulSoup

def main():
    subreddit_file = 'data/subreddits.gz'
    print('Fetching number of lines in ' + subreddit_file + '...')
    nsubreddits = sum(1 for l in gzip.open(subreddit_file))
    subreddits = (json.loads(line) for line in gzip.open(subreddit_file))
    graph = setup_graph()

    print('Parsing {}...'.format(subreddit_file))
    progress.init_progbar(nsubreddits)
    for s in subreddits:
        parse_subreddit(s, graph)
        progress.report_progress()
    progress.report_finished()

    print('Saving...')
    output = snap.TFOut('output/subreddits.graph')
    graph.Save(output)
    output.Flush()
    print('Done')
    
strattrs = ['description', 'id', 'lang', 'name', 'public_description', 'submit_text', 'title', 'url']
def setup_graph():
    graph = snap.TNEANet.New()
    graph.AddIntAttrN('subscribers')
    for sa in strattrs:
        graph.AddStrAttrN(sa)
    return graph

def parse_subreddit(sr, graph):
    nid = graph.AddNode()
    graph.AddIntAttrDatN(nid, sr['subscribers'], 'subscribers')
    graph.AddIntAttrDatN(nid, sr['created_utc'], 'created_utc')
    for sa in strattrs:
        if not sr[sa]: # |None| in field
            continue
        graph.AddStrAttrDatN(nid, sr[sa].lower(), sa) # Convert text to lowercase
                
if __name__ == '__main__':
    main()
