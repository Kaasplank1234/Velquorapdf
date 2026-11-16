"""Fetch a curated, redistributable desktop font collection during release builds."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import time

FAMILIES = """
arimo tinos cousine carlito
inter roboto opensans montserrat lato poppins raleway nunito sourcesans3 worksans dmsans
manrope rubik urbanist outfit plusjakartasans figtree geist instrumentsans notosans
ibmplexsans publicsans archivo barlow cabin assistant karla mulish lexend cabincondensed
dosis quicksand josefinsans hind oxygen catamaran exo2 exo overpass redhatdisplay redhattext
readexpro sora epilogue onest afacad splinesans commissioner bevietnampro spacegrotesk
spacemono jetbrainsmono robotomono firacode firasans firasanscondensed ibmplexmono
inconsolata anonymouspro cousine courierprime cutivemono sharetechmono ubuntu ubuntumono
ubuntusans ubuntusansmono dmmono novamono playfairdisplay merriweather lora librebaskerville
librecaslontext crimsontext crimsonpro cormorantgaramond cormorant cormorantinfant spectral
vollkorn bitter literata fraunces dmseriftext dmserifdisplay oldstandardtt neuton alegreya
alegreyasans gentiumplus gentiumbookplus notoserif notoserifdisplay ptserif ptsans
ptsansnarrow librefranklin frankruhllibre oswald anton bebasneue teko titilliumweb rajdhani
chivo chivomono kanit prompt sarabun athiti baijamjuree chakrapetch acme alfaslabone bangers
bungee bungeeshade cabinsketch concertone fredoka baloo2 comfortaa varelaround varela
grandstander patrickhand architectsdaughter caveat permanentmarker satisfy pacifico
dancingscript greatvibes allura kaushanscript yellowtail lobster lobstertwo cookie
sacramento badscript marckscript shadowsintolight indieflower kalam handlee gloriahallelujah
amaticsc comicneue delius gochihand justanotherhand comingsoon rocksalt reeniebeanie
shalimar tangerine italianno parisienne abrilfatface cinzel cinzeldecorative bodonimoda
gfsdidot prata yesevaone forum marcellus marcellussc sortsmillgoudy ebgaramond cardo taviraj
trirong alice vidaloka rokkitt arvo robotoslab zillaslab robotoserif adamina amiri arapey
asul bellefair belleza cantataone caudex enriqueta faustina glegoo habibi imfellenglish
imfellenglishsc jost albertsans lexenddeca sen aneklatin arimo archivonarrow archivoblack
barlowcondensed barlowsemicondensed economica newscycle pathwaygothicone tinos abel aboreto
actor adventpro agdasima alata aldrich alef alkatra allerta allertastencil amaranth andika
antic anticdidone anticslab arbutus arbutusslab asap asapcondensed asset audiowide
averialibre averiasanslibre averiaseriflibre balsamiqsans balthazar baskervville belanosima
bentham berkshireswash bigshoulders bigshouldersstencil bonbon brygada1918 bubblegumsans
cairo carlito carroisgothic changa courgette delagothicone didactgothic dynapuff electrolize
emblemaone encodesans fahkwang fanwoodtext fugazone gabriela gelasio georama gildadisplay
glory gupter hankengrotesk heebo heptaslab hubotsans inriasans inriaserif istokweb itim
jaldi juliussansone k2d kameron karma khand khula kreon kufam kumbhsans ledger leaguegothic
leaguespartan lemonada lusitana lustria mada magra maitree mali manuale markazitext martel
martelsans mate matesc mclaren
"""

def fetch(url):
    headers = {'User-Agent': 'Velqora-PDF-build'}
    token = os.environ.get('VELQORA_FONT_TOKEN')
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = 'Bearer ' + token
    request = Request(url, headers=headers)
    for attempt in range(4):
        try:
            with urlopen(request, timeout=40) as response:
                return response.read()
        except OSError:
            if attempt == 3:
                raise
            time.sleep(attempt + 1)

def tree(ref, recursive=False):
    query = '?recursive=1' if recursive else ''
    data = json.loads(fetch('https://api.github.com/repos/google/fonts/git/trees/' + ref + query))
    if data.get('truncated'):
        raise RuntimeError('The upstream font tree was truncated.')
    return data

def main():
    commit = json.loads(fetch('https://api.github.com/repos/google/fonts/commits/main'))['sha']
    root = tree(commit)
    ofl = next(entry['sha'] for entry in root['tree'] if entry['path'] == 'ofl')
    families = {}
    for entry in tree(ofl, recursive=True)['tree']:
        family, separator, path = entry['path'].partition('/')
        if separator and '/' not in path:
            families.setdefault(family, []).append(path)

    choices = []
    for name in dict.fromkeys(FAMILIES.split() + sorted(families)):
        files = families.get(name, [])
        if 'OFL.txt' not in files or 'METADATA.pb' not in files:
            continue
        fonts = [file for file in files if file.endswith('.ttf') and 'italic' not in file.lower()]
        if fonts:
            filename = min(fonts, key=lambda file: ('-Regular.ttf' not in file, '[' not in file, len(file)))
            choices.append((name, filename))
        if len(choices) == 200:
            break
    if len(choices) != 200:
        raise RuntimeError('Could not resolve 200 OFL families.')

    dest = Path(__file__).resolve().parents[1] / 'assets/fonts'
    dest.mkdir(exist_ok=True)
    def download(item):
        slug, filename = item
        base = f'https://raw.githubusercontent.com/google/fonts/{commit}/ofl/{slug}/'
        folder = dest / slug
        folder.mkdir(exist_ok=True)
        for name in (filename, 'OFL.txt', 'METADATA.pb'):
            (folder / name).write_bytes(fetch(base + quote(name)))
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(download, choices))
    (dest / 'source.txt').write_text(f'https://github.com/google/fonts/tree/{commit}/ofl\n')
    print(f'Bundled {len(choices)} OFL font families at {commit}.', flush=True)

if __name__ == '__main__':
    main()
