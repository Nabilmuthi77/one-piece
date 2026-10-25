import flet as ft

# API Endpoints
API_URL = 'https://oparchive.com/data/characters.json'
DEVIL_FRUITS_API_URL = 'https://oparchive.com/data/devil_fruits.json'
BASE_IMG_URL = 'https://oparchive.com'

# Theme Colors (matching my-life palette)
DARK_BG = "#071A20"
DARK_CARD = "#0A2028"
DARK_TEXT_MAIN = "#FFFFFF"
DARK_TEXT_MUTED = "#CBD5E1"

LIGHT_BG = "#F5F7FA"
LIGHT_CARD = "#FFFFFF"
LIGHT_TEXT_MAIN = "#0D9488"
LIGHT_TEXT_MUTED = "#0D9488"

ACCENT = "#0D9488"
WHATSAPP = "#25D366"

# Status Bar Clearance Constant (Matching my-life for mobile punch-hole/notch safety)
STATUS_BAR_SPACER_HEIGHT = 52

# Floating Button & Menu Positioning Constants
BUTTON_SIZE = 42
VIEWPORT_MARGIN = 16
MENU_GAP = 12

# Story Arcs in chronological order
ARC_ORDER = [
    "Romance Dawn", "Orange Town", "Syrup Village", "Baratie", "Arlong Park",
    "Loguetown", "Reverse Mountain", "Whisky Peak", "Little Garden", "Drum Island",
    "Arabasta", "Jaya", "Skypiea", "Long Ring Long Land", "Water 7",
    "Enies Lobby", "Post-Enies Lobby", "Thriller Bark", "Sabaody Archipelago",
    "Amazon Lily", "Impel Down", "Marineford", "Post-War", "Return to Sabaody",
    "Fish-Man Island", "Punk Hazard", "Dressrosa", "Zou", "Whole Cake Island",
    "Levely", "Wano Country", "Egghead", "Elbaph", "SBS & Extras"
]

# Game Mode Curation Lists
GAME_MODE_HARD_PATTERNS = {
    'pandaman', 'tomato gang', 'minatomo', 'sam', 'batchee', 'unigaro',
    'hattori', 'stronger', 'monster', 'eyelashes', 'hasami', 'camel',
    'aegir', 'alvar', 'axel', 'bent', 'millet pine', 'moon isaac',
    'seagull guns', 'sunbell', 'doringo', 'bonk punch', 'limejuice',
    'bell-m'
}

# Curated characters assigned to Hard
GAME_MODE_HARD_EXACT = {
    'nezumi', 'mozu', 'kurozumi higurashi', 'genzo', 'chaka', 'yokozuna',
    'banchina', 'attach', 'blade', 'bourbon jr.', 'buchi',
    'chadros higelyges [brownbeard]', 'dago', 'dalton', 'ganzui', 'ganryu',
    'gambia', 'hiramera', 'ida', 'ishilly', 'ivan x', 'keith',
    'kashigami', "kashigami's child", 'kelly funk', 'kiku',
    'kentauros', 'kinoko', 'kiev', 'kiwi', 'macro', 'marlon', 'matsuge',
    'ninjin', 'masked deuce', 'moda', 'masira', 'milky', 'nojiko', 'ohm',
    'ochoku', 'onigumo', 'part', 'petermoo', 'potato', 'portgas d. rouge',
    'seamars', 'seira', 'scotch [yeti cool brother]', 'sham', 'shin detamaruka',
    'shoujou', 'spandine', 'stomp', 'tom', 'tamanegi', 'tansui', 'taro',
    'terracotta', 'tokijiro', 'tokikake [chaton]', 'umit', 'wyper', 'wire',
    'yomo', 'yamakaji', 'totts', 'urban', 'very good', 'wolf', 'wanda',
    'strawberry', 'suleiman', 'tamagon', 'tama', 'kurozumi tama', 'sora',
    'squard', 'shishilian', 'shura', 'skaldi', 'stainless', 'ronja',
    'ryunosuke', 'mero', 'kumadori', 'kumadori yamanbako', 'marguerite',
    'lulis', 'kalgara', 'leonero', 'john', 'roddy', 'gustav', 'gyaro',
    'hikoichi', 'higuma', 'gyogyo', 'fillonce', 'footbianco', 'fullbody',
    'gedatsu', 'gin', 'giovanni', 'goro', 'chouchou', 'dagny', 'concelot',
    'comil', 'cowboy', 'draw', 'emil', 'erik', 'capone pez',
    'charlotte newgo', 'charlotte fuyumeg', 'charlotte akimeg', 'charlotte allmeg',
    'charlotte nutmeg', 'charlotte harumeg', 'charlotte newji', 'charlotte newsan',
    'charlotte newshi', 'charlotte newichi', 'charlotte mobile', 'chew',
    'blackback [bb]', 'battaman', 'bluejam', 'bomba', 'boodle', 'adele',
    'bobbin', 'atmos', 'bian', 'hiriluk', 'hototogisu', 'igaram', 'hongo',
    'kabu', 'kairen', 'kong', 'kyo [silver axe]', 'kujaku',
    'pound', 'porchemy', 'sarquiss', 'tamachibi', 't bone',
    'demalo black', 'yarisugi', 'zambai',
    'carmel', 'rock [yeti cool brother]', 'paulie', 'tilestone',
    'doberman', 'ylva', 'vander decken', 'vander decken ix', 'yorki', 'olav',
    'johanna', 'johana', 'ottoland', 'karin', 'maha',
    'tosa', 'pell', 'mashikaku', 'kuroobi', 'guillotine', 'bjorn', 'piiman', 'pomsky', 'jabra'
}

# Curated exact 100 characters for Easy Mode
GAME_MODE_EASY_EXACT = {
    # 1-10 Topi Jerami
    'monkey d. luffy', 'roronoa zoro', 'nami', 'usopp', 'sanji',
    'tony tony chopper', 'nico robin', 'cutty flam [franky]', 'brook', 'jinbe',
    # 11-20
    'gol d. roger', 'edward newgate [whitebeard]', 'shanks', 'kaidou',
    'charlotte linlin [big mom]', 'marshall d. teach [blackbeard]', 'buggy',
    'portgas d. ace', 'sabo', 'monkey d. dragon',
    # 21-30
    'monkey d. garp', 'silvers rayleigh', 'kouzuki oden', 'sengoku',
    'sakazuki [akainu]', 'kuzan [aokiji]', 'borsalino [kizaru]',
    'issho [fujitora]', 'aramaki [ryokugyu]', 'dracule mihawk',
    # 31-40
    'crocodile', 'boa hancock', 'bartholomew kuma', 'gecko moria [kouzuki moria]',
    'donquixote doflamingo', 'trafalgar d. water law', 'eustass kid', 'killer',
    'loki', 'jewelry bonney',
    # 41-50
    'basil hawkins', 'scratchmen apoo', 'x drake', 'smoker', 'koby',
    'arber [king]', 'scien [queen]', 'jack', 'charlotte katakuri', 'charlotte cracker',
    # 51-60
    'charlotte smoothie', 'charlotte perospero', 'polo marco', 'vegapunk',
    'yasopp', 'jaygarcia saturn', 'jesus burgess', 'van augur', 'enel', 'rob lucci',
    # 61-70
    'kaku', 'caesar clown', 'magellan', 'alvida',
    'bentham (bon clay) [mr. 2]', 'bepo', 'nefertari vivi', 'rebecca',
    'bartolomeo', 'perona',
    # 71-80
    'shirahoshi', 'yamato', 'charlotte pudding', 'vinsmoke reiju', 'makino',
    'koala', 'kureha', 'nerona imu', 'arlong', 'carrot',
    # 81-90
    'kinemon', 'kouzuki momonosuke', 'tashigi', 'bellamy', 'cavendish',
    'emporio ivankov', 'helmeppo', 'baby 5', 'joy boy', 'sugar',
    # 91-100
    'diamante', 'pica', 'figarland garling', 'dellinger', 'sai',
    'hajrudin', 'davy d. xebec [rocks]', 'scopper gaban', 'caribou'
}

GAME_MODE_MEDIUM_KEYWORDS = [
    # Early & Flashback characters
    'kuina', 'kaya', 'zeff', 'saul',
    'fisher tiger', 'otohime', 'noland', 'yasuie', 'toki', 'hyogoro', 'hyougoro',
    'clover',
    # Egghead & Vegapunk Satellites
    'edison', 'shaka', 'lilith', 'pythagoras', 'atlas', 'york',
    # Yonko Commanders & Key Pirates
    'jozu', 'vista', 'shiryu', 'doc q', 'laffitte', 'beckman', 'lucky roux',
    # Grand Fleet & Key Arc Allies
    'leo', 'ideo', 'kyros', 'pedro', 'shinobu',
    # Akazaya 9 & Wano
    'denjiro', 'raizo', 'kikunojo', 'kanjuro', 'kawamatsu', 'nekomamushi', 'inuarashi', 'ashura doji', 'izo',
    # CP9 / CP0 & World Govt
    'blueno', 'kalifa', 'fukurou', 'spandam', 'stussy',
    'mars', 'warcury', 'nusjuro', 'ju peter',
    # Shichibukai Subordinates & Family
    'galdino', 'mr. 3', 'daz bonez', 'mr. 1', 'absalom',
    'trebol', 'vergo', 'monet', 'ichiji', 'niji', 'yonji', 'judge',
    # Marines
    'hina', 'sentomaru', 'momonga',
    # Arc Villains & Specific requested Medium characters
    'kuro', 'morgan', 'krieg', 'wapol', 'hody jones',
    'flampe', 'brûlée', 'brulee', 'building snake', 'batman', 'kashii', 'nico olvia'
]
