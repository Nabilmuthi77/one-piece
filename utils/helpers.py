import re
import requests
from constants import (
    DEVIL_FRUITS_API_URL,
    GAME_MODE_EASY_EXACT,
    GAME_MODE_HARD_EXACT,
    GAME_MODE_HARD_PATTERNS,
    GAME_MODE_MEDIUM_KEYWORDS
)

DEVIL_FRUIT_TYPES = {
    # Fallback alias jika diperlukan
    "gomu gomu no mi": "Zoan",
    "gomu-gomu no mi": "Zoan",
}


def load_devil_fruits_types():
    global DEVIL_FRUIT_TYPES
    import os, json
    data = None
    cached_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'devil_fruits.json')

    # Load from local cache first for instant startup
    if os.path.exists(cached_file):
        try:
            with open(cached_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass

    # Fetch updated data from network with browser User-Agent
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(DEVIL_FRUITS_API_URL, headers=headers, timeout=5)
        if resp.status_code == 200:
            net_data = resp.json()
            if net_data:
                data = net_data
                try:
                    os.makedirs(os.path.dirname(cached_file), exist_ok=True)
                    with open(cached_file, 'w', encoding='utf-8') as f:
                        json.dump(net_data, f)
                except Exception:
                    pass
    except Exception:
        # Gracefully rely on local cache if network is unreachable
        pass

    if not data and os.path.exists(cached_file):
        try:
            with open(cached_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass

    if data:
        for item in data:
            name = item.get('name', '').strip()
            f_type = item.get('type', '').strip()
            if name and f_type:
                clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', name, flags=re.IGNORECASE).strip()
                DEVIL_FRUIT_TYPES[clean.casefold()] = f_type
                base = clean.split(',')[0].strip()
                if base.casefold() not in DEVIL_FRUIT_TYPES:
                    DEVIL_FRUIT_TYPES[base.casefold()] = f_type


def get_devil_fruit_type(fruit_name):
    if not fruit_name:
        return None
    clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', str(fruit_name), flags=re.IGNORECASE).strip()
    if 'SMILE' in clean.upper() or 'ZOAN' in clean.upper() or 'MODEL:' in clean.upper():
        return 'Zoan'
    cf = clean.casefold()
    if cf in DEVIL_FRUIT_TYPES:
        return DEVIL_FRUIT_TYPES[cf]
    base = clean.split(',')[0].strip().casefold()
    if base in DEVIL_FRUIT_TYPES:
        return DEVIL_FRUIT_TYPES[base]
    return None


def get_story_arc(chapter_str):
    if not chapter_str:
        return 'Unknown'
    match = re.search(r'Chapter\s+(\d+)', chapter_str)
    if not match:
        return 'SBS & Extras'
    ch = int(match.group(1))
    if ch >= 1126: return 'Elbaph'
    if ch >= 1058: return 'Egghead'
    if ch >= 909: return 'Wano Country'
    if ch >= 903: return 'Levely'
    if ch >= 825: return 'Whole Cake Island'
    if ch >= 802: return 'Zou'
    if ch >= 700: return 'Dressrosa'
    if ch >= 654: return 'Punk Hazard'
    if ch >= 603: return 'Fish-Man Island'
    if ch >= 598: return 'Return to Sabaody'
    if ch >= 581: return 'Post-War'
    if ch >= 550: return 'Marineford'
    if ch >= 525: return 'Impel Down'
    if ch >= 514: return 'Amazon Lily'
    if ch >= 490: return 'Sabaody Archipelago'
    if ch >= 442: return 'Thriller Bark'
    if ch >= 431: return 'Post-Enies Lobby'
    if ch >= 375: return 'Enies Lobby'
    if ch >= 322: return 'Water 7'
    if ch >= 303: return 'Long Ring Long Land'
    if ch >= 237: return 'Skypiea'
    if ch >= 218: return 'Jaya'
    if ch >= 155: return 'Arabasta'
    if ch >= 130: return 'Drum Island'
    if ch >= 115: return 'Little Garden'
    if ch >= 106: return 'Whisky Peak'
    if ch >= 101: return 'Reverse Mountain'
    if ch >= 96: return 'Loguetown'
    if ch >= 69: return 'Arlong Park'
    if ch >= 42: return 'Baratie'
    if ch >= 22: return 'Syrup Village'
    if ch >= 8: return 'Orange Town'
    if ch >= 1: return 'Romance Dawn'
    return 'SBS & Extras'


def get_character_game_mode(c):
    name = (c.get('name') or '').strip().lower()
    if not name:
        return "Hard"

    # 1. Exact curated 100 characters in Easy
    if name in GAME_MODE_EASY_EXACT or ('pink' in name and ('se' in name or name == 'pink')):
        return "Easy"

    # 2. Hard check (curated Hard characters + hard patterns)
    if name in GAME_MODE_HARD_EXACT or any(hp in name for hp in GAME_MODE_HARD_PATTERNS):
        return "Hard"

    # 3. Medium keywords: Other notable characters & commanders
    for mk in GAME_MODE_MEDIUM_KEYWORDS:
        if mk in name:
            if mk == 'kuro' and name not in ['kuro', 'captain kuro']:
                continue
            if mk == 'morgan' and name != 'morgan':
                continue
            if mk == 'krieg' and 'krieg' not in name:
                continue
            return "Medium"

    # 4. Fallback scoring based on data richness
    j_count = min(len(c.get('journey') or []), 15)
    rel_count = len(c.get('relationships') or [])
    has_bounty = bool(c.get('bounty'))
    has_df = bool(c.get('devil_fruit'))
    has_ep = bool(c.get('epithet'))

    if j_count <= 1 and not has_bounty:
        return "Medium" if rel_count >= 8 else "Hard"

    score = (j_count * 2.0) + (rel_count * 1.5)
    if has_bounty: score += 5
    if has_df: score += 4
    if has_ep: score += 3

    return "Medium" if score >= 12 else "Hard"


def matches_game_mode_filter(c, target):
    if not target:
        return True
    return get_character_game_mode(c).lower() == target.lower()


def matches_df_filter(c, target):
    if not target:
        return True
    raw = c.get('devil_fruit')
    items = raw if isinstance(raw, list) else ([raw] if raw else [])
    items = [str(x).strip() for x in items if x and str(x).strip().lower() not in ['none', 'unknown', '']]

    if target == 'None':
        return len(items) == 0

    if target in ['Paramecia', 'Zoan', 'Logia']:
        for it in items:
            clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', it, flags=re.IGNORECASE).strip()
            t = get_devil_fruit_type(clean)
            if t and t.lower() == target.lower():
                return True
        return False

    for it in items:
        clean = re.sub(r'\s*\([^)]*awakened[^)]*\)', '', it, flags=re.IGNORECASE).strip()
        if clean.lower() == target.lower():
            return True
    return False


def format_bounty(bounty):
    if not bounty: return 'Unknown'
    if isinstance(bounty, str): return bounty
    return f"{bounty:,} Berries"


def format_haki(haki):
    if not haki or not len(haki): return 'No Haki or Unknown'
    res = []
    for h in haki:
        hl = h.lower()
        if 'armament' in hl: res.append('Busoshoku')
        elif 'observation' in hl: res.append('Kenbunshoku')
        elif 'conqueror' in hl: res.append('Haoshoku')
        else: res.append(h)
    return ', '.join(res) if res else 'No Haki or Unknown'


def format_devil_fruit(devil_fruit):
    if not devil_fruit:
        return "Unknown"

    fruit_name = devil_fruit.strip()
    fruit_type = get_devil_fruit_type(fruit_name)

    if fruit_type:
        return f"{fruit_type} -- {fruit_name}"

    return fruit_name
