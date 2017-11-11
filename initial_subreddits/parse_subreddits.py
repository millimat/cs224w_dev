import snap
import json
import re
import utils.progress as progress
from subprocess import check_output
from markdown import markdown
from bs4 import BeautifulSoup

def main():
    subreddit_file = 'subreddits.json'
    nsubreddits = int(check_output(['wc', '-l', subreddit_file]).split()[0])
    subreddits = (json.loads(line) for line in open(subreddit_file))
    graph = setup_graph()

    print('Parsing {}...'.format(subreddit_file))
    progress.init_progbar(nsubreddits)
    for s in subreddits:
        parse_subreddit(s, graph)
        progress.report_progress()
    progress.report_finished()

    print('Saving...')
    output = snap.TFOut('subreddits_basic.graph')
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
        if not sr[sa]:
            continue
        if sa not in ['description', 'public_description']:
            graph.AddStrAttrDatN(nid, sr[sa].lower(), sa) # Convert text to lowercase
        else:
            # parse description; convert markdown to plaintext; convert EOLs to spaces; convert text to lowercase
            desc_markdown = sr[sa].replace('&gt;', '') # Catch HTML in /r/fantasypl
            desc_html = markdown(desc_markdown)
            
            # TODO: decide how to handle unicode chars
            desc_plaintext = (BeautifulSoup(desc_html, 'lxml').get_text())
            desc_plaintext = desc_plaintext.replace('\n', ' ').encode('ascii', 'backslashreplace').lower()
            graph.AddStrAttrDatN(nid, desc_plaintext, sa)

            if sa == 'description':
                # Get a list of subreddits this one mentions
                mentioned_subreddits = set()
                for tok in desc_plaintext.split():
                    if tok.startswith('/r/'): # Get name by removing punctuation or garbage at the end
                        mentioned_subreddit_name = re.split('[^a-zA-Z_]',tok[3:])[0] # get [a-zA-Z_] chars after '/r/'
                        mentioned_subreddits.add('/r/' + mentioned_subreddit_name + '/')
                graph.AddStrAttrDatN(nid, ' '.join(tok for tok in mentioned_subreddits), 'desc_subreddits')

                
if __name__ == '__main__':
    main()
