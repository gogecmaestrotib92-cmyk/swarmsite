import base64, subprocess, re
html=open('v2/sportbot-v2.html').read()
tok=subprocess.run(['python3','-I','lib/css/tokens.py','C1','dark','#10B981','Barlow Condensed'],capture_output=True,text=True).stdout
tok='\n'.join(l for l in tok.splitlines() if not l.startswith('/*'))
# concept-pure alternatives (user toggles in intro): font + colour
tok+='''
html[data-font="concept"]{--font-display:'Space Grotesk',system-ui,sans-serif;--display-weight:600}
html[data-color="concept"]{--accent:#FA3600;--accent-ink:#FA3600;--accent-contrast:#FFFFFF;--mv-highlight:#FA3600}
'''
comp=open('lib/css/components.css').read()
moves=open('lib/motion/moves.js').read()
swarm=open('swarm.js').read().replace("const BOX_SEL = '.card, .record, .rows li, .ways > div, .plans > div, .lifetime, .faq details, .rg, .stores a, .pricelist li, .stats .grid div, .btn, nav';","const BOX_SEL = '.card, .cells > div, .frame, .rows li, .lifetime > div, .faq details, .btn, .nav, .marquee, .pillbar';")
img=base64.b64encode(open('before_hero.jpg','rb').read()).decode()
intro=open('v2/intro.js').read().replace('IMG',img)
import json as _j; assets=_j.load(open('lib/audit/sportbot_assets.json')); html=html.replace('{{LOGO}}',assets['logo']['data'])
html=html.replace('family=Barlow+Condensed','family=Space+Grotesk:wght@300..700&family=Barlow+Condensed').replace('/*TOKENS*/',tok).replace('/*COMPONENTS*/',comp).replace('<script>/*MOVES*/</script>','<script>'+moves+'</script>').replace('<script>/*SWARM*/</script>','<script>'+swarm+'</script>').replace('/*INTRO*/',intro)
open('v2/index.html','w').write(html); print(len(html))
