import snap
import json
import re
import os
import sys
import argparse
import bz2
import utils.progress as progress
from subprocess import check_output
from markdown import markdown
from bs4 import BeautifulSoup
                    
def main():
    args = parse_args()

    print('Initializing mmnet...')
    mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids = read_mmnet(args['mmnet'])
    parse_comments(mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids, args['comment_directory'])

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
    srids_to_urls = {} # e.g. t5_2qgzg -> '/r/business/'
    subids_to_nids = {} # e.g. t3_64b3l -> (node id of submission within its subreddit mode)

    # Map subreddit ids to mode ids and submission ids to node ids
    MI = mmnet.BegModeNetI()
    while MI < mmnet.EndModeNetI():
        sr_id, sr_url = mmnet.GetModeName(MI.GetModeId()).split('|')[:2] # pushshift subreddit id (t3_xxx), url (/r/xxx)
        srids_to_urls[sr_id] = sr_url
        srids_to_submission_mids[sr_id] = MI.GetModeId()
        mode = MI.GetModeNet() # submission mode
        for NI in MI.GetModeNet().Nodes():
            subids_to_nids['t3_' + mode.GetStrAttrDatN(NI.GetId(), 'id')] = NI.GetId()
        MI.Next()

    # Make comment modes and crossnets
    for (sr_id, sr_url) in srids_to_urls.iteritems():
        comment_mid = mmnet.AddModeNet('{}|{}|comments'.format(sr_id, sr_url))
        srids_to_comment_mids[sr_id] = comment_mid
        comment_mode = mmnet.GetModeNetById(comment_mid)
        for ia in int_attrs:
            comment_mode.AddIntAttrN(ia)
        for sa in str_attrs:
            comment_mode.AddStrAttrN(sa)
        comment_crossnet = mmnet.AddCrossNet(comment_mid, srids_to_submission_mids[sr_id],
                                             '{}|{}|top_level_comments'.format(sr_id, sr_url))
        reply_crossnet = mmnet.AddCrossNet(comment_mid, comment_mid, '{}|{}|replies'.format(sr_id, sr_url), True)
        
    return mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids


def parse_comments(mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids, comdir):
    comfiles = []
    for fname in os.listdir(comdir):
        if fname.startswith('.') or fname.endswith('~'):
            continue
        path = os.path.join(comdir, fname)
        if os.path.isdir(path): # skip subdirectories
            continue
        comfiles.append(path)

    comids_to_nids = {} # comment id to node id in appropriate comment mode, e.g. t1_xxxxx -> 253
    print('Parsing comments...')
    for comfile in comfiles:
        print('\n' + comfile + ': fetching number of lines...')
        ncoms = sum(1 for l in bz2.BZ2File(comfile))

        print(comfile + ': parsing...')
        comments = (json.loads(line) for line in bz2.BZ2File(comfile))
        progress.init_progbar(ncoms)
        for com in comments:
            parse_one_comment(mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids, comids_to_nids, com)
            progress.report_progress()
        progress.report_finished()

        
def parse_one_comment(mmnet, srids_to_urls, srids_to_comment_mids, subids_to_nids, comids_to_nids, com):
    com_id = com['name']
    sr_id = com['subreddit_id'] # t5_xxxxx
    sub_id = com['link_id'] # t3_xxxxx
    parent_id = com['parent_id'] # t1_xxxxx (comment) if reply; t3_xxxxx (post) if top-level comment
    reply = parent_id.startswith('t1')
    
    # If subreddit, submission, or parent comment not in mmnet, ignore comment
#    print(sr_id)
#    print(srids_to_comment_mids)
#    print('')
#    print(sub_id)
#    print(subids_to_nids)
#    print('')
#    print(parent_id)
#    print(comids_to_nids)
#    print(reply)
#    raw_input()
    
    if sr_id not in srids_to_comment_mids or sub_id not in subids_to_nids \
       or (reply and parent_id not in comids_to_nids):
        return

    sr_url = srids_to_urls[sr_id]
    comment_mid = srids_to_comment_mids[sr_id]
    comment_mode = mmnet.GetModeNetById(comment_mid)
    
    # Add comment to comment mode; add attributes
    nid = comment_mode.AddNode()
    try:
        for ia in int_attrs:
            if ia in com and com[ia] != None:
                comment_mode.AddIntAttrDatN(nid, int(com[ia]), ia)
        for sa in str_attrs:
            if sa in com:
                if sa == 'body': # Convert markdown to plaintext
                    body_markdown = com[sa]
                    body_html = markdown(body_markdown)
                    body_plain = (BeautifulSoup(body_html, 'lxml').get_text().replace('\n', ' ')
                                  .encode('ascii', 'backslashreplace').lower())
                    comment_mode.AddStrAttrDatN(nid, body_plain, sa)
                elif sa == 'author': # Not case-sensitive; change to lowercase
                    comment_mode.AddStrAttrDatN(nid, com[sa], sa)
                else: # Case-sensitive; leave alone
                    comment_mode.AddStrAttrDatN(nid, com[sa], sa)
    except UnicodeEncodeError: # Comment unrepresentable in ascii; remove node and skip
        mode.DelNode(nid)
        return

#    print(com)
    # Add comment-parent edge to proper crossnet
    comids_to_nids[com_id] = nid
    crossnet = mmnet.GetCrossNetByName('{}|{}|{}'.format(sr_id, sr_url, 'replies' if reply else 'top_level_comments'))
    parent_nid = (comids_to_nids[parent_id] if reply else subids_to_nids[sub_id])
    crossnet.AddEdge(nid, parent_nid)
    
                    
if __name__ == '__main__':
    main()
