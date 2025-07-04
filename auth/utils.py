import datetime
import random, string
from jose import jwt
from config import JWT_SECRET, REFRESH_SECRET
from fastapi import HTTPException
from database import redis_client , users_collection

ADJECTIVES = [
    # Colors (60)
    "Crimson", "Azure", "Amber", "Emerald", "Onyx", "Vermilion", "Cerulean", "Obsidian", "Ivory", "Scarlet",
    "Sapphire", "Ruby", "Topaz", "Jade", "Cobalt", "Indigo", "Magenta", "Turquoise", "Violet", "Maroon",
    "Charcoal", "Pearl", "Copper", "Bronze", "Silver", "Gold", "Platinum", "Garnet", "Lavender", "Coral",
    "Mint", "Olive", "Mustard", "Salmon", "Teal", "Fuchsia", "Lilac", "Sepia", "Slate", "Crimson",
    "Ultramarine", "Pumpkin", "Honeydew", "Eggplant", "Denim", "Rust", "Mauve", "Peach", "Rose", "Wine",
    "Ink", "Ivory", "Jet", "Khaki", "Lemon", "Moss", "Navy", "Orchid", "Pine", "Quartz",

    # Emotions/Personality (80)
    "Silent", "Happy", "Melancholic", "Furious", "Serene", "Anxious", "Ecstatic", "Grumpy", "Blissful", "Lonely",
    "Playful", "Joyful", "Wistful", "Frenzied", "Moody", "Jubilant", "Sullen", "Zealous", "Apathetic", "Bewildered",
    "Content", "Dismal", "Enraged", "Frightened", "Gloomy", "Hopeful", "Irritated", "Jaded", "Keen", "Lethargic",
    "Mischievous", "Nervous", "Optimistic", "Pensive", "Quizzical", "Resentful", "Sarcastic", "Timid", "Unsettled", "Vivacious",
    "Whimsical", "Exuberant", "Yearning", "Zestful", "Anguished", "Bitter", "Cynical", "Dreadful", "Euphoric", "Fervent",
    "Grave", "Hysterical", "Indifferent", "Jovial", "Knavish", "Lugubrious", "Morose", "Nonchalant", "Outraged", "Petulant",
    "Quirky", "Radiant", "Somber", "Tranquil", "Upset", "Vexed", "Wrathful", "Yawning", "Zany", "Adoring",
    "Brooding", "Curious", "Defiant", "Earnest", "Flustered", "Guarded", "Haughty", "Insecure", "Jealous", "Loving",

    # Nature (100)
    "Electric", "Thundering", "Solar", "Lunar", "Breezy", "Stormy", "Frozen", "Fiery", "Misty", "Dewy",
    "Sunny", "Rainy", "Windy", "Foggy", "Snowy", "Icy", "Humid", "Arid", "Tropical", "Temperate",
    "Volcanic", "Geothermal", "Tidal", "Seismic", "Barren", "Fertile", "Lush", "Overgrown", "Desolate", "Verdant",
    "Flourishing", "Withered", "Blossoming", "Decaying", "Pristine", "Polluted", "Crystalline", "Murky", "Glistening", "Parched",
    "Rugged", "Sandy", "Rocky", "Muddy", "Swampy", "Mossy", "Grassy", "Leafy", "Petal-strewn", "Pine-scented",
    "Salt-crusted", "Sun-drenched", "Moonlit", "Starlit", "Twilight", "Dawn-kissed", "Dusk-covered", "Noon-baked", "Frost-laden", "Heat-hazed",
    "Cloud-covered", "Sky-piercing", "Root-entangled", "Waterlogged", "Drought-stricken", "Flood-soaked", "Erosion-carved", "Sediment-layered", "Mineral-rich", "Oxygen-deprived",
    "Photosynthetic", "Symbiotic", "Predatory", "Nocturnal", "Diurnal", "Migratory", "Hibernating", "Burrowing", "Nesting", "Blooming",
    "Photosynthetic", "Carnivorous", "Herbivorous", "Omnivorous", "Parasitic", "Venomous", "Poisonous", "Camouflaged", "Transparent", "Luminescent",
    "Bio-luminescent", "Fluorescent", "Iridescent", "Hibernal", "Estival", "Vernal", "Autumnal", "Seasonless", "Tidal-locked", "Orbit-stable",

    # Size/Scale (60)
    "Colossal", "Minuscule", "Gigantic", "Petite", "Titanic", "Microscopic", "Vast", "Infinite", "Pocket-sized", "Cosmic",
    "Subatomic", "Planetary", "Galactic", "Universal", "Multiversal", "Infinitesimal", "Monumental", "Towering", "Lilliputian", "Gargantuan",
    "Expansive", "Compact", "Sparse", "Dense", "Bulky", "Svelte", "Voluminous", "Diminutive", "Boundless", "Limited",
    "Capacious", "Cramped", "Spacious", "Narrow", "Wide", "Deep", "Shallow", "Elongated", "Squat", "Rotund",
    "Slender", "Corpulent", "Skeletal", "Hulking", "Portly", "Lanky", "Stocky", "Paunchy", "Willowy", "Brawny",
    "Athletic", "Stout", "Tubby", "Dwarfish", "Towering", "Lanky", "Trim", "Pudgy", "Svelte", "Rotund",

    # Time-Related (60)
    "Ancient", "Futuristic", "Prehistoric", "Neon", "Medieval", "Victorian", "Retro", "Cyber", "Stone-age", "Space-age",
    "Jurassic", "Paleolithic", "Neolithic", "Classical", "Renaissance", "Enlightenment", "Industrial", "Atomic", "Digital", "Nanotech",
    "Primeval", "Archaic", "Antediluvian", "Bygone", "Olden", "Yesteryear", "Contemporary", "Modern", "Postmodern", "Futurist",
    "Dated", "Obsolete", "Brand-new", "Nascent", "Perennial", "Eternal", "Ephemeral", "Momentary", "Endless", "Timeless",
    "Anachronistic", "Synchronous", "Diachronous", "Chronological", "Sequential", "Concurrent", "Simultaneous", "Expired", "Fresh", "Aged",
    "Seasoned", "Ripened", "Decade-old", "Century-old", "Millenia-old", "Eon-spanning", "Dawn-of-time", "End-of-days", "Pre-apocalyptic", "Post-apocalyptic",

    # Texture/Quality (80)
    "Mysterious", "Velvety", "Prickly", "Smooth", "Rough", "Glossy", "Matte", "Gritty", "Slimy", "Fuzzy",
    "Slick", "Sticky", "Gooey", "Crispy", "Crunchy", "Soggy", "Squishy", "Brittle", "Malleable", "Pliable",
    "Rigid", "Flexible", "Porous", "Impermeable", "Transparent", "Opaque", "Translucent", "Reflective", "Absorbent", "Waterproof",
    "Flammable", "Nonflammable", "Conductive", "Insulating", "Magnetic", "Radioactive", "Toxic", "Harmless", "Fragrant", "Pungent",
    "Aromatic", "Odorless", "Flavorful", "Bland", "Sweet", "Sour", "Bitter", "Salty", "Savory", "Spicy",
    "Mild", "Piquant", "Zesty", "Tangy", "Rancid", "Fresh", "Stale", "Rotten", "Preserved", "Cured",
    "Fermented", "Distilled", "Carbonated", "Flat", "Fizzy", "Sparkling", "Still", "Turbulent", "Calm", "Agitated",
    "Viscous", "Runny", "Thick", "Thin", "Diluted", "Concentrated", "Pure", "Contaminated", "Sterile", "Fertile",

    # Sound-Related (40)
    "Echoing", "Muffled", "Resonant", "Shrill", "Melodic", "Discordant", "Harmonic", "Cacophonous", "Silent", "Deafening",
    "Thunderous", "Whispering", "Hissing", "Roaring", "Howling", "Chirping", "Screeching", "Murmuring", "Growling", "Purring",
    "Clanging", "Tinkling", "Jingling", "Rattling", "Humming", "Buzzing", "Droning", "Sizzling", "Crackling", "Popping",
    "Squeaking", "Squealing", "Groaning", "Moaning", "Wailing", "Singing", "Rapping", "Beatboxing", "Yodeling", "Crooning",

    # Light-Related (40)
    "Luminous", "Radiant", "Glowing", "Shimmering", "Glistening", "Twinkling", "Flickering", "Pulsing", "Strobing", "Fluorescent",
    "Incandescent", "Iridescent", "Phosphorescent", "Bioluminescent", "Moonlit", "Sunlit", "Starlit", "Shadowy", "Dusky", "Murky",
    "Opaque", "Transparent", "Translucent", "Hazy", "Misty", "Foggy", "Smoky", "Crystal-clear", "Glassy", "Diamond-bright",
    "Laser-focused", "Diffused", "Concentrated", "Scattered", "Refracted", "Diffracted", "Polarized", "Ultraviolet", "Infrared", "X-ray"
]
NOUNS = [
    # Animals (100)
    "Panda", "Falcon", "Cobra", "Mantis", "Narwhal", "Chameleon", "Armadillo", "Platypus", "Dragonfly", "Phoenix",
    "Griffin", "Kraken", "Yeti", "Centaur", "Sphinx", "Basilisk", "Chimera", "Pegasus", "Hydra", "Golem",
    "Banshee", "Doppelganger", "Leviathan", "Mermaid", "Minotaur", "Satyr", "Djinn", "Troll", "Ogre", "Imp",
    "Gremlin", "Wraith", "Specter", "Poltergeist", "Wendigo", "Skinwalker", "Selkie", "Kelpie", "Harpy", "Cerberus",
    "Cockatrice", "Manticore", "Behemoth", "Ziz", "Roc", "Simurgh", "Quetzalcoatl", "Jormungandr", "Fenrir", "Tiamat",
    "Dullahan", "Bunyip", "Dropbear", "Jackalope", "Wolpertinger", "Hodag", "Snallygaster", "Sidehill", "Squonk", "Hidebehind",
    "Vampire", "Werewolf", "Zombie", "Ghoul", "Revenant", "Lich", "Necromancer", "Wight", "Draugr", "Barghest",
    "Blackdog", "Hellhound", "Cheshire", "Jabberwock", "Bandersnatch", "Jubjub", "Toves", "Borogove", "Mome", "Rath",
    "Snark", "Boojum", "Gimble", "Frumious", "Manxome", "Tulgey", "Vorpal", "Frabjous", "Callooh", "Callay",
    "Chortle", "Galumph", "Jubjub", "Mimsy", "Outgrabe", "Slithy", "Tove", "Uffish", "Whiffling", "Burble",

    # Professions (80)
    "Wizard", "Architect", "Astronaut", "Blacksmith", "Cartographer", "Diver", "Engineer", "Forger", "Geologist", "Herbalist",
    "Illusionist", "Jeweler", "Knight", "Librarian", "Machinist", "Navigator", "Ophthalmologist", "Puppeteer", "Quartermaster", "Ranger",
    "Sculptor", "Tinker", "Undertaker", "Vintner", "Watchmaker", "Xenobiologist", "Yachtsman", "Zoologist", "Alchemist", "Botanist",
    "Cryptographer", "Druid", "Exorcist", "Falconer", "Geomancer", "Horologist", "Inquisitor", "Jester", "Keeper", "Lamplighter",
    "Mercenary", "Numismatist", "Obelisk", "Pirate", "Quilter", "Rogue", "Spy", "Trapper", "Upholsterer", "Voyager",
    "Warden", "Xylographer", "Yodeler", "Zealot", "Archer", "Bard", "Cleric", "Dervish", "Enchanter", "Fletcher",
    "Gunslinger", "Hacker", "Illuminator", "Jongleur", "Kabbalist", "Luthier", "Mime", "Necromancer", "Oracle", "Pugilist",
    "Quillmaster", "Runecaster", "Soothsayer", "Troubadour", "Usurper", "Valkyrie", "Wayfarer", "Xenodochial", "Yogi", "Zookeeper",

    # Technology (80)
    "Nanobot", "Hologram", "Drone", "Cyborg", "Android", "Mainframe", "Server", "Processor", "Motherboard", "Transformer",
    "Replicant", "Synth", "AI", "Algorithm", "Firewall", "Router", "Switch", "Node", "Cluster", "Array",
    "Compiler", "Interpreter", "Kernel", "Daemon", "Firmware", "Middleware", "Hypervisor", "Blockchain", "Ledger", "Token",
    "Smartcontract", "DApp", "Oracle", "Miner", "Validator", "Sequencer", "Prover", "Verifier", "ZK-Rollup", "Optimistic",
    "Shard", "Beacon", "Epoch", "Slot", "Committee", "Attestation", "Finality", "Checkpoint", "Snapshot", "Fork",
    "Merge", "Surge", "Verge", "Purge", "Splurge", "Quantum", "Qubit", "Superposition", "Entanglement", "Teleportation",
    "Interference", "Coherence", "Decoherence", "Tunneling", "Annealing", "Transistor", "Diode", "Capacitor", "Resistor", "Inductor",
    "Oscillator", "Amplifier", "Modulator", "Demodulator", "Multiplexer", "Demultiplexer", "Encoder", "Decoder", "Arbiter", "Scheduler",

    # Nature Elements (80)
    "Unicorn", "Tornado", "Aurora", "Tsunami", "Geyser", "Quasar", "Supernova", "Meteor", "Comet", "Nebula",
    "Blackhole", "Singularity", "Wormhole", "Whitehole", "Einstein-Rosen", "Kugelblitz", "Boltzmann", "Fermion", "Boson", "Hadron",
    "Lepton", "Quark", "Gluon", "Photon", "Neutrino", "Muon", "Tau", "Pion", "Kaon", "Baryon",
    "Meson", "Tachyon", "Axion", "WIMP", "SIMPs", "Sterile", "Dirac", "Majorana", "Weyl", "Fermi",
    "Bose", "Higgs", "Inflaton", "Curvaton", "Quintessence", "Phantom", "K-essence", "Tachyon", "Chaplygin", "Dilaton",
    "Radion", "Moduli", "Graviton", "Plasmon", "Polaron", "Magnon", "Phonon", "Roton", "Soliton", "Vorton",
    "Skyrmion", "Instanton", "Monopole", "Vortex", "Cosmic-string", "Domain-wall", "Texture", "Defect", "Anomaly", "Exciton",
    "Polariton", "Anyon", "Pleon", "Fracton", "Unparticle", "Preon", "Technicolor", "X-particle", "Y-particle", "Z-particle",

    # Mythological Weapons (60)
    "Excalibur", "Mjolnir", "Gungnir", "Durendal", "Caladbolg", "Fragarach", "Claíomh", "Tizona", "Joyeuse", "Courtain",
    "Kusanagi", "Ame-no", "Totsuka-no", "Tonbogiri", "Nandaka", "Pinaka", "Trishula", "Vajra", "Sudarshana", "Sharanga",
    "Gandiva", "Parashu", "Bhargavastra", "Brahmastra", "Pashupatastra", "Narayanastra", "Vaishnavastra", "Agneyastra", "Varunastra", "Vayavyastra",
    "Suryastra", "Somashtra", "Maheshwar", "Kaumodaki", "Modaki", "Khatvanga", "Khadga", "Nandaka", "Pinaka", "Sharanga",
    "Gandiva", "Parashu", "Bhargavastra", "Brahmastra", "Pashupatastra", "Narayanastra", "Vaishnavastra", "Agneyastra", "Varunastra", "Vayavyastra",
    "Suryastra", "Somashtra", "Maheshwar", "Kaumodaki", "Modaki", "Khatvanga", "Khadga", "Nandaka", "Pinaka", "Sharanga",

    # Scientific Instruments (60)
    "Telescope", "Microscope", "Spectrometer", "Oscilloscope", "Chromatograph", "Centrifuge", "Cyclotron", "Synchrotron", "Collider", "Detector",
    "Calorimeter", "Tracker", "Muon-chamber", "Time-projection", "Wire-chamber", "Bubble-chamber", "Cloud-chamber", "Spark-chamber", "Streamer", "Drift",
    "Cherenkov", "Scintillator", "Photomultiplier", "Avalanche", "Semiconductor", "Superconducting", "Transition-edge", "Microcalorimeter", "Bolometer", "Interferometer",
    "Gravitational-wave", "Laser-interferometer", "Atom-interferometer", "Fabry-Perot", "Michelson", "Mach-Zehnder", "Sagnac", "Fizeau", "Twyman-Green", "Shearing",
    "Common-path", "White-light", "Phase-shifting", "Holographic", "Speckle", "Moiré", "Talbot", "Hartmann", "Shack-Hartmann", "Curvature",
    "Pyramid", "Quadri-wave", "Shearography", "ESPI", "DIC", "Photoelasticity", "Thermography", "Schlieren", "Shadowgraph", "Birefringence"
]
def generate_otp(length=5):
    """
    Generates a random numeric OTP of a given length.

    Args:
        length: The length of the OTP to generate, defaults to 5.

    Returns:
        A string of length `length` consisting of random digits.
    """
    return ''.join(random.choices(string.digits, k=length))

def create_jwt(email: str):
    """
    Creates a JWT token for the given email address.

    Args:
        email: The email address for which to create the token.

    Returns:
        A string containing the JWT token.

    Notes:
        The token will expire in 7 days.
    """
    return jwt.encode({
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

def refresh_jwt(email: str):
    """
    Creates a refresh JWT token for the given email address.

    Args:
        email: The email address for which to create the refresh token.

    Returns:
        A string containing the refresh JWT token.

    Notes:
        The refresh token will expire in 30 days.
    """

    return jwt.encode({
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, REFRESH_SECRET, algorithm="HS256")

async def check_rate_limit(key: str, limit: int = 5, window: int = 300):
    """
    Checks a rate limit for the given key.

    Args:
        key: The Redis key to use for the rate limit.
        limit: The number of requests allowed within the given window.
        window: The time in seconds for the rate limit.

    Raises:
        HTTPException: If the rate limit has been exceeded.
    """
    count = await redis_client.get(key)
    if count is not None and int(count) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    txn = redis_client.pipeline()
    txn.incr(key)
    txn.expire(key, window)
    await txn.execute()

async def generate_random_username():
    for _ in range(100):  # Try 10 times max
        username = f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randint(100, 999)}"
        if not await users_collection.find_one({"username": username}):
            return username
    raise Exception("Could not generate unique username")