from django.core.management.base import BaseCommand
from doc_search.models import Document
from django import db
from django.conf import settings

import os
import re
import shutil
import logging

logger = logging.getLogger(settings.LOGGER_NAME)

STOP_WORDS = set(["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"])
STOP_WORDS.update(["page", "pages", "yes"])

def get_number(text):
    return re.sub('[^0-9]+', '', text)

def process_text(text):
    return re.sub('\s+', ' ', re.sub('[^0-9a-zA-Z\s]+', '', text)).lower()

ORGS = ['Carlyle Group', 'Kohlberg Kravis Roberts', 'TPG', 'Apollo Global Management', 'Goldman Sachs Merchant Banking Division', 'Oaktree Capital Management', 'Blackstone Group', 'Bain Capital', 'Warburg Pincus', 'Advent International', 'Goldman Sachs AIMS Private Equity', 'Riverstone Holdings', 'HarbourVest Partners', 'Providence Equity Partners', 'Fortress Investment Group', 'Silver Lake', 'Hellman & Friedman', 'First Reserve Corporation', 'Adams Street Partners', 'Clayton Dubilier & Rice', 'JC Flowers & Co', 'TA Associates', 'Sankaty Advisors', 'Leonard Green & Partners', 'Ares Management', 'Centerbridge Capital Partners', 'Neuberger Berman', 'Madison Dearborn Partners', 'Cerberus Capital Management', 'Summit Partners', 'GTCR Golder Rauner', 'JPMorgan Asset Management - Private Equity Group', 'Welsh, Carson, Anderson & Stowe', 'Sun Capital Partners', 'Thomas H Lee Partners', 'Denham Capital Management', 'Golden Gate Capital', 'Lindsay Goldberg', 'Berkshire Partners', 'Kelso & Company', 'Platinum Equity', 'American Securities', 'Stone Point Capital', 'Insight Venture Partners', 'New Mountain Capital', 'Oak Hill Capital Partners', 'Vista Equity Partners', 'AEA Investors', 'Hamilton Lane', 'Court Square Capital Partners', 'Capital International', 'Bayside Capital', 'Yorktown Partners', 'H.I.G. Capital', 'Technology Crossover Ventures', 'ABRY Partners', 'Avista Capital Partners', 'CCMP Capital Advisors', 'Riverside Company', 'The Jordan Company', 'Angelo, Gordon & Co', 'Vestar Capital Partners', 'Catterton Partners', 'Francisco Partners', 'Odyssey Investment Partners', 'Quantum Energy Partners', 'StepStone Group', 'Kohlberg & Company', 'Crestview Partners', 'Olympus Partners', 'Metalmark Capital', 'Gores Group', 'KSL Capital Partners', 'GI Partners', 'Thoma Bravo', 'Levine Leichtman Capital Partners', 'Battery Ventures', 'GoldPoint Partners', 'Audax Private Equity', 'Roark Capital Group', 'Tinicum Incorporated', 'Investcorp', 'Irving Place Capital', 'Aurora Capital Group', 'KRG Capital', 'Mesirow Financial Private Equity', 'Sterling Partners', 'Castle Harlan', 'Charlesbank Capital Partners', 'JLL Partners', 'Sentinel Capital Partners', 'Rhone Capital', 'FFL', 'Flexpoint Ford', 'Performance Equity Management', 'Wellspring Capital Management', 'Littlejohn & Co.', 'TSG Consumer Partners', 'LLR Partners', 'Yucaipa Companies', 'Genstar Capital Partners', 'Aquiline Capital Partners', 'Essex Woodlands Health Ventures', 'GCM Customized Fund Investment Group', 'Veritas Capital', 'Harvest Partners', 'Corsair Capital', 'Moelis Capital Partners', 'Elevation Partners', 'Great Hill Partners', 'MidOcean Partners', 'Accel-KKR', 'Diamond Castle Holdings', 'Norwest Venture Partners', 'Lightyear Capital', 'Quadrangle Group', 'H&Q Asia Pacific', 'JMI Equity', 'Pamlico Capital', 'Vector Capital', 'Neuberger Berman', 'Freeman Spogli & Co', 'Veronis Suhler Stevenson', 'Domain Associates', 'W Capital Partners', 'Spectrum Equity', 'Pegasus Capital Advisors', 'Orchard First Source', 'Wind Point Partners', 'General Atlantic', 'American Capital', 'Symphony Technology Group', 'J.H. Whitney & Co', 'RoundTable Healthcare Partners', 'Frazier Healthcare Ventures', 'Snow Phipps Group', 'Perella Weinberg Partners', 'Centre Partners Management', 'Bedford Funding', 'New Silk Route Growth Capital', 'Endeavour Capital', 'Arsenal Capital Partners', 'Clearlake Capital Group', 'Polaris Partners', 'Sageview Capital', 'Windjammer Capital', 'Monitor Clipper Partners', 'ACON Investments', 'The Sterling Group', 'Lincolnshire Management', 'Emerging Capital Partners', 'Altamont Capital Partners', 'Behrman Capital', 'ABS Capital Partners', 'Darby Overseas Investments', 'Caltius Capital Management', "Beecken Petty O'Keefe & Company", 'Morgan Stanley Global Private Equity', 'NCH Capital', 'Paine & Partners', 'Blum Capital Partners', 'Ridgemont Equity Partners', 'Riverside Partners', 'PPM America Capital Partners', 'Edgewater Funds', 'Harbour Group', 'GCP Capital Partners', 'Graham Partners', 'Versa Capital Management', 'American Industrial Partners', 'Palladium Equity Partners', 'Banc Funds Company', 'Brazos Private Equity Partners', 'Corporate Partners', 'HGGC', 'Lee Equity Partners', 'Intervale Capital', 'Perseus', 'SV Life Sciences', 'Huron Capital Partners', 'Cortec Group', 'Morgenthaler', 'Quad-C Management', 'Greenbriar Equity Group', 'Industrial Growth Partners', 'Quintana Capital Group', 'Sycamore Partners', 'Weston Presidio Capital', 'Arlington Capital Partners', 'Leeds Equity Partners', 'Brynwood Partners', 'Wynnchurch Capital Partners', 'WestView Capital Partners', 'Wicks Group', 'Eos Partners', 'Mason Wells', 'ComVest Partners', 'JF Lehman & Company', 'Energy Trust Capital', 'Gryphon Investors', 'Fisher Lynch Capital', 'Searchlight Capital Partners', 'Linsalata Capital Partners', 'Element Partners', 'NewSpring Capital', 'Jefferies Capital Partners', 'Trivest Partners', 'Pfingsten Partners', 'Sciens Capital Management', 'Insight Equity', 'Post Oak Energy Capital', 'LNK Partners', 'Lake Capital Partners', 'Nautic Partners', 'Castanea Partners', 'HealthPoint Capital', 'Kinderhook Industries', 'Riverwood Capital', 'GE Asset Management - Private Equity', 'Trident Capital', 'Tailwind Capital', 'Chicago Growth Partners', 'Bertram Capital', 'Red Zone Capital Partners', 'Excellere Partners', 'Altaris', 'Gridiron Capital', 'Waud Capital Partners', 'Pharos Capital Group', 'Platte River Equity', 'Shamrock Capital Advisors', 'Health Evolution Partners', 'MSouth Equity Partners', 'Parallel Resource Partners', 'Fenway Partners', 'Brockway Moran & Partners', 'Evergreen Pacific Partners', 'Monomoy Capital Partners', 'Peak Rock Capital', 'VMG Partners', 'The Halifax Group', 'Five Points Capital', 'Arias Resource Capital Management', 'Cadent Energy Partners', 'Thompson Street Capital Partners', 'Lovell Minnick Partners', 'InterMedia Advisors', 'KarpReilly', 'Mill Road Capital', 'Cyprium Partners', 'Milestone Partners', 'Calera Capital', 'DCA Capital Partners', 'Housatonic Partners', 'Sorenson Capital', 'Grey Mountain Partners', 'Riordan, Lewis & Haden', 'Siris Capital', 'Seidler Equity Partners', 'Carousel Capital', 'CI Capital Partners', 'Primus', 'Arlon Capital Partners', 'GenNx360 Capital Partners', 'Serent Capital', 'Alpine Investors', 'Baird Capital Partners', 'SK Capital Partners', 'Enhanced Equity Funds', 'Lombard Investments', 'Clearview Capital', 'Linden', 'Incline Equity', 'Arbor Private Investment Company', 'SigmaBleyzer', 'HCI Equity Partners', 'McCarthy Capital', 'Blue Point Capital Partners', 'M/C Partners', 'Prairie Capital', 'Skyline Ventures', 'TZP Group', 'Sterling Investment Partners', 'Glencoe Capital', 'Northwestern Mutual Capital Management', 'Beringea Private Equity', 'TCW Group', 'Telegraph Hill Partners', 'Castle Creek Capital Partners', 'FTV Capital', 'Goldner Hawn Johnson & Morrison', 'Capital Partners', 'Black Canyon', 'Capital Z Partners', 'HIG Growth Partners', 'Centerview Capital', 'Galen Partners', 'Tower Three Partners', 'Valor Equity Partners', 'Victory Park Capital', 'Frontenac Company', 'Kainos Capital', 'The Raine Group', 'High Road Capital Partners', 'Peterson Partners', 'Summer Street Capital Partners', 'Catalyst Investors', 'RFE Investment Partners', 'Industrial Opportunity Partners', 'CapitalSpring', 'Wingate Partners', 'Harren Equity Partners', 'Quad Partners', 'Charterhouse Equity Partners', 'Brentwood Associates', 'BV Investment Partners', 'Trinity Hunt Partners', 'Spire Capital', 'Bison Capital', 'Brookside Group', 'Ferrer, Freeman & Co', 'GF Capital Management', 'Petra Capital Partners', 'Sverica', 'SunTx Capital Partners', 'Encore Consumer Capital', 'Commerce Street Capital', 'Century Capital Management', 'Great Point Partners', 'Gemini Investors', 'Prospect Partners', 'CIVC Partners', 'Mainsail Partners', 'Carson Private Capital', 'Cressey & Co.', 'Garnett & Helfrich Capital', 'Swander Pace Capital', 'ACI Capital', 'LaSalle Capital', 'River Associates', 'Small Enterprise Assistance Funds', 'Evercore Partners', 'Bunker Hill Capital', 'Falconhead Capital', 'Bedminster Capital Management', 'Blue Sage Capital', 'Liberty Partners', 'Vance Street Capital', 'CIC Partners', 'Corinthian Capital', 'ICV Partners', 'Greyrock Capital Group', 'FdG Associates', 'MTS Health Partners', 'Eureka Growth Capital', 'SFW Capital Partners', 'Patriot Financial Partners', 'Relativity Capital', 'ShoreView Industries', 'Stonebridge Partners', 'Stonehenge Partners', 'Vanterra Capital', 'ZS Fund', 'Rizvi Traverse Management', 'Lone Star Investment Advisors', 'Foundation Energy Company', 'Winona Capital Management', 'Mistral Equity Partners', 'Silver Oak Services Partners', 'Thomas Weisel Global Growth Partners', 'Stone Arch Capital', 'MD Sass Investors Services', 'Chapter IV Investors', 'Halyard Capital', 'Saw Mill Capital', 'DFW Capital', 'Century Park Capital Partners', 'Gen Cap America', 'Inverness Graham Investments', 'Aterian Investment Partners', 'ValStone Partners', 'Clarion Capital Partners', 'Hancock Park Associates', 'RLJ Equity Partners', 'Equifin Capital Partners', 'Navigation Capital Partners', 'Nogales Investors', 'Transportation Resource Partners', 'Solamere Capital', 'Palm Beach Capital', 'Wafra Partners', 'Rosemont Investment Partners', 'Friend Skoler Equity Partners', 'Parallel Investment Partners', 'Health Enterprise Partners', 'Chart Capital Partners', 'LINX Partners', 'CID Capital', 'Calvert Street Capital Partners', 'Goode Partners', 'MBF Healthcare Partners', 'Yellow Wood Partners', 'Falfurrias Capital Partners', 'Bruckmann Rosser Sherrill & Co', 'Clarity Partners', 'The Rohatyn Group', 'Avante Mezzanine Partners', 'Walnut Group', 'Silverhawk Capital Partners', 'CapStreet Group', 'Kubera Partners', 'Webster Capital', 'Content Partners', 'Hammond, Kennedy, Whitney & Co.', 'Cohesive Capital', 'Altitude Capital Partners', 'Altus Capital Partners', 'BlackEagle Partners', 'Dominus Capital', 'Exhilway Global', 'First Atlantic Capital', 'Pine Tree Equity Partners', 'Pittsford Ventures Management', 'Smith Whiley & Company', 'Spell Capital Partners', 'Hudson Ferry Capital', 'Belvedere Capital Partners', 'EIG Global Energy Partners', 'Bow River Capital Partners', 'Dos Rios Partners', 'Stellus Capital Management', 'Firebird Management', 'Blackstreet Capital Management', 'THL Credit Advisors', 'Tonka Bay Equity Partners', 'Marwit Investment Management', 'Carrick Capital Partners', 'Renovus Capital Partners', 'New Heritage Capital', 'EDG Partners', 'F.N.B. Capital Partners', 'Tengram Capital Partners', 'Beekman Group', 'Long Point Capital', 'San Francisco Equity Partners', 'Boston Millennia Partners', 'Tuckerman Capital', 'Virgo Capital', 'Fulham & Co.', 'Kirtland Capital Partners', 'Leeds Novamark Capital', 'Vicente Capital Partners', 'Dowling Capital Partners', 'Bridgescale Partners', 'Lineage Capital', 'McNally Capital', 'EMP Global', 'Mill City Capital', 'BelHealth Investment Partners', 'Estancia Capital Management', 'MVP Capital Partners', 'Oxford Bioscience Partners', 'Seacoast Capital', 'Seguin Partners', 'Sheridan Legacy Group', 'Stratim Capital', 'TGF Management Corporation', 'Transom Capital Group', 'Vintage Capital Group', 'ZelnickMedia', 'Balmoral Funds', 'Atlantic Street Capital', 'New Capital Partners', 'OFS Energy', 'Palisade Capital Management', 'Prism Capital', 'Strength Capital Partners', 'Cordish Private Ventures', 'GESD Capital Partners', 'Founders Equity', 'Bankcap Partners', 'Topspin Partners', 'Deerpath Capital', 'Guardian Capital Partners', 'Pelican Energy Partners', 'Seaport Capital', 'Vintage Capital Management', 'Hastings Equity Partners', 'DeltaPoint Capital Management', 'Consonance Capital Partners', 'Rosemont Solebury', 'Atlanta Equity Partners', 'Azalea Capital', 'Creation Investments Capital Management', 'Hopewell Ventures', 'Broadhaven Capital Partners', 'Salem Halifax Capital Partners', 'The Vistria Group', 'Advect Group', 'J M H Capital Management', 'CapitalWorks', 'Convergent Capital', 'Forsyth Capital Investors', 'Green Brook Capital Management', 'North Castle Partners', 'Purepay Capital', 'SMS Capital', 'Svoboda Capital Partners', 'Tamarix Capital', 'Trevi Health Ventures', 'North Atlantic Capital Corp', 'Marquette Capital Partners', 'TVC Capital', 'Fort Point Capital', 'Riverlake Partners', 'Prometheus Partners', 'Meritage Funds', '21st Century Group', 'Capitaline Advisors', 'Lakeview Equity Partners', 'Parallax Capital Partners', 'Buckingham Capital Partners', 'Hamilton Robinson', 'Tower Arch Capital', 'High Street Capital', 'Invision Capital Group', 'Torch Lake Capital Partners', 'Black Diamond Capital Partners', 'Larsen MacColl Partners', 'HealthEdge Investment Partners', 'Alumni Capital Network', 'Dolphin Capital Group', 'Owner Resource Group', 'FCF Partners', 'Solis Capital Partners', 'Generation Growth Capital', 'Capital For Business', 'Fireman Capital Partners', 'LongueVue Capital', 'Waveland Capital Partners', 'Ironwood Partners', 'TGP Investments', 'Trillium Group', 'Ticonderoga Capital', 'Vulcan Capital Management', 'Partnership Capital Growth Investors', 'Pine Creek Partners', 'Bravo Equity Partners', 'Elixir Capital', 'Ridgewood Capital', 'Satori Capital', 'White Oak Group', 'MCM Capital Partners', 'Cotton Creek Capital', 'Presidio Financial Partners', 'Brass Ring Capital', 'Corridor Capital', 'Bridge Street Capital Partners', 'CMS Mezzanine', 'Copeley Capital', 'Dubin Clark', 'Evolution Capital Partners', 'LFE Capital', 'Pacific Lake Partners', 'T Squared Partners', 'Main Street Resources', 'Plaza Belmont Management Group', 'Edgewater Capital Partners', 'FedCap Partners', 'HB Equity Partners', 'Quantum Wave Fund', 'Warson Capital Partners', 'Shore Capital Partners', 'C&B Capital', 'JPB Capital Partners', 'Heron Capital', 'TVV Capital', 'Inter-Atlantic Group', 'Staley Capital', 'Corbel Structured Equity Partners', 'Islington Capital Partners', 'Artemis Capital Partners', 'Vopne Capital', 'Endeavor Capital Management', 'Seven Mile Capital Partners', 'Adventure Funds', 'Crystal Ridge Partners', 'Southport Lane', 'Supply Chain Equity Partners', 'Appletree Capital', 'Axum Capital Partners', 'Horizon Capital Partners', 'Saugatuck Capital', 'Yellowstone Group', 'Axiom Capital Group', 'Axia Partners', 'Rockbrook Advisors', 'UNC Kenan-Flagler Private Equity Fund', 'White Wolf Capital', '20/20 HealthCare Partners', '3 Rivers Capital', '3G Capital', '3K Limited Partnership', '3P Capital', '3P Equity Partners', '6Pacific', 'Accelerated Venture Partners', 'Acorn Growth Companies', 'Addison Capital Partners', 'Admiralty Partners, Inc.', 'AEP Capital', 'AeroEquity', 'AFI Partners', 'AG Capital Partners', 'Agamya Capital', 'Agincourt Capital Partners', 'Agio Capital Partners', 'AGR Partners', 'Agribusiness Management Company', 'AgVictus Capital Management', 'Akin Bay', 'Alerion Capital Group', 'Alleghany Corporation', 'Alliance Warburg Capital Management', 'Alpha Capital Partners', 'Alpine Pacific Capital', 'Alston Capital Partners', 'Alta Communications', 'Alta Equity Partners', 'Altpoint Capital Partners', 'Amalgamated Capital', 'Amulet Capital Partners', 'Amvensys Capital Group', 'Anchor Capital', 'Ancor Capital Partners', 'Andlinger & Company', 'Annapurna Capital Management', 'Annex Capital Management', 'Antson Capital Partners', 'AP Capital Partners', 'Arcady Capital Company', 'Arch Equity Partners', 'Argenta Partners', 'Argentum', 'Argo Management Partners', 'Argonne Capital Group', 'Ascendant Capital', 'AUA Private Equity Partners', 'Audubon Capital', 'Augusta Columbia Capital', 'Aureus Capital', 'Austin Capital Partners', 'B12 Capital Partners', 'Bank of America Capital Investors', 'Bard Capital Group', 'Bariston Partners', 'Barken Holdings', 'Barton Creek Equity Partners', 'Bay Grove Capital', 'Berwind Private Equity', 'BHMS Investments', 'Blackland Group', 'BlackRock Capital Partners', 'Blackthorne Partners', 'Blu Venture Investors', 'Blue Heron Capital', 'Blue Horizon Equity', 'Blue Ocean Equity Partners', 'Blue Road Capital', 'Bolder Capital', 'Boss Group', 'Bosworth Capital Partners', 'Boulder Brook Partners', 'Boyne Capital Partners', 'Braddock Holdings Company', 'Bradford Equities Management', 'Branford Castle', 'Breakwater Investment Management', 'Bregal Partners', 'Bregal Sagemount', 'Bridge East Management', 'Bridge Growth Partners', 'Bridge Investments', 'Bridge Lane Capital', 'BrightPath Capital', 'Brook Street Investments', 'Brookstone Partners', 'Buffalo Capital Partners', 'BV Group', 'Cambria Group', 'Cameron Holdings', 'CameronBlue Capital', 'Canal Partners', 'Candescent Partners', 'Cantor Capital Partners', 'Canyon River Capital Partners', 'Capas', 'Cape Oak Capital', 'Capital Acceleration Partners', 'CapitalAsia', 'Capitol Partners', 'Capricorn Holdings', 'Capstar Partners', 'Capstone Capital Partners', 'Cardinal Equity Partners', 'Carlisle Enterprises', 'Carrboro Capital', 'Cartica Capital', 'Cascade Partners', 'Castle Crow & Company', 'Castle Island Partners', 'Catalus Capital', 'Catalyst Management', 'Cave Creek Capital Management', 'Caymus Equity Partners', 'CCCC Growth Fund', 'Celerity Partners', 'Centurion Capital', 'Champlain Capital Partners', 'Charter Oak Equity', 'Chartwell Investments', 'Cheyenne Capital', 'Chicago Venture Partners', 'Cimarron Infrastructure Group', 'CIP Capital', 'Circle Peak Capital Management', 'Citron Capital', 'Clarey Capital', 'Clean Energy Capital', 'Cloquet Capital Partners', 'CloudBreak Capital', 'Clover Investment Group', 'CM Equity Partners', 'Cognitive Capital Partners', 'Colchester Capital', 'Cold Mountain Capital', 'Colony Capital', 'Colville Capital', 'Commonwealth Investment Partners', 'Compass Diversified Holdings', 'Concentric Equity Partners', 'Concorde Group', 'Connemara Capital Company', 'Continental Investors', 'Continuum Capital Partners', 'Copley Equity Partners', 'Coppermine Capital', 'Coral Reef Capital', 'Cordova Ventures', 'Cordova, Smart & Williams', 'Cornerstone Capital Holdings', 'Cornerstone Equity Investors', 'Cornerstone Holdings', 'Corona Investment Partners', 'Corporate Fuel', 'CounterPoint Capital Partners', 'Courtney Group', 'Crane Street Capital', 'Cranemere', 'Crimson Investment', 'Crofton Capital', 'Crosse Partners', 'CrossHarbor Capital Partners', 'Crossroads Capital Partners', 'CS Capital Partners', 'Culbro', 'Current Capital', 'Cypress Group', 'D Cubed Group', 'D2K Equity Partners', 'Danville Partners', 'Davis, Tuttle Venture Partners', 'DBI Capital', 'DC Capital Partners', 'Delos Capital', 'Denali Partners', 'Denargo Capital', 'Dering Capital', 'DGZ Capital', 'Diamond Equity Partners', 'DigaComm', 'Dimeling Schreiber & Park', 'Dinan & Company', 'Diversis Capital', 'DLB Capital', 'Dogwood Equity', 'Driehaus Private Equity', 'DTI Capital', 'Dubilier & Company', 'Duff Ackerman & Goodrich Private Equity', 'Dunes Point Capital', 'Dyad Partners', 'E&A Companies', 'Eastport Operating Partners', 'Education Growth Partners', 'EG Capital Group', 'Egis Capital Partners', 'Egret Capital Partners', 'Eigen Capital', 'Elk Lake Capital', 'Elm Creek Partners', 'Emerald Asset Management', 'Emigrant Capital', 'Emil Capital Partners', 'Encina Capital Partners', 'Enhanced Capital Partners', 'Ennovance Capital', 'Enterprise Partners Venture Capital', 'Entrepreneur Partners', 'Equinox Capital', 'Equis Capital Partners', 'Equity South Partners', 'Equus Capital Management', 'Esposito Private Equity Group', 'Exaltare Capital Partners', 'Exigen Capital', 'Expedition Capital Partners', 'Fairfax Partners', 'Family Capital Growth Partners', 'Fellowship Capital Partners', 'Fenwick Capital Group', 'Financo', 'Five Crowns Capital', 'Five Peaks Capital Management', 'Five Point Capital Partners', 'Flexis Capital', 'Florida Value Fund', 'Foghorn Capital', 'Forest Hill Capital', 'Fort\xc3\xa9 Capital Advisors', 'Foundation Capital Partners', 'Foundation Investment Partners', 'Founders Court', 'Four Seasons Venture Capital', 'Fox Paine & Company', 'Fremont Private Holdings', 'Fulton Capital', 'Fundamental Capital', 'G.L. Ohrstrom & Co.', 'Gallagher Industries', 'Garrison Street', 'Gart Capital Partners', 'GC Capital', 'GE Capital, Equity', 'Generation Equity Investors', 'Generation Partners', 'Generation3 Capital', 'Genesis Park', 'Geneva Glen Capital', 'Georgia Oak Partners', 'Gilbert Global Equity Partners', 'Gladstone Investment', 'Gleacher & Company', 'GlendonTodd Capital', 'Global Emerging Markets', 'Global Healthcare Partners', 'Goense & Company', 'Gordian Capital', 'Goya Capital', 'GPX Enterprises', 'Graham Allen Partners', 'Grail Partners', 'Gramercy', 'Gramercy Park Capital Management', 'Granite Creek Partners', 'Graycliff Partners', 'Graylight Partners', 'Great Circle Capital', 'Great Range Capital', 'Greenstreet Equity Partners', 'Greenwoods Capital Partners', 'Grouse Ridge Capital', 'GrowthPath Capital', 'GTG Capital Partners', 'GTI Group', 'H Equity Partners', 'Hadley Capital', 'Hale Capital Partners', 'Halpern, Denny & Co', 'Hamilton Investment Partners', 'Hampshire Equity Partners', 'Han Capital', 'Hanover Partners', 'Harbinger', 'Harding Partners', 'Harlingwood Equity Partners', 'Hart Capital', 'HealthCap', 'Helios Capital', 'Hermitage Equity Partners', 'Hidden Lion Partners', 'Highlander Partners', 'HighPoint Capital', 'Hilco Brands', 'HLL Partners', 'Holding Capital', 'Holland Park Capital', 'Hovde Private Equity Advisors', 'Howard Industries', 'Hughes & Company', 'Hunter Equity Capital', 'Hypatia Capital', 'ICE Capital', 'Imperial Private Equity', 'Incyte Capital Holdings', 'Indigo Partners', 'Industrial Renaissance', 'Insignia Capital Group', 'InTandem Capital Partners', 'Invemed Associates', 'Inverness Management', 'Investor Growth Capital', 'Invus Group', 'Isaac Organization', 'Isis Venture Partners', 'Island Forest Enterprises', 'J.P. Kotts & Company', 'J.W. Childs Associates', 'J2 Partners', 'Jacobs Private Equity', 'Jaguar Capital Partners', 'January Partners', 'Joshua Partners', 'Juggernaut Capital Partners', 'Jump Capital Partners', 'Juniper Ventures', 'Jupiter Partners', 'JWI Capital', 'JZ Capital Partners', 'K.R. Abraham & Co.', 'Kachi Partners', 'Kale Holdings', 'Kamylon Capital', 'KCA Partners', 'KCB Management', 'Kelly Capital', 'Kern Whelan Capital', 'Kerppola Nordic Investments', 'Kerry Capital Advisors', 'Keystone Capital', 'Kidd & Company', 'Kildare Enterprises', 'Kinsale Capital Partners', 'KleinPartners Capital Corporation', 'KLH Capital', 'Kline Hawkes & Co', 'Knox Lawrence International', 'L2 Capital', 'Labrador Capital', 'Laguna Canyon Capital', 'Lagunita Capital', 'Lake Pacific Partners', 'Lake Rudd Capital Partners', 'Lakemark Partners', 'Lakewood Capital', 'LaMarch Capital', 'Lampstand Investments', 'Lao Golden Capital', 'Lariat Partners', 'LaunchEquity Partners', 'Laurel Capital Partners', 'Laurel Crown Partners', 'Lazarus Capital Partners', 'Lead Lap Enterprises', 'Leading Ridge Capital Partners', 'Leland Capital', 'Le\xc3\xb3n, Mayer & Co.', 'Leonis Partners', 'Liberation Capital', 'Liberty Associated Partners', 'Liberty Hall Capital Partners', 'Liberty Lane Partners', 'Lion Chemical Capital', 'Lionheart Ventures', 'LMW2 Partners', 'London Bay Capital', 'Lone Rock Technology Group', 'Lone Star Funds', 'Longmeadow Capital Partners', 'Longport Capital', 'Longview Capital Partners', 'Lookout Capital', 'Lovett Miller & Co', 'LV2 Equity Partners', 'Lynwood Capital', 'MacAndrews & Forbes Holdings', 'Madison Capital Partners', 'Madison Parker Capital', 'Magna Capital', 'Mantucket Capital', 'Maroon Capital Group', 'Marwood Group', 'Maxim Partners', 'Maybrook Capital Partners', 'MBH Enterprises', 'MC Asset Management Holdings', 'MDM Equity Partners', 'Med Opportunity Partners', 'Medallion Capital', 'MedEquity Capital', 'Medusa Capital Partners', 'Melwood Capital', 'Meriturn Partners', 'Metapoint Partners', 'MidCap Equity Partners', 'Midmark Capital', 'MidStates Capital', 'Milestone Merchant Partners', 'Momentum Capital Partners', 'Monhegan Partners', 'Montage Partners', 'Montis Capital', 'Monument Capital Group', 'Monument Capital Partners', 'Moriah Partners', 'Morningside Private Investors', 'Morris Capital Management', 'Mosaic Investment Partners', 'Mountain Group Capital', 'Mountaineer Capital', 'Moxie Capital', 'MSD Capital', 'MTN Capital Partners', 'Murphy & Partners', 'MVC Capital', 'Najafi Companies', 'Neff Capital Management', 'New England Capital Partners', 'New Gate Capital Partners', 'New MainStream Capital', 'New State Capital Partners', 'Newport Partners', 'Next Point Capital', 'NGP Energy Technology Partners', 'Nicolet Capital Partners', 'Nicollet Capital Investors', 'Nimes Capital', 'Ninth Street Capital Partners', 'Noble Capital', 'North American Funds', 'North Cove Partners', 'North River Capital', 'North State Capital Investors', 'North Street Capital', 'Northwest Capital Appreciation', 'Noson Lawen Partners', 'NRDC Equity Partners', 'NxGen Partners', "O'Brien Capital", 'O2 Investment Partners', 'Oasis Capital Partners', 'Old Willow Partners', 'Olympic Valley Capital', 'One Equity Partners', 'One Rock Capital Partners', 'OpenGate Capital', 'Oppenheimer Alternative Investment Management', 'Opus Financial Partners', 'Opus Global Holdings', 'Opus Partners', 'Opus8, Inc.', 'Orchard Holdings', 'Overall Capital Partners', 'Pacesetter Capital Group', 'Pacific Growth Partners', 'Pacific Life Private Equity', 'Pacific Venture Group', 'PAG Capital Partners', 'Palladian Capital Partners', 'Paragon Equity Group', 'Parami Capital Management', 'Pareto Capital Group', 'Park Avenue Equity Management', 'Parkview', 'PCG Capital Partners', 'Pegasus Capital Group', 'Pelagic Capital Advisors', 'Penn Venture Partners', 'Peppertree Capital Management', 'Phare Capital', 'Phoenix Asset Management', 'Phoenix Financial Holdings', 'Pier Six Capital', 'Pilgrim Capital Partners', 'Pivotal Group', 'Platinum Group', 'Plenary Partners', 'PNC Riverarch Capital', 'Pocket Ventures', 'Point Lookout Capital Partners', 'Poplar Partners', 'Post Capital Partners', 'Potomac Equity Partners', 'Powell Growth Capital', 'Preston Hollow Capital', 'Prides Capital', 'Pritzker Group Private Capital', 'Private Equity Capital Corporation', 'Prodos Capital Management', 'Progress Equity Partners', 'Promus Equity Partners', 'Protostar Partners', 'PS Capital Partners', 'PSP Capital Partners', 'Public Pension Capital Management', 'Pummerin Investments', 'Q Investments', 'Quadrant Management', 'Quarry Capital Management', 'R.A.F. Industries', 'Ramco Capital Corp.', 'Raymond James Capital', 'RBx Capital', 'Red Acre Capital', 'Red Barn Investments', 'Red Oak Capital', 'Red Oak Growth Partners', 'Red River Ventures', 'Red Top Capital', 'Redborn Capital Partners', 'Renova Capital Partners', 'Republic Financial Private Equity', 'Reservoir Capital Group', 'Revelstoke Capital Partners', 'Revere Merchant Capital', 'Revolution Capital Group', 'RHV Capital', 'Richard L. Scott Investments', 'Ridge Capital Partners', 'Ridge Road Partners', 'Ridgeview Capital', 'Rigel Associates', 'Riker Capital', 'Ripplewood Holdings', 'River Branch Holdings', 'River Capital', 'Riverstone Growth Partners', 'RNS Capital Partners', 'Rock Gate Partners', 'Rockbridge Growth Equity', 'RockPool Private Capital', 'RockWood Equity Partners', 'Ropart Asset Management Funds', 'Rosser Capital Partners', 'Roundwood Capital', 'Royal Palm Capital Partners', 'RSA Capital', 'RUBICON Technology Partners', 'Rural American Fund', 'Saban Capital Group', 'Sagamore Capital', 'Sage Capital', 'Salt Creek Capital Management', 'Sampa Partners', 'Sandia Capital Partners', 'Sandstone Capital', 'Saratoga Partners', 'Scimitar Capital', 'Scott Capital Partners', 'SE Capital', 'Selway Capital', 'Sequel Holdings', 'Shackleton Equity Partners', 'Shah Capital Partners', 'Shore Points Capital', 'Sidereal Capital Group', 'Signal Equity Partners', 'SilkRoad Equity', 'Siltstone Capital', 'Silver Beacon Partners', 'Silver Peak Partners', 'Silver Sail Capital', 'Silverfern Co-Investment Partners', 'SilverStream Capital', 'Siva Ventures', 'Skyline Global Partners', 'Skyway Capital Partners', 'Slate Capital Group', 'Snowmass Capital Partners', 'Solera Capital', 'Solic Capital', 'Sound Harbor Partners', 'Source Capital', 'South Atlantic Venture Funds', 'Southern Equity Partners', 'Southlake Equity Group', 'Speyside Equity', 'Spinnaker Capital Partners', 'Spring Bay Capital', 'Stairway Capital', 'Stanwich Partners', 'Staple Street Capital', 'Starboard Capital Partners', 'Steel Capital', 'Steelpoint Capital Partners', 'Stelac Capital Partners', 'Stellar Ventures', 'Stephens Capital Partners', 'Stockton Road Capital', 'Stone-Goff Partners', 'StoneCalibre', 'StoneCreek Capital', 'Stony Lane Partners', 'Strattam Capital', 'Striker Partners', 'Stripes Group', 'Stuart Mill Venture Partners', 'Succession Capital Partners', 'Summit Equity Group', 'Summit Investment Management', 'Summit Park Partners', 'Sun European Partners', 'Sun Mountain Capital', 'Sunland Capital', 'Susquehanna Capital', 'Susquehanna Growth Equity', 'SV Investment Partners', 'Swift River Investment', 'Synetro Capital', 'Taglich Private Equity', 'Taiyo Pacific Partners', 'Talisman Capital Partners', 'Talon Group', 'Tarpon Hill Capital', 'Tavistock Group', 'Texas Next Capital', 'TGV Partners', 'TH Lee Putnam Ventures', 'The Anderson Group', 'The Ballast Fund', 'The BearFund', 'The Compass Group', 'The Dellacorte Group', 'The Ellis Company', 'The Ferrante Group', 'The Stephens Group', 'The Stony Point Group', 'Third Century Management', 'Three Cities Research', 'Thurston Group', 'Tillery Capital', 'Timepiece Capital', 'Titan Equity Partners', 'Torque Capital Group', 'Transition Capital Partners', 'Traveller Capital', 'Trent Capital Partners', 'Triad Capital Management', 'Trilea Capital Partners', 'Trimaran Capital Partners', 'Tritium Partners', 'True North Equity', 'TSG Equity Partners', 'TSI Holding', 'Tulcan', 'Turnbridge Capital', 'Turning Basin Capital Partners', 'Twin Focus Capital Partners', 'Two Six Capital', "Tyree & D'Angelo Partners", 'Tyrian Capital', 'Union Bay Partners', 'Union Capital Corp', 'Union Park Capital', 'Unique Investment Corporation', 'US Equity', 'Valesco Industries', 'Validor Capital', 'Vanguard Atlantic', 'Venatus Capital Partners', 'Vencon Management', 'Venquest Capital', 'Verdis Investment Management', 'Verus International', 'Vinco Capital', 'Virginia Capital', 'Vitesse Capital Partners', 'Vivaris Ltd', 'VO2 Partners', 'Vortus Investments', 'Vulcan Capital', 'Wall Street Technology Partners', 'Wall Street Venture Capital', 'Wand Partners', 'Warwick Group', 'Wasserstein & Co', 'Waveland Investments', 'Weatherly Financial Group', 'Weld North', 'Wellbridge Capital', 'Wells Fargo Capital Finance', 'Werther Partners', 'West Coast Capital', 'West End Holdings', 'Westar Capital', 'Westridge Capital', 'Westward Partners', 'Willcrest Partners', 'Willis Stein & Partners', 'Wing Capital Group', 'Wings Capital Partners', 'Wisdom Capital Partners', 'WJ Partners', 'WMG Capital', 'Woodlawn Partners', 'Worth Investments Group', 'WR Capital Partners', 'Wright Equity Partners', 'WS Capital Partners', 'WSG Partners', 'Wyndham Global Partners', 'YAM Capital', 'Yenni Capital', 'Yorkville Advisors', 'Your Source Partners', 'YVC Partners', 'Zabel Capital']

class Command(BaseCommand):
    help = 'parse files into tags'


    def get_words_from_doc(self, words):
        text_set = set()

        for processed in words:
            if len(processed) > 2 and processed not in STOP_WORDS and not processed.isdigit():
                text_set.add(processed)

        return text_set

    def build_orgs(self, processed_text):
        orgs = []

        for org in ORGS:
            if process_text(org) in processed_text:
                orgs.append(org)

        return orgs

    def handle(self, *args, **options):

        logger.info('****** Adding new docs!****** ')

        rootdir = settings.ROOT_NEW_DIR
        roottxtdir = settings.ROOT_TXT_DIR
        rootdonedir = settings.ROOT_FILE_DIR

        def sort_files(x, y):
            return int(get_number(x)) - int(get_number(y))

        def move_file(file_name):
            if(os.path.isfile(os.path.join(rootdonedir, file_name))):
                os.remove(os.path.join(rootdir, file_name))
                print("Exists\n")
                logger.info('File already exists')
            else:
                shutil.move(os.path.join(rootdir, file_name), rootdonedir)
                print("Moving\n")
                logger.info('Moving file')


        files_in_dir = sorted(os.listdir(rootdir), cmp=sort_files)

        for file_in_dir in files_in_dir:
            if file_in_dir.endswith(".pdf"):

                document_id = get_number(file_in_dir)

                document, created = Document.objects.get_or_create(file_name=file_in_dir, id=document_id)

                print document
                logger.info(document)

                if document.done and not settings.DEBUG:
                    logger.info('Document done')
                    move_file(file_in_dir)
                    continue

                print "new"
                logger.info('New document!')

                f = open(os.path.join(roottxtdir, document_id+'.txt'), 'r')
                pages = f.read()
                f.close()

                doc_processed = process_text(pages)

                orgs = self.build_orgs(doc_processed)

                if len(orgs) > 0 or settings.DEBUG:
                    print orgs

                    document.indexed = True
                    document.document_text = doc_processed

                document.done = True
                document.save()

                db.reset_queries()

                move_file(file_in_dir)
