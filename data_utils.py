import pandas as pd


def get_title_col(df):
    if 'title' in df.columns:
        return 'title'
    return 'name'


def get_rating_col(df):
    if 'rating' in df.columns:
        return 'rating'
    elif 'ratings' in df.columns:
        return 'ratings'
    return None


def shorten(title, n=4):
    words = str(title).split()
    if len(words) >= n:
        return " ".join(words[:n])
    return str(title)


def clean_num(val):
    # keep only digits and dots from a string
    clean = ""
    for ch in str(val):
        if ch.isdigit() or ch == '.':
            clean += ch
    if clean:
        try:
            return float(clean)
        except:
            return None
    return None


def get_num_cols(df):
    num_cols = []

    # price
    if 'price' in df.columns:
        df['price_num'] = df['price'].apply(clean_num)
    if 'price_num' in df.columns:
        num_cols.append('price_num')

    # rating
    rat_col = get_rating_col(df)
    if rat_col:
        df['rating_num'] = df[rat_col].apply(clean_num)
    if 'rating_num' in df.columns:
        num_cols.append('rating_num')

    # ram
    if 'ram' in df.columns:
        df['ram_num'] = pd.to_numeric(df['ram'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
        if df['ram_num'].notna().sum() > 0:
            num_cols.append('ram_num')

    # storage
    if 'memory_storage_capacity' in df.columns:
        df['storage_num'] = pd.to_numeric(df['memory_storage_capacity'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
        if df['storage_num'].notna().sum() > 0:
            num_cols.append('storage_num')
    elif 'storage' in df.columns:
        df['storage_num'] = pd.to_numeric(df['storage'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
        if df['storage_num'].notna().sum() > 0:
            num_cols.append('storage_num')

    # noon specs
    if 'specifications' in df.columns:
        if 'ram_num' not in num_cols:
            df['ram_num'] = pd.to_numeric(df['specifications'].astype(str).str.extract(r'RAM Size:\s*(\d+)')[0], errors='coerce')
            if df['ram_num'].notna().sum() > 0:
                num_cols.append('ram_num')
        if 'storage_num' not in num_cols:
            df['storage_num'] = pd.to_numeric(df['specifications'].astype(str).str.extract(r'Internal Memory:\s*(\d+)')[0], errors='coerce')
            if df['storage_num'].notna().sum() > 0:
                num_cols.append('storage_num')

    num_cols = list(dict.fromkeys(num_cols))
    return df, num_cols
