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
                    
def main():
    args = parse_args()

    print('Initializing mmnet...')
    mmnet, srids_to_submission_mids, srids_to_comment_mids, subids_to_nids = read_mmnet(args['mmnet'])
    parse_comments(mmnet, srids_to_mids, args['comment_directory'])

    print('Saving...')
    output = snap.TFOut(args['output_file'])
    mmnet.Save(output)
    output.Flush()
    print('Done')

# Handle command-line args
def parse_args():
    parser = argparse.ArgumentParser(description='Add comments to Reddit mmnet.')
    parser.add_argument('mmnet', help='SNAP TMMNet file containing info about subreddit submissions')
    parser.add_argument('comment_directory', help='Directory storing files from which to read comments')
    parser.add_argument('output_file', help='Destination file for TMMNet')
    args = parser.parse_args()
    return vars(args)

# Load mmnet with submission info. Add modes for comments, and comment crossnets.
int_attrs = ['controversiality', 'retrieved_on', 'distinguished', 'ups', 'downs', 'score',
             'archived', 'created_utc', 'gilded', 'edited']
str_attrs = ['name', 'body', 'subreddit_id', 'link_id', 'parent_id', 'author']
def read_mmnet(mmnetfile):
    mmnet = snap.TMMNet.Load(snap.TFIn(mmnetfile))
    srids_to_submission_mids = {} # e.g. t5_2qgzg -> (submission mode id of /r/business)
    srids_to_comment_mids = {} # e.g. t5_2qgzg -> (comment mode id of /r/business)
    subids_to_nids = {} # e.g. t3_64b3l -> (node id of submission within its subreddit mode)

    # Map subreddit ids to mode ids and submission ids to node ids
    sr_ids_urls = []
    MI = mmnet.BegModeNetI()
    while MI < mmnet.EndModeNetI():
        sr_id, sr_url = mmnet.GetModeName(MI.GetModeId()).split('|')[:1] # pushshift subreddit id (t3_xxx), url (/r/xxx)
        sr_ids_urls.append((sr_id, sr_url))
        srids_to_mids[sr_id] = MI.GetModeId()
        mode = MI.GetModeNet() # submission mode
        for NI in MI.GetModeNet().Nodes():
            subids_to_nids[mode.GetStrAttrDatN(NI, 'id')] = NI.GetId()
        MI.Next()

    # Make comment modes and crossnets
    for (sr_id, sr_url) in sr_ids_urls:
        comment_mid = mmnet.AddModeNet('{}|{}|comments'.format(sr_id, sr_url))
        comment_mode = mmnet.GetModeNetById(comment_mid)
        for ia in int_attrs:
            comment_mode.AddIntAttrN(ia)
        for sa in str_attrs:
            comment_mode.AddStrAttrN(sa)

        comment_crossnet = mmnet.AddCrossNet(comment_mid, srids_to_submission_mids[sr_id],
                                             '{}|{}|top_level_comments'.format(sr_id, sr_url))
        reply_crossnet = mmnet.AddCrossNet(comment_mid, comment_mid, '{}|{}|replies'.format(sr_id, sr_url), True)
        
    return mmnet, srids_to_submission_mids, srids_to_comment_mids, subids_to_nids

    
# def parse_submissions(mmnet, srids_to_mids, subdir):
#     subfiles = []
#     for fname in os.listdir(subdir):
#         path = os.path.join(subdir, fname)
#         if os.path.isdir(path): # skip subdirectories
#             continue
#         subfiles.append(path)

#     print('Parsing submissions...')
#     for subfile in subfiles:
#         submissions = (json.loads(line) for line in open(subfile))
#         nsubs = int(check_output(['wc', '-l', subfile]).split()[0])
        
#         progress.init_progbar(nsubs)                    
#         print(subfile)
#         for sub in submissions:
#             if sub['subreddit_id'] not in srids_to_mids: # Subreddit too small or post doesn't have subreddit
#                 progress.report_progress()
#             else:
#                 try:
#                     parse_one_submission(mmnet, srids_to_mids, sub)
#                 except UnicodeEncodeError: # Some part of submission not representable in ascii. Skip
#                     pass
#                 progress.report_progress()
#         progress.report_finished()


# def parse_one_submission(mmnet, srids_to_mids, sub):
#     mode = mmnet.GetModeNetById(srids_to_mids[sub['subreddit_id']])
#     nid = mode.AddNode()
        
#     for ia in int_attrs:
#         if ia in sub:
#             mode.AddIntAttrDatN(nid, int(sub[ia]), ia)
                
#         for sa in str_attrs:
#             if sa in sub:
#                 if sa == 'selftext': # Parse to remove markdown
#                     selftext_markdown = sub[sa]
#                     selftext_html = markdown(selftext_markdown)
#                     selftext_plain = (BeautifulSoup(selftext_html, 'lxml').get_text().replace('\n', ' ')
#                                       .encode('ascii', 'backslashreplace').lower())
#                     mode.AddStrAttrDatN(nid, selftext_plain, sa)
#                 elif sa in ('author', 'title', 'subreddit'): # Not case-sensitive; change to lowercase
#                     mode.AddStrAttrDatN(nid, sub[sa].encode('ascii').lower(), sa)
#                 else: # id (post) permalink or (content) url; case-sensitive
#                     mode.AddStrAttrDatN(nid, sub[sa], sa)

                    
if __name__ == '__main__':
    main()
