import snap
import json
import re
import os
import sys
import argparse
import bz2
import utils.progress as progress
#from subprocess import check_output
#from markdown import markdown
#from bs4 import BeautifulSoup
                    
def main():
    args = parse_args()

    print('Initializing mmnet...')
    subreddit_metagraph = snap.TNEANet.Load(snap.TFIn(args['metagraph_file']))
    mmnet, srids_to_mids = setup_mmnet(subreddit_metagraph, args['previous_work'], args['top'], args['minsubs'])
    parse_submissions(mmnet, srids_to_mids, args['submission_directory'])

    print('Saving...')
    output = snap.TFOut(args['output_file'])
    mmnet.Save(output)
    output.Flush()
    print('Done')

# Handle command-line args
def parse_args():
    parser = argparse.ArgumentParser(description='Add submissions to Reddit mmnet.')
    parser.add_argument('metagraph_file', help='SNAP TNEANet file containing information about subreddits')
    parser.add_argument('submission_directory', help='Directory storing files from which to read submissions')
    parser.add_argument('output_file', help='Destination file for TMMNet')
    parser.add_argument('--previous_work', help='Existing TMMNet file; pick up from a TMMNet already created')
    parser.add_argument('--top', metavar='N', help='Only create MMNet using submissions from the top N subreddits'
                        + ' by subscriber count', type=int, default=0)
    parser.add_argument('--minsubs', metavar='M', help='Only create MMNet using subreddits with at least M'
                        + ' subscribers', type=int, default=0)
    args = parser.parse_args()
    return vars(args)

# If previous mmnet exists, load it. If new one, create its modes by reading the TNEANet of
# basic subreddit info. Also return dict mapping subreddit IDs to their submission mode IDs.
int_attrs = ['archived', 'created_utc', 'edited', 'gilded', 'is_self', 'num_comments',
             'num_crossposts', 'over_18', 'pinned', 'retrieved_on', 'score']
str_attrs = ['author', 'id', 'permalink', 'selftext', 'title', 'url']
def setup_mmnet(subreddit_metagraph, prev_mmnet_file, top, minsubs):
    acceptable = None
    if top > 0: # Only consider top N subreddits by subscriber count
        acceptable = set(sorted(((NI.GetId(), subreddit_metagraph.GetIntAttrDatN(NI, 'subscribers'))
                                for NI in subreddit_metagraph.Nodes()), key=(lambda (nid, subs): -subs))[:top])
        acceptable = [nid for (nid, subs) in acceptable]
        
    srids_to_mids = {}
    if prev_mmnet_file == None:
        mmnet = snap.TMMNet.New()
        for NI in subreddit_metagraph.Nodes():
            if subreddit_metagraph.GetIntAttrDatN(NI, 'subscribers') > minsubs \
               and (acceptable == None or NI.GetId() in acceptable):
                name = subreddit_metagraph.GetStrAttrDatN(NI, 'name') # e.g. t5_2y6r4, identifies subreddit throughout pushshift database
                url = subreddit_metagraph.GetStrAttrDatN(NI, 'url') # e.g. /r/politics, identifies subreddit on Reddit
                mode_id = mmnet.AddModeNet('{}|{}|submissions'.format(name, url))
                for ia in int_attrs:
                    mmnet.GetModeNetById(mode_id).AddIntAttrN(ia)
                for sa in str_attrs:
                    mmnet.GetModeNetById(mode_id).AddStrAttrN(sa)
                srids_to_mids[name] = mode_id
        return mmnet, srids_to_mids
    else:
        mmnet = snap.TMMNet.Load(snap.TFIn(prev_mmnet_file))
        MI = mmnet.BegModeNetI()
        while MI < mmnet.EndModeNetI():
            sr_name = MI.GetModeName().split('|')[0] # pushshift subreddit identifier
            srids_to_mids[sr_name] = MI.GetModeId()
            MI.Next()
        return mmnet, srids_to_mids

    
def parse_submissions(mmnet, srids_to_mids, subdir):
    subfiles = []
    for fname in os.listdir(subdir):
        if fname.startswith('.') or fname.endswith('~'):
            continue
        path = os.path.join(subdir, fname)
        if os.path.isdir(path): # skip subdirectories
            continue
        subfiles.append(path)

    print('Parsing submissions...')
    for subfile in subfiles:
        print('\n' + subfile + ': fetching number of lines...')
        nsubs = sum(1 for l in bz2.BZ2File(subfile))

        print(subfile + ': parsing...')
        submissions = (json.loads(line) for line in bz2.BZ2File(subfile))
        progress.init_progbar(nsubs)                    
        for sub in submissions:
            if sub['subreddit_id'] in srids_to_mids: # else, subreddit too small or post doesn't have subreddit
                parse_one_submission(mmnet, srids_to_mids, sub)
            progress.report_progress()
        progress.report_finished()


def parse_one_submission(mmnet, srids_to_mids, sub):
    mode = mmnet.GetModeNetById(srids_to_mids[sub['subreddit_id']])
    nid = mode.AddNode()
    
    try:
        for ia in int_attrs:
            if ia in sub:
                mode.AddIntAttrDatN(nid, int(sub[ia]), ia)

            for sa in str_attrs:
                if sa in sub:
                    if sa == 'selftext': # Parse to remove markdown
                        pass
                        # selftext_markdown = sub[sa]
                        # selftext_html = markdown(selftext_markdown)
                        # selftext_plain = (BeautifulSoup(selftext_html, 'lxml').get_text().replace('\n', ' ')
                        #                   .encode('ascii', 'backslashreplace').lower())
                        # mode.AddStrAttrDatN(nid, selftext_plain, sa)
                    elif sa in ('author', 'title', 'subreddit'): # Not case-sensitive; change to lowercase
                        mode.AddStrAttrDatN(nid, sub[sa].encode('ascii').lower(), sa)
                    else: # id, permalink (for post) or url (for content); case-sensitive
                        mode.AddStrAttrDatN(nid, sub[sa], sa)
    except UnicodeEncodeError: # Some part of submission wasn't representable in ascii. Remove node
        mode.DelNode(nid)
        
                    
if __name__ == '__main__':
    main()
