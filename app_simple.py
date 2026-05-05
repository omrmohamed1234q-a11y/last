import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import network_graph
import plot_3d
import heatmap
from data_utils import get_title_col, get_rating_col, get_num_cols

st.set_page_config(page_title="Phone Data Dashboard", layout="wide")

# our datasets
datasets = {
    "All Data (Noon + Amazon)": None,
    "Noon - Budget (10k-25k)": ("../data/noon_data/first_category.csv", ","),
    "Noon - Mid (25k-40k)": ("../data/noon_data/second_category.csv", ","),
    "Noon - High (40k+)": ("../data/noon_data/third_category.csv", ","),
    "Noon - Custom Scrape": ("../data/noon_data/noon_custom_scrape.csv", ","),
    "Amazon - All Ranges": ("../data/serpapi_data/Dif ranges serp.csv", ";"),
    "Amazon - Phones": ("../data/serpapi_data/amazon_phones (3).csv", ";"),
    "Amazon - Under 25k": ("../data/serpapi_data/10000 or 25000 serp.csv", ";"),
    "Amazon - 25k to 40k": ("../data/serpapi_data/25000 OR 40000 SERP.csv", ";"),
    "Amazon - Over 40k": ("../data/serpapi_data/More than 40000 serp.csv", ";"),
    "Amazon - Cleaned Data": ("../data/cleaned_phones_data.csv", ","),
    "Mobizil Reviews - Budget": ("../data/reviews/first_category_reviews.csv", ","),
    "Mobizil Reviews - Mid": ("../data/reviews/second_category_reviews.csv", ","),
    "Mobizil Reviews - High": ("../data/reviews/third_category_reviews.csv", ","),
}

# matching reviews for noon datasets
reviews_map = {
    "Noon - Budget (10k-25k)": "../data/reviews/first_category_reviews.csv",
    "Noon - Mid (25k-40k)": "../data/reviews/second_category_reviews.csv",
    "Noon - High (40k+)": "../data/reviews/third_category_reviews.csv",
}

st.title("Phone Data Dashboard")

selected = st.selectbox("Choose dataset:", list(datasets.keys()))

if selected == "All Data (Noon + Amazon)":
    # load all noon data
    noon1 = pd.read_csv("../data/noon_data/first_category.csv")
    noon1['source'] = 'Noon'
    noon2 = pd.read_csv("../data/noon_data/second_category.csv")
    noon2['source'] = 'Noon'
    noon3 = pd.read_csv("../data/noon_data/third_category.csv")
    noon3['source'] = 'Noon'
    noon4 = pd.read_csv("../data/noon_data/noon_custom_scrape.csv")
    noon4['source'] = 'Noon'

    # load all amazon data (serpapi uses name instead of title)
    amz_files = [
        ("../data/serpapi_data/Dif ranges serp.csv", ";"),
        ("../data/serpapi_data/amazon_phones (3).csv", ";"),
        ("../data/serpapi_data/10000 or 25000 serp.csv", ";"),
        ("../data/serpapi_data/25000 OR 40000 SERP.csv", ";"),
        ("../data/serpapi_data/More than 40000 serp.csv", ";"),
        ("../data/cleaned_phones_data.csv", ","),
    ]
    amz_list = []
    for f, s in amz_files:
        tmp = pd.read_csv(f, sep=s)
        # rename 'name' to 'title' so all data matches
        if 'name' in tmp.columns and 'title' not in tmp.columns:
            tmp = tmp.rename(columns={'name': 'title'})
        # rename 'ratings' to 'rating'
        if 'ratings' in tmp.columns and 'rating' not in tmp.columns:
            tmp = tmp.rename(columns={'ratings': 'rating'})
        tmp['source'] = 'Amazon'
        amz_list.append(tmp)

    # combine everything
    df = pd.concat([noon1, noon2, noon3, noon4] + amz_list, ignore_index=True)
    df = df.drop_duplicates(subset=['title'], keep='first')
else:
    path, sep = datasets[selected]
    df = pd.read_csv(path, sep=sep)

# figure out column names
title_col = get_title_col(df)
rat_col = get_rating_col(df)

# extract numeric columns using shared function
df, num_cols = get_num_cols(df)

st.markdown("---")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Data & Filters", "Network Graph", "3D Plot", "Heatmap", "Compare"])


# ---- TAB 1: DATA & FILTERS ----
with tab1:
    search = st.text_input("Search by phone name:")
    col1, col2 = st.columns(2)

    filtered = df.copy()

    if search:
        filtered = filtered[filtered[title_col].astype(str).str.contains(search, case=False, na=False)]

    if 'price_num' in filtered.columns:
        prices = filtered['price_num'].dropna()
        if len(prices) > 0 and prices.min() < prices.max():
            rng = col1.slider("Price (EGP):", int(prices.min()), int(prices.max()),
                              (int(prices.min()), int(prices.max())))
            filtered = filtered[(filtered['price_num'] >= rng[0]) & (filtered['price_num'] <= rng[1])]

    if 'brand' in filtered.columns:
        brands = sorted(filtered['brand'].dropna().unique().tolist())
        pick = col2.selectbox("Brand:", ["All"] + brands)
        if pick != "All":
            filtered = filtered[filtered['brand'] == pick]

    if 'seller' in filtered.columns:
        sellers = sorted(filtered['seller'].dropna().unique().tolist())
        pick_s = col2.selectbox("Seller:", ["All"] + sellers)
        if pick_s != "All":
            filtered = filtered[filtered['seller'] == pick_s]

    if 'rating_num' in filtered.columns:
        min_r = col1.number_input("Min Rating:", 0.0, 5.0, 0.0, 0.5)
        if min_r > 0:
            filtered = filtered[filtered['rating_num'] >= min_r]

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Products", len(filtered))
    if 'price_num' in filtered.columns:
        avg = filtered['price_num'].mean()
        if pd.notnull(avg):
            c2.metric("Avg Price", f"{avg:,.0f} EGP")
    if 'rating_num' in filtered.columns:
        avg_r = filtered['rating_num'].mean()
        if pd.notnull(avg_r):
            c3.metric("Avg Rating", f"{avg_r:.1f} / 5")

    # filter by source if All Data
    if 'source' in filtered.columns:
        sources = sorted(filtered['source'].dropna().unique().tolist())
        pick_src = col2.selectbox("Source:", ["All"] + sources)
        if pick_src != "All":
            filtered = filtered[filtered['source'] == pick_src]

    # show table with main columns only
    cols = [title_col]
    for c in ['price', rat_col, 'brand', 'seller', 'source']:
        if c and c in filtered.columns:
            cols.append(c)
    st.dataframe(filtered[cols], use_container_width=True)

    # show mobizil reviews if this is a noon dataset
    if selected in reviews_map:
        st.markdown("---")
        st.subheader("Mobizil Reviews")
        reviews_df = pd.read_csv(reviews_map[selected])
        st.write(f"Found {len(reviews_df)} reviews from Mobizil.")

        rev_search = st.text_input("Search reviews by model:")
        if rev_search:
            reviews_df = reviews_df[reviews_df['model_name'].astype(str).str.contains(rev_search, case=False, na=False)]

        for i, row in reviews_df.iterrows():
            with st.expander(row['model_name']):
                st.write("**Pros:**")
                st.write(str(row['pros']))
                st.write("**Cons:**")
                st.write(str(row['cons']))
                if pd.notnull(row.get('review_link')):
                    st.write(f"Source: {row['review_link']}")

    # bar charts
    st.markdown("---")
    st.subheader("Charts")
    chart1, chart2 = st.columns(2)

    # brand distribution
    if 'brand' in filtered.columns:
        with chart1:
            st.write("Products per Brand")
            brand_counts = filtered['brand'].value_counts().head(10)
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            brand_counts.plot(kind='bar', ax=ax1)
            ax1.set_ylabel("Count")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig1)

    # price distribution
    if 'price_num' in filtered.columns:
        with chart2:
            st.write("Price Distribution")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            filtered['price_num'].dropna().plot(kind='hist', bins=15, ax=ax2)
            ax2.set_xlabel("Price (EGP)")
            ax2.set_ylabel("Count")
            plt.tight_layout()
            st.pyplot(fig2)

    # download button
    st.markdown("---")
    csv_data = filtered[cols].to_csv(index=False)
    st.download_button("Download filtered data as CSV", csv_data, "filtered_phones.csv", "text/csv")
# ---- TAB 2: NETWORK GRAPH ----
with tab2:
    st.subheader("Network Graph")

    options = ["By Recommendations", "By Price Range", "By Rating", "By Brand"]
    if 'seller' in df.columns:
        options.append("By Seller")

    rel = st.selectbox("Relation:", options)

    p1, p2 = st.columns(2)
    tiers = 4
    min_rat = 0.0
    if rel == "By Price Range":
        tiers = p1.selectbox("Tiers:", [2, 3, 4], index=2)
    if rel == "By Rating":
        min_rat = p1.slider("Min rating:", 0.0, 5.0, 0.0, 0.5)

    if st.button("Build Graph"):
        if rel == "By Recommendations":
            edges = network_graph.recommendation_edges(df, title_col)
        elif rel == "By Price Range":
            edges = network_graph.price_edges(df, title_col, tiers)
        elif rel == "By Rating":
            edges = network_graph.rating_edges(df, title_col, rat_col, min_rat)
        elif rel == "By Brand":
            edges = network_graph.brand_edges(df, title_col)
        elif rel == "By Seller":
            edges = network_graph.seller_edges(df, title_col)

        if not edges:
            st.warning("No edges found.")
        else:
            G = network_graph.make_graph(edges)
            stats = network_graph.graph_stats(G)

            if stats is None:
                st.warning("Empty graph.")
            else:
                st.success(f"Built: {stats['nodes']} nodes, {stats['edges']} edges")

                s1, s2, s3 = st.columns(3)
                s1.metric("Density", f"{stats['density']:.4f}")
                s2.metric("Communities", stats['communities'])
                s3.metric("Max Degree", stats['max_degree'])

                st.write("Top 5 by Degree Centrality:")
                st.table(pd.DataFrame(stats['top_degree'], columns=["Node", "Score"]))

                st.write("Top 5 by Betweenness Centrality:")
                st.table(pd.DataFrame(stats['top_betweenness'], columns=["Node", "Score"]))

                net = network_graph.make_pyvis(G, stats)
                net.save_graph("graph.html")
                with open("graph.html", "r", encoding="utf-8") as f:
                    html = f.read()
                components.html(html, height=650)


# ---- TAB 3: 3D PLOT ----
with tab3:
    st.subheader("3D Scatter Plot")

    if len(num_cols) < 3:
        st.warning(f"Need 3 numeric columns, found: {num_cols}")
    else:
        a1, a2, a3 = st.columns(3)
        x = a1.selectbox("X:", num_cols, index=0)
        y = a2.selectbox("Y:", num_cols, index=1)
        z = a3.selectbox("Z:", num_cols, index=2)

        c1, c2 = st.columns(2)
        elev = c1.slider("Elevation:", -90, 90, 20)
        azim = c2.slider("Azimuth:", -180, 180, 30)

        fig = plot_3d.make_3d_plot(df, x, y, z, elev, azim)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("No data for these columns.")


# ---- TAB 4: HEATMAP ----
with tab4:
    st.subheader("Heatmap (KDE)")
    st.write("Distance-based Kernel Density Estimation heatmap from the data points.")

    if len(num_cols) < 2:
        st.warning("Need at least 2 numeric columns for heatmap.")
    else:
        h1, h2 = st.columns(2)
        x_col = h1.selectbox("X axis (heatmap):", num_cols, index=0)
        y_col = h2.selectbox("Y axis (heatmap):", num_cols, index=1 if len(num_cols) > 1 else 0)

        R = st.slider("Radius (R):", 0.1, 5000.0, 500.0, 0.1)
        grid_size = st.slider("Grid resolution:", 20, 200, 100)

        fig = heatmap.make_heatmap(df, x_col, y_col, R, grid_size)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("No data for these columns.")


# ---- TAB 5: COMPARE ----
with tab5:
    st.subheader("Compare Two Phones")

    titles = df[title_col].dropna().unique().tolist()
    titles.sort()

    if len(titles) < 2:
        st.warning("Need at least 2 products to compare.")
    else:
        cp1, cp2 = st.columns(2)
        phone1 = cp1.selectbox("Phone 1:", titles, index=0)
        phone2 = cp2.selectbox("Phone 2:", titles, index=min(1, len(titles)-1))

        row1 = df[df[title_col] == phone1].iloc[0]
        row2 = df[df[title_col] == phone2].iloc[0]

        # show comparison table
        compare_cols = [title_col]
        for c in ['price', rat_col, 'brand', 'seller', 'source', 'ram', 'memory_storage_capacity', 'storage', 'operating_system', 'screen_size']:
            if c and c in df.columns:
                compare_cols.append(c)

        compare_df = pd.DataFrame({
            "Field": compare_cols,
            phone1[:30]: [str(row1[c]) for c in compare_cols],
            phone2[:30]: [str(row2[c]) for c in compare_cols],
        })
        st.table(compare_df)
