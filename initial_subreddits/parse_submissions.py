import snap
import json
import re
import os
import sys
import argparse
import utils.progress as progress
from subprocess import check_output
from markdown import markdown
from bs4 import BeautifulSoup

def parse_args():
    parser = argparse.ArgumentParser(description='Add submissions to Reddit mmnet.')
    parser.add_argument('metagraph_file')
    parser.add_argument('submission_directory')
    parser.add_argument('output_file')
    parser.add_argument('--previous_work')
    args = parser.parse_args()
    return vars(args)

# If previous mmnet exists, load it. If new one, create its modes by reading the TNEANet of
# basic subreddit info. Also return dict mapping subreddit IDs to their submission mode IDs.
def setup_mmnet(subreddit_metagraph, prev_mmnet_file):
    srids_to_mids 
    if prev_mmnet_file == None:
        mmnet = snap.TMMNet.New()
        for NI in subreddit_metagraph.Nodes():
            if subreddit_metagraph.GetIntAttrDatN(NI, 'subscribers') > 0:
                name = graph.GetStrAttrDatN(NI, 'name') # e.g. t5_2y6r4, identifies subreddit throughout pushshift database
                url = graph.GetStrAttrDatN(NI, 'url') # e.g. /r/politics, identifies subreddit on Reddit
                mode_id = mmnet.AddModeNet('{}|{}|submissions'.format(name, url))
                
            
    mmnet = (snap.TMMNet.Load(snap.TFIn(prev_mmnet_file)) if prev_mmnet_file != None else snap.TMMNet.New())
            
            


def main():
    args = parse_args()

    print('Initializing mmnet...')
    subreddit_metagraph = snap.TNEANet.Load(snap.TFIn(args['metagraph_file']))
    mmnet, srids_to_mids = setup_mmnet(subreddit_metagraph, args['previous_work'])
    
    
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
def setup_mmnet():
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
