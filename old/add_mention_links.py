import snap
from pprint import pprint

def main():
    graph = snap.TNEANet.Load(snap.TFIn('subreddits_basic.graph'))
    titles_to_ids = {}
    titles_to_subs = {}
    
    for NI in graph.Nodes():
        srname = graph.GetStrAttrDatN(NI, 'url')
        titles_to_ids[srname] = NI.GetId()
        titles_to_subs[srname] = graph.GetIntAttrDatN(NI, 'subscribers')
    for NI in graph.Nodes():
        for srname in graph.GetStrAttrDatN(NI, 'desc_subreddits').split():
            if srname in titles_to_ids:
                graph.AddEdge(NI.GetId(), titles_to_ids[srname])

    print('Mention graph has {} nodes and {} edges'.format(graph.GetNodes(), graph.GetEdges()))
    print('Mention graph clustering coefficient: {}'.format(snap.GetClustCf(graph)))
    
    prankh = snap.TIntFltH()
    snap.GetPageRank(graph, prankh)
    ranks = sorted([(prankh[nid], nid) for nid in prankh])
    print('Top 50 mention graph PageRanks:')
    print('Node ID\tSubreddit\tPageRank')
    for (prank, nid) in ranks[-50:][::-1]:
        print('{:10}\t{:30}\t{:10}'.format(nid, graph.GetStrAttrDatN(nid, 'url'), prank))
    print('')
    
    print('Top 50 subscriber counts:')
    print('Node ID\tSubreddit\tSubscribers')
    for (title, nsubs) in sorted(titles_to_subs.items(), key=lambda tup: -tup[1])[:50]:
        print('{:10}\t{:30}\t{:10}'.format(titles_to_ids[title], title, nsubs))

    out = snap.TFOut('subreddits_with_desc_mentions.graph')
    graph.Save(out)
    out.Flush()
    
    

if __name__ == '__main__':
    main()
