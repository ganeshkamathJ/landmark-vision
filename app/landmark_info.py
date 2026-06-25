"""
Landmark metadata: name, country, city, description, emoji flag.
Aligned with the 'vaslemon/pictures-of-famous-places' Kaggle dataset (50 classes).
Class folder names are the dict keys (lowercase, underscored).
"""

LANDMARK_INFO = {
    "eiffel_tower": {
        "name": "Eiffel Tower",
        "country": "France",
        "city": "Paris",
        "flag": "🇫🇷",
        "description": (
            "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, "
            "designed by engineer Gustave Eiffel for the 1889 World's Fair. Standing 330 metres tall, "
            "it was the world's tallest man-made structure for 41 years and now attracts nearly "
            "7 million visitors annually, making it the most-visited paid monument on Earth."
        ),
        "year_built": "1889",
        "category": "Monument",
        "latitude": 48.8584,
        "longitude": 2.2945,

    },
    "colosseum": {
        "name": "Colosseum",
        "country": "Italy",
        "city": "Rome",
        "flag": "🇮🇹",
        "description": (
            "The Colosseum is an elliptical amphitheatre in the centre of Rome, built of travertine "
            "limestone, tuff, and brick-faced concrete between 70–80 AD. It could hold between 50,000 "
            "and 80,000 spectators who gathered to watch gladiatorial contests, animal hunts, and "
            "public spectacles. It remains the largest ancient amphitheatre ever built."
        ),
        "year_built": "80 AD",
        "category": "Ancient Ruins",
        "latitude": 41.8902,
        "longitude": 12.4922,

    },
    "statue_of_liberty": {
        "name": "Statue of Liberty",
        "country": "United States",
        "city": "New York",
        "flag": "🇺🇸",
        "description": (
            "The Statue of Liberty is a colossal neoclassical sculpture on Liberty Island in New York "
            "Harbor, a gift from France to the United States dedicated on October 28, 1886. Designed by "
            "sculptor Frédéric Auguste Bartholdi and engineered by Gustave Eiffel, she stands 93 metres "
            "tall and has served as a universal symbol of freedom and democracy."
        ),
        "year_built": "1886",
        "category": "Monument",
        "latitude": 40.6892,
        "longitude": -74.0445,

    },
    "big_ben": {
        "name": "Big Ben",
        "country": "United Kingdom",
        "city": "London",
        "flag": "🇬🇧",
        "description": (
            "Big Ben is the nickname for the Great Bell of the clock at the north end of the Palace of "
            "Westminster in London, officially known as the Elizabeth Tower since 2012. Completed in 1859, "
            "the tower stands 96 metres tall and its four clock faces are each 7 metres in diameter, "
            "making it one of the most recognisable landmarks in the world."
        ),
        "year_built": "1859",
        "category": "Tower",
        "latitude": 51.5007,
        "longitude": -0.1246,

    },
    "taj_mahal": {
        "name": "Taj Mahal",
        "country": "India",
        "city": "Agra",
        "flag": "🇮🇳",
        "description": (
            "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the Yamuna river in "
            "Agra, commissioned by Mughal emperor Shah Jahan in 1631 to house the tomb of his favourite "
            "wife Mumtaz Mahal. A UNESCO World Heritage Site and one of the Seven Wonders of the Modern "
            "World, it is widely considered the finest example of Mughal architecture."
        ),
        "year_built": "1653",
        "category": "Mausoleum",
        "latitude": 27.1751,
        "longitude": 78.0421,

    },
    "great_wall_of_china": {
        "name": "Great Wall of China",
        "country": "China",
        "city": "Beijing",
        "flag": "🇨🇳",
        "description": (
            "The Great Wall of China is a series of fortifications built across the historical northern "
            "borders of ancient Chinese states, stretching over 21,000 kilometres. Built primarily during "
            "the Ming dynasty (1368–1644), it is a UNESCO World Heritage Site and one of the greatest "
            "architectural feats in human history."
        ),
        "year_built": "7th Century BC",
        "category": "Fortification",
        "latitude": 40.4319,
        "longitude": 116.5704,

    },
    "machu_picchu": {
        "name": "Machu Picchu",
        "country": "Peru",
        "city": "Cusco Region",
        "flag": "🇵🇪",
        "description": (
            "Machu Picchu is a 15th-century Inca citadel situated on a mountain ridge 2,430 metres above "
            "sea level in the Andes Mountains of Peru. Built around 1450 as an estate for the Inca emperor "
            "Pachacuti, it was abandoned a century later during the Spanish conquest and remained unknown to "
            "the outside world until 1911 when it was brought to international attention by historian Hiram Bingham."
        ),
        "year_built": "c. 1450",
        "category": "Archaeological Site",
        "latitude": -13.1631,
        "longitude": -72.545,

    },
    "sydney_opera_house": {
        "name": "Sydney Opera House",
        "country": "Australia",
        "city": "Sydney",
        "flag": "🇦🇺",
        "description": (
            "The Sydney Opera House is a multi-venue performing arts centre in Sydney, designed by Danish "
            "architect Jørn Utzon and opened in 1973. Its distinctive sail-shaped roof shells have made it "
            "one of the most photographed buildings in the world. A UNESCO World Heritage Site since 2007, "
            "it hosts over 1,500 performances each year."
        ),
        "year_built": "1973",
        "category": "Opera House",
        "latitude": -33.8568,
        "longitude": 151.2153,

    },
    "sagrada_familia": {
        "name": "Sagrada Família",
        "country": "Spain",
        "city": "Barcelona",
        "flag": "🇪🇸",
        "description": (
            "The Basílica de la Sagrada Família is a large unfinished Roman Catholic minor basilica in "
            "Barcelona, designed by the Catalan architect Antoni Gaudí. Construction began in 1882 and "
            "is expected to be completed in 2026. A UNESCO World Heritage Site, it is the most-visited "
            "monument in Spain and a masterpiece of Art Nouveau architecture."
        ),
        "year_built": "1882 (ongoing)",
        "category": "Cathedral",
        "latitude": 41.4036,
        "longitude": 2.1744,

    },
    "acropolis": {
        "name": "Acropolis of Athens",
        "country": "Greece",
        "city": "Athens",
        "flag": "🇬🇷",
        "description": (
            "The Acropolis of Athens is an ancient citadel located on a rocky outcrop above the city of "
            "Athens, containing the remains of several historically significant ancient Greek buildings. "
            "The most famous is the Parthenon, a temple dedicated to the goddess Athena, built between "
            "447 and 432 BC. It is one of the most enduring symbols of Western civilization."
        ),
        "year_built": "5th Century BC",
        "category": "Ancient Ruins",
        "latitude": 37.9715,
        "longitude": 23.7257,

    },
    "christ_the_redeemer": {
        "name": "Christ the Redeemer",
        "country": "Brazil",
        "city": "Rio de Janeiro",
        "flag": "🇧🇷",
        "description": (
            "Christ the Redeemer is an Art Deco statue of Jesus Christ in Rio de Janeiro, created by "
            "French sculptor Paul Landowski and built by engineer Heitor da Silva Costa. Standing 30 metres "
            "tall atop the 710-metre Corcovado mountain, it has become a cultural icon of Brazil and a "
            "symbol of Christianity worldwide."
        ),
        "year_built": "1931",
        "category": "Statue",
        "latitude": -22.9519,
        "longitude": -43.2105,

    },
    "petra": {
        "name": "Petra",
        "country": "Jordan",
        "city": "Ma'an Governorate",
        "flag": "🇯🇴",
        "description": (
            "Petra is a famous archaeological city in southern Jordan, known for its rock-cut architecture "
            "and water conduit system. Established possibly as early as the 4th century BC as the capital "
            "of the Nabataean Kingdom, it is often called the 'Rose City' due to the colour of the stone "
            "from which it is carved. A UNESCO World Heritage Site since 1985."
        ),
        "year_built": "c. 312 BC",
        "category": "Archaeological Site",
        "latitude": 30.3285,
        "longitude": 35.4444,

    },
    "chichen_itza": {
        "name": "Chichen Itza",
        "country": "Mexico",
        "city": "Yucatán",
        "flag": "🇲🇽",
        "description": (
            "Chichen Itza is a large pre-Columbian city built by the Maya people, located in the Tinúm "
            "municipality in Yucatán State. The site's most famous structure is El Castillo, a step pyramid "
            "that served as a temple to the feathered-serpent deity Kukulcan. Designated one of the New "
            "Seven Wonders of the World in 2007."
        ),
        "year_built": "c. 750 AD",
        "category": "Archaeological Site",
        "latitude": 20.6843,
        "longitude": -88.5678,

    },
    "stonehenge": {
        "name": "Stonehenge",
        "country": "United Kingdom",
        "city": "Wiltshire",
        "flag": "🇬🇧",
        "description": (
            "Stonehenge is a prehistoric monument on Salisbury Plain in Wiltshire, England, consisting "
            "of a ring of standing stones, each around 4 metres high and 2 metres wide, weighing around "
            "25 tons. Archaeologists believe it was constructed from 3000 BC to 2000 BC. Its purpose "
            "remains debated, with theories ranging from a burial ground to an astronomical observatory."
        ),
        "year_built": "c. 3000 BC",
        "category": "Prehistoric Monument",
        "latitude": 51.1789,
        "longitude": -1.8262,

    },
    "burj_khalifa": {
        "name": "Burj Khalifa",
        "country": "United Arab Emirates",
        "city": "Dubai",
        "flag": "🇦🇪",
        "description": (
            "The Burj Khalifa is a skyscraper in Dubai, United Arab Emirates, and the tallest structure "
            "in the world, standing at 829.8 metres. Designed by Skidmore, Owings & Merrill and opened "
            "in 2010, it has 163 floors and holds several world records. Its observation deck on the "
            "124th floor offers a panoramic view of the city and the Arabian Gulf."
        ),
        "year_built": "2010",
        "category": "Skyscraper",
        "latitude": 25.1972,
        "longitude": 55.2744,

    },
    "empire_state_building": {
        "name": "Empire State Building",
        "country": "United States",
        "city": "New York",
        "flag": "🇺🇸",
        "description": (
            "The Empire State Building is a 102-storey Art Deco skyscraper in Midtown Manhattan, New York "
            "City. Completed in 1931, it stood as the world's tallest building for nearly 40 years. "
            "The building is a designated New York City landmark and was ranked first on the American "
            "Institute of Architects' list of America's favourite architecture."
        ),
        "year_built": "1931",
        "category": "Skyscraper",
        "latitude": 40.7484,
        "longitude": -73.9857,

    },
    "pyramids_of_giza": {
        "name": "Pyramids of Giza",
        "country": "Egypt",
        "city": "Giza",
        "flag": "🇪🇬",
        "description": (
            "The Pyramids of Giza are the oldest and largest of the three major pyramids in the Giza "
            "pyramid complex, built as tombs for the pharaohs Khufu, Khafre, and Menkaure. The Great "
            "Pyramid of Khufu, completed around 2560 BC, was the tallest man-made structure in the world "
            "for over 3,800 years. They are the only surviving wonder of the ancient world."
        ),
        "year_built": "c. 2560 BC",
        "category": "Ancient Wonder",
        "latitude": 29.9792,
        "longitude": 31.1342,

    },
    "notre_dame": {
        "name": "Notre-Dame Cathedral",
        "country": "France",
        "city": "Paris",
        "flag": "🇫🇷",
        "description": (
            "Notre-Dame de Paris is a medieval Catholic cathedral on the Île de la Cité in the 4th "
            "arrondissement of Paris. Considered one of the finest examples of French Gothic architecture, "
            "construction began in 1163 and was largely complete by 1345. Severely damaged by fire in 2019, "
            "it is currently undergoing restoration and is expected to reopen in 2024."
        ),
        "year_built": "1345",
        "category": "Cathedral",
        "latitude": 48.853,
        "longitude": 2.3499,

    },
    "mount_fuji": {
        "name": "Mount Fuji",
        "country": "Japan",
        "city": "Shizuoka",
        "flag": "🇯🇵",
        "description": (
            "Mount Fuji is the highest mountain in Japan at 3,776 metres, an active stratovolcano located "
            "on Honshu Island. A UNESCO World Heritage Site since 2013, it is one of Japan's 'Three Holy "
            "Mountains' and has been a popular subject in Japanese art and literature. Approximately 200,000 "
            "people climb it every year during the official climbing season."
        ),
        "year_built": "Natural Formation",
        "category": "Natural Landmark",
        "latitude": 35.3606,
        "longitude": 138.7274,

    },
    "angkor_wat": {
        "name": "Angkor Wat",
        "country": "Cambodia",
        "city": "Siem Reap",
        "flag": "🇰🇭",
        "description": (
            "Angkor Wat is a temple complex in Cambodia and is the largest religious monument in the world, "
            "covering some 162.6 hectares. Originally constructed as a Hindu temple of the Khmer Empire in "
            "the early 12th century, it was gradually transformed into a Buddhist temple towards the end of "
            "the 12th century. It is a symbol of Cambodia, appearing on its national flag."
        ),
        "year_built": "c. 1150",
        "category": "Temple",
        "latitude": 13.4125,
        "longitude": 103.867,

    },
    "parthenon": {
        "name": "Parthenon",
        "country": "Greece",
        "city": "Athens",
        "flag": "🇬🇷",
        "description": (
            "The Parthenon is a former temple on the Athenian Acropolis, dedicated to the goddess Athena, "
            "considered the most important surviving building of Classical Greece. Built between 447 and 438 BC, "
            "it is the culmination of the development of the Doric order and has had an enduring influence "
            "on Western architecture."
        ),
        "year_built": "438 BC",
        "category": "Ancient Temple",
        "latitude": 37.9715,
        "longitude": 23.7266,

    },
    "leaning_tower_of_pisa": {
        "name": "Leaning Tower of Pisa",
        "country": "Italy",
        "city": "Pisa",
        "flag": "🇮🇹",
        "description": (
            "The Leaning Tower of Pisa is the campanile, or freestanding bell tower, of the cathedral of "
            "the Italian city of Pisa. Construction began in 1173 and took 199 years, during which the "
            "foundation soil began to subside, causing the iconic lean of about 3.99 degrees. Engineers "
            "stabilised the tower between 1990 and 2001."
        ),
        "year_built": "1372",
        "category": "Tower",
        "latitude": 43.723,
        "longitude": 10.4,

    },
    "niagara_falls": {
        "name": "Niagara Falls",
        "country": "United States / Canada",
        "city": "Niagara Falls",
        "flag": "🇺🇸🇨🇦",
        "description": (
            "Niagara Falls is a group of three waterfalls at the southern end of Niagara Gorge, spanning the "
            "border between the province of Ontario in Canada and the state of New York in the USA. Known for "
            "their beauty and as a valuable source of hydroelectric power, they are among the most powerful "
            "waterfalls in North America, attracting millions of tourists annually."
        ),
        "year_built": "Natural Formation",
        "category": "Natural Landmark",
        "latitude": 43.0828,
        "longitude": -79.0742,

    },
    "golden_gate_bridge": {
        "name": "Golden Gate Bridge",
        "country": "United States",
        "city": "San Francisco",
        "flag": "🇺🇸",
        "description": (
            "The Golden Gate Bridge is a suspension bridge spanning the Golden Gate strait, the opening "
            "of San Francisco Bay into the Pacific Ocean. Completed in 1937, it was the longest and tallest "
            "suspension bridge in the world at the time, with a main span of 1,280 metres. It remains one "
            "of the most photographed bridges in the world."
        ),
        "year_built": "1937",
        "category": "Bridge",
        "latitude": 37.8199,
        "longitude": -122.4783,

    },
    "tower_of_london": {
        "name": "Tower of London",
        "country": "United Kingdom",
        "city": "London",
        "flag": "🇬🇧",
        "description": (
            "The Tower of London, officially His Majesty's Royal Palace and Fortress of the Tower of London, "
            "is a historic castle on the north bank of the River Thames founded in 1066 by William the "
            "Conqueror. It has served as a royal palace, prison, armoury, treasury and menagerie. Today it "
            "houses the Crown Jewels and is visited by over 2.5 million people a year."
        ),
        "year_built": "1078",
        "category": "Castle",
        "latitude": 51.5081,
        "longitude": -0.0759,

    },
    "buckingham_palace": {
        "name": "Buckingham Palace",
        "country": "United Kingdom",
        "city": "London",
        "flag": "🇬🇧",
        "description": (
            "Buckingham Palace is the London residence and administrative headquarters of the monarch of the "
            "United Kingdom. Acquired by King George III in 1761, it has been the principal royal residence "
            "since 1837. The palace has 775 rooms including 19 state rooms, 52 royal and guest bedrooms, "
            "188 staff bedrooms, 92 offices, and 78 bathrooms."
        ),
        "year_built": "1703",
        "category": "Palace",
        "latitude": 51.5014,
        "longitude": -0.1419,

    },
    "louvre": {
        "name": "Louvre Museum",
        "country": "France",
        "city": "Paris",
        "flag": "🇫🇷",
        "description": (
            "The Louvre, officially the Musée du Louvre, is the world's most-visited art museum, located in "
            "Paris, France. A historic monument, it was originally built as a fortress in the late 12th to "
            "13th century under Philip II. The museum houses over 38,000 objects including the Mona Lisa and "
            "the Venus de Milo."
        ),
        "year_built": "1793 (as museum)",
        "category": "Museum",
        "latitude": 48.8606,
        "longitude": 2.3376,

    },
    "alhambra": {
        "name": "Alhambra",
        "country": "Spain",
        "city": "Granada",
        "flag": "🇪🇸",
        "description": (
            "The Alhambra is a palace and fortress complex located in Granada, Andalusia, Spain. Originally "
            "constructed in 889 CE as a small fortress, it was rebuilt in the mid-13th century by the Nasrid "
            "emir Mohammed ben Al-Ahmar. Its intricate Moorish architecture and beautiful gardens make it one "
            "of Spain's most visited tourist attractions and a UNESCO World Heritage Site."
        ),
        "year_built": "1238",
        "category": "Palace",
        "latitude": 37.176,
        "longitude": -3.5875,

    },
    "westminster_abbey": {
        "name": "Westminster Abbey",
        "country": "United Kingdom",
        "city": "London",
        "flag": "🇬🇧",
        "description": (
            "Westminster Abbey is a large, mainly Gothic abbey church in the City of Westminster, London, "
            "just to the west of the Palace of Westminster. It has been the traditional place of coronation "
            "and burial site for British monarchs since 1066. A UNESCO World Heritage Site, it is one of the "
            "most visited religious buildings in the world."
        ),
        "year_built": "1090",
        "category": "Abbey",
        "latitude": 51.4993,
        "longitude": -0.1273,

    },
    "st_peters_basilica": {
        "name": "St. Peter's Basilica",
        "country": "Vatican City",
        "city": "Vatican City",
        "flag": "🇻🇦",
        "description": (
            "St. Peter's Basilica is an Italian Renaissance church in Vatican City, designed principally by "
            "Donato Bramante, Michelangelo, Carlo Maderno and Gian Lorenzo Bernini. The current basilica, "
            "begun in 1506 and completed in 1626, is the largest church in the world and the centrepiece of "
            "the Catholic faith, drawing millions of pilgrims each year."
        ),
        "year_built": "1626",
        "category": "Basilica",
        "latitude": 41.9022,
        "longitude": 12.4539,

    },
    "versailles": {
        "name": "Palace of Versailles",
        "country": "France",
        "city": "Versailles",
        "flag": "🇫🇷",
        "description": (
            "The Palace of Versailles, or simply Versailles, is a royal château in Versailles, in the Île-de-France "
            "region of France. Originally a hunting lodge for Louis XIII, it was transformed into a magnificent "
            "palace by Louis XIV in the 17th century. Its Hall of Mirrors, formal gardens, and royal apartments "
            "reflect the absolute power of the French monarchy."
        ),
        "year_built": "1682",
        "category": "Palace",
        "latitude": 48.8049,
        "longitude": 2.1204,

    },
    "unknown": {
        "name": "Unknown Landmark",
        "country": "Unknown",
        "city": "Unknown",
        "flag": "🌍",
        "description": (
            "The model could not identify this landmark with sufficient confidence. Please try uploading "
            "a clearer image with the landmark as the main subject, ideally taken from a common viewpoint. "
            "Ensure the image is well-lit and not heavily cropped."
        ),
        "year_built": "—",
        "category": "Unknown",
        "latitude": None,
        "longitude": None,

    },
}


def get_landmark(class_name: str) -> dict:
    """Return metadata for a predicted class name, falling back to 'unknown'."""
    key = class_name.lower().replace(" ", "_").replace("-", "_")
    return LANDMARK_INFO.get(key, LANDMARK_INFO["unknown"])
