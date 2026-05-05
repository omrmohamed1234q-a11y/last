import networkx as nx
from pyvis.network import Network
from networkx.algorithms import community
from data_utils import shorten, clean_num


def recommendation_edges(df, title_col):
    if 'recommendations' in df.columns:
        rec_col = 'recommendations'
    elif 'related_items' in df.columns:
        rec_col = 'related_items'
    else:
        return []

    edges = []
    for i, row in df.iterrows():
        main = shorten(row[title_col])
        if main == 'nan':
            continue

        recs = str(row[rec_col])
        if recs == 'nan' or 'No recommendations' in recs:
            continue

        clean = recs.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        for r in clean.split(","):
            r = r.strip()
            if r and r != 'No recommendations':
                edges.append((main, shorten(r)))

    return edges


def price_edges(df, title_col, tiers=4):
    edges = []
    if 'price' not in df.columns:
        return edges

    for i, row in df.iterrows():
        main = shorten(row[title_col])
        if main == 'nan':
            continue

        price = clean_num(row['price'])
        if price is None:
            continue

        if tiers == 4:
            if price < 10000:
                tier = "Budget (< 10k)"
            elif price < 20000:
                tier = "Mid-Range (10k-20k)"
            elif price < 40000:
                tier = "High-End (20k-40k)"
            else:
                tier = "Flagship (40k+)"
        elif tiers == 3:
            if price < 15000:
                tier = "Low (< 15k)"
            elif price < 35000:
                tier = "Medium (15k-35k)"
            else:
                tier = "High (35k+)"
        else:
            if price < 25000:
                tier = "Under 25k"
            else:
                tier = "Over 25k"
        edges.append((main, tier))

    return edges


def rating_edges(df, title_col, rat_col, min_rating=0):
    if rat_col is None:
        return []

    edges = []
    for i, row in df.iterrows():
        main = shorten(row[title_col])
        if main == 'nan':
            continue

        rating = clean_num(row[rat_col])
        if rating is None:
            continue
        if rating < min_rating:
            continue

        if rating >= 4.5:
            tier = "Top Rated (4.5-5.0)"
        elif rating >= 4.0:
            tier = "Great (4.0-4.4)"
        elif rating >= 3.0:
            tier = "Average (3.0-3.9)"
        else:
            tier = "Poor (< 3.0)"
        edges.append((main, tier))

    return edges


def brand_edges(df, title_col):
    edges = []

    if 'brand' in df.columns:
        for i, row in df.iterrows():
            main = shorten(row[title_col])
            brand = str(row['brand']).strip()
            if main != 'nan' and brand != 'nan' and brand != '':
                edges.append((main, brand))
    else:
        for i, row in df.iterrows():
            title = str(row[title_col])
            if title == 'nan':
                continue
            main = shorten(title)
            brand = title.split()[0]
            if brand:
                edges.append((main, brand))
    return edges


def seller_edges(df, title_col):
    edges = []
    if 'seller' not in df.columns:
        return edges

    for i, row in df.iterrows():
        main = shorten(row[title_col])
        seller = str(row['seller']).strip()
        if main != 'nan' and seller != 'nan' and seller != '':
            edges.append((main, seller))
    return edges


def make_graph(edges):
    G = nx.Graph()
    G.add_edges_from(set(edges))
    return G


def graph_stats(G):
    if len(G.nodes) == 0:
        return None

    density = nx.density(G)
    deg = nx.degree_centrality(G)
    bet = nx.betweenness_centrality(G)
    comms = list(community.greedy_modularity_communities(G))
    max_deg = max(dict(G.degree()).values())

    top_deg = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:5]
    top_bet = sorted(bet.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "nodes": len(G.nodes),
        "edges": len(G.edges),
        "density": density,
        "communities": len(comms),
        "max_degree": max_deg,
        "top_degree": top_deg,
        "top_betweenness": top_bet,
        "comms": comms,
        "deg": deg,
    }


def make_pyvis(G, stats):
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'pink', 'yellow']
    node_color = {}
    for i, comm in enumerate(stats["comms"]):
        for node in comm:
            node_color[node] = colors[i % len(colors)]

    deg = stats["deg"]
    max_val = max(deg.values()) if deg else 1

    for node in G.nodes():
        G.nodes[node]['size'] = (deg[node] / max_val) * 35 + 10
        G.nodes[node]['color'] = node_color.get(node, 'white')

    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    net.barnes_hut(gravity=-5000, spring_length=150)
    net.from_nx(G)
    return net
