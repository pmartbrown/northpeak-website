#!/usr/bin/env python3
"""Build North Peak Recovery static site (RQF pattern: one folder per page, index.html).
Run from repo root:  python3 src/build_pages.py
Inputs: assets/states.json, src/us-paths.json (Wikimedia Commons 'Blank US Map (states only).svg', public domain).
"""
import json, os, html
BASE=os.environ.get('BASE','').rstrip('/')  # e.g. BASE=/northpeak-website for GitHub Pages preview
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATES=json.load(open(os.path.join(ROOT,'assets/states.json')))
PATHS=json.load(open(os.path.join(ROOT,'src/us-paths.json')))
SITE='https://northpeakrecovery.com'
LOGO='<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M2 27 12 9l5 8 4-6 9 16z" fill="#1f6f5c"/><circle cx="25" cy="7" r="3.5" fill="#f2b544"/></svg>'

def page(path,title,desc,body,cls=''):
    nav=[('/how-it-works/','How it works'),('/what-are-surplus-funds/','Surplus funds'),('/states/','States'),('/faq/','FAQ'),('/about/','About'),('/beware-of-scams/','Avoid scams')]
    navh=''.join(f'<li><a href="{h}">{t}</a></li>' for h,t in nav)
    doc=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}{path}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<link rel="stylesheet" href="/assets/site.css">
</head><body class="{cls}"><a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap nav"><a class="logo" href="/">{LOGO} North Peak Recovery</a>
<nav aria-label="Main"><ul>{navh}</ul></nav></div></header>
<main id="main">{body}</main>
<footer class="site"><div class="wrap grid g3">
<div><strong>North Peak Recovery</strong><br>Helping former owners find surplus funds after a foreclosure or tax sale, nationwide.<br>1873 West Traverse Parkway, Suite E 521<br>Lehi, Utah 84043</div>
<div><a href="/check-my-funds/">Check my funds</a><br><a href="/states/">State guides</a><br><a href="/beware-of-scams/">How to avoid scams</a><br><a href="/loan-recovery/">For private lenders</a></div>
<div><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/disclosures/">Disclosures</a><p class="small" style="color:#cfd8e6">North Peak Recovery is not a law firm and is not a government agency. Legal work is performed by independent licensed attorneys. You can always file a claim yourself, at no cost.</p></div>
</div></footer><script src="/assets/site.js"></script></body></html>'''
    if BASE: doc=doc.replace('href="/','href="'+BASE+'/').replace('src="/','src="'+BASE+'/').replace('<html lang="en">','<html lang="en" data-base="'+BASE+'">')
    d=os.path.join(ROOT,path.strip('/')) if path not in ('/','/404.html') else ROOT
    os.makedirs(d,exist_ok=True)
    fn=os.path.join(ROOT,'404.html') if path=='/404.html' else os.path.join(d,'index.html')
    open(fn,'w').write(doc)

def state_options(sel=''):
    return '<option value="">Choose a state…</option>'+''.join(f'<option value="{s["abbr"]}" data-slug="{s["slug"]}"{" selected" if s["name"]==sel else ""}>{s["name"]}</option>' for s in STATES)

def lead_form(fid,state_val='',state_select=True,hidden_state=False):
    if hidden_state: st=f'<input type="hidden" name="state" value="{html.escape(state_val)}">'
    elif state_select: st=f'<label for="{fid}-st">State where the home was sold</label><select id="{fid}-st" name="state" required>{state_options(state_val)}</select>'
    else: st=''
    return f'''<form class="lead" novalidate>
<input type="hidden" name="form" value="{fid}">{st}
<label for="{fid}-n">Your name</label><input id="{fid}-n" name="name" autocomplete="name" required>
<label for="{fid}-c">County <span class="small">(if you know it)</span></label><input id="{fid}-c" name="county" autocomplete="off">
<label for="{fid}-y">About what year was it sold?</label><select id="{fid}-y" name="sale_year"><option value="">Not sure</option>{''.join(f'<option>{y}</option>' for y in range(2026,2014,-1))}<option value="before-2015">Before 2015</option></select>
<label for="{fid}-p">Phone</label><input id="{fid}-p" name="phone" type="tel" autocomplete="tel">
<label for="{fid}-e">Email</label><input id="{fid}-e" name="email" type="email" autocomplete="email" required>
<fieldset class="radios"><legend>How should we reach you?</legend>
<label><input type="radio" name="contact_pref" value="phone"> Phone call</label><label><input type="radio" name="contact_pref" value="text"> Text</label><label><input type="radio" name="contact_pref" value="email" checked> Email</label></fieldset>
<div class="check"><label><input type="checkbox" name="consent" value="yes" required><span>I agree that North Peak Recovery may contact me by the method I chose, including by phone or text, about my possible claim. Consent isn’t required to use any service, and I can opt out anytime. Message/data rates may apply. See our <a href="/privacy/">Privacy Policy</a>.</span></label></div>
<p class="err" aria-live="polite"></p>
<button class="btn" type="submit">Check for my funds</button>
<p class="small">Free, no obligation. We will never ask for your Social Security number to check.</p></form>'''

def usmap():
    by={s['abbr'].lower():s for s in STATES}; out=[]
    for k,items in sorted(PATHS.items(),key=lambda x:by[x[0]]['name']):
        s=by[k]; shapes=''.join(f'<path d="{d}"/>' for t,d in items if t=='p')
        if k=='dc': shapes+='<circle cx="801.6" cy="252.1" r="7"/>'
        out.append(f'<a href="/states/{s["slug"]}/" data-state="{s["abbr"]}" data-name="{s["name"]}" data-slug="{s["slug"]}" aria-label="{s["name"]}: check for funds" role="button"><title>{s["name"]}</title>{shapes}</a>')
    return ('<svg class="usmap" viewBox="0 0 959 593" role="group" aria-labelledby="mapTitle">'
            '<title id="mapTitle">Map of the United States. Choose a state to check for surplus funds.</title>'+''.join(out)+'</svg>'
            '<!-- Map: Wikimedia Commons "Blank US Map (states only).svg", public domain. https://commons.wikimedia.org/wiki/File:Blank_US_Map_(states_only).svg -->')

HOW=[('We look','Tell us where and roughly when the home was sold. We search public court, trustee and county records to see if surplus funds exist in your name. Free.'),
     ('We explain','If there’s money, we tell you how much the records show, who is holding it, and every option you have, including filing on your own.'),
     ('Attorneys file','If you want our help, you sign a clear written agreement first. Where the law requires it, an independent licensed attorney prepares and files the claim.'),
     ('You get paid','The court, trustee or county releases the funds. Our fee, if any, is only taken from a successful recovery, as stated in your agreement.')]
def how_cards():
    return '<div class="grid g4">'+''.join(f'<div class="card"><div class="step">{i+1}</div><h3>{t}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(HOW))+'</div>'
EXAMPLE='''<div class="card example" aria-label="Worked example"><div><span>Home sold at auction for</span><span>$285,000</span></div><div><span>Mortgage and costs owed</span><span>− $200,000</span></div><div><span>Other liens paid</span><span>− $10,000</span></div><div class="tot"><span>Surplus that may belong to the former owner</span><span>$75,000</span></div><p class="small">Illustration only. The real amount is set by the court or county record after valid liens and costs.</p></div>'''
TRUST='''<div class="grid g4">
<div class="card"><h3>No upfront fees</h3><p>Checking is free. You never pay us out of pocket.</p></div>
<div class="card"><h3>Attorney partners</h3><p>Independent licensed attorneys handle legal filings where your state requires it.</p></div>
<div class="card"><h3>No SSN to check</h3><p>We will never ask for your Social Security number just to see if funds exist.</p></div>
<div class="card"><h3>You can file yourself</h3><p>Honestly: in most places you can claim surplus funds on your own for free. We’ll even tell you where to start.</p></div></div>'''
FAQS=[('What are surplus funds?','When a home sells at a foreclosure or tax sale for more than what was owed, the extra money (the surplus, also called overage or excess proceeds) is usually owed to the former owner or other people with a legal interest.'),
('Is this a scam?','It’s a fair question, and you should ask it of anyone. Real surplus funds are held by a court, trustee or county, and you can verify them there yourself. We never charge upfront and never ask for your SSN to check. See <a href="/beware-of-scams/">how to spot a scam</a>.'),
('Do I have to use a company?','No. In many states you can file a claim yourself. Some people prefer help because the paperwork, deadlines and competing claims can be complicated.'),
('How much does it cost?','Checking is free. If you choose our help, our fee comes only from a successful recovery and is written into your agreement before anything is filed. Some states cap or restrict fees, and we follow those rules.'),
('How long does it take?','It depends on the state, the county and whether anyone else files a claim. Some claims resolve in a few months; others take longer. We’ll give you an honest estimate.'),
('What if the owner passed away?','Heirs or the estate may be able to claim. Tell us what you know and we’ll look into it.')]
def faq_html(n=None):
    return ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in FAQS[:n])
DIALOG=f'''<dialog id="stateDialog" aria-labelledby="dlgTitle"><div class="dlg"><button class="x" type="button" aria-label="Close">&times;</button>
<h2 id="dlgTitle">Let’s see if money is waiting for you</h2><p class="small">A few details are all we need. No cost, no pressure.</p>
<form class="lead" novalidate><input type="hidden" name="form" value="map-modal"><input type="hidden" name="state" value="">
{lead_form('m',hidden_state=True).split('<input type="hidden" name="state" value="">',1)[1].split('<form class="lead" novalidate>',1)[-1].replace('<input type="hidden" name="form" value="m">','',1)}
<p><a id="dlgLink" href="/states/">Read the state guide</a></p></div></dialog>'''

# ---------- HOME
page('/','North Peak Recovery | Surplus funds after a foreclosure or tax sale',
 'If your home sold at a foreclosure or tax auction for more than you owed, money may be waiting for you. Free, no-pressure check, nationwide.',
f'''<div class="hero"><div class="wrap grid g2" style="align-items:center"><div>
<p class="kicker">Foreclosure &amp; tax sale surplus recovery · Nationwide</p>
<h1>Your home sold at auction. Some of that money may still be yours.</h1>
<p class="lead">When a home sells for more than was owed, the difference is often held for the former owner, and many people are never told. We help you find out, calmly and for free.</p>
<p><a class="btn" href="#map">Check my state</a> <a class="btn ghost" href="/how-it-works/">How it works</a></p></div>
<div class="card"><h2 style="font-size:1.25rem">What to expect</h2><ul><li>A free look at public records</li><li>No upfront fees, ever</li><li>We never ask for your SSN to check</li><li>An honest answer, even if that’s “you can file this yourself”</li></ul><p class="small">Licensed attorney partners handle legal filings where required.</p></div></div></div>
<section id="map"><div class="wrap"><h2>Where was the home sold?</h2><p>Choose a state on the map to start a quick, free check.</p>
<div class="map-wrap">{usmap()}</div>
<div class="card" style="margin-top:1rem"><label for="statePick">Or pick from a list</label>
<div style="display:flex;gap:.5rem;flex-wrap:wrap"><select id="statePick" style="flex:1;min-width:14rem">{state_options()}</select><button class="btn" id="statePickGo" type="button">Start my check</button></div>
<p class="small">Prefer not to use the map? Go to the <a href="/check-my-funds/">full form</a> or browse the <a href="/states/">list of state guides</a>.</p></div></div></section>
<section style="background:#fff"><div class="wrap grid g2"><div><h2>What are surplus funds?</h2>
<p>At a foreclosure or tax sale, the home is sold to pay what was owed. If bidding goes higher than the debt, costs and other liens, there’s money left over. That leftover, called <strong>surplus funds</strong>, overages or excess proceeds, usually belongs to the former owner (or heirs).</p>
<p>The money often sits with a court, trustee or county because the notice went to an address nobody lives at anymore. Rules and deadlines vary by state and county.</p><p><a href="/what-are-surplus-funds/">Learn more about surplus funds</a></p></div><div>{EXAMPLE}</div></div></section>
<section><div class="wrap"><h2>How it works</h2>{how_cards()}</div></section>
<section style="background:#fff"><div class="wrap"><h2>Why people trust us</h2>{TRUST}</div></section>
<section><div class="wrap grid g2"><div><h2>How we get paid</h2><p>We’re a business, and we’d rather say it plainly. We cover the cost of research and, where needed, the attorney’s filing. If the claim succeeds, our fee comes out of the recovered funds at the rate in your written agreement. If it doesn’t succeed, you owe nothing.</p>
<p>Some states cap or restrict these fees, and some don’t allow them at certain times. We follow the rules where your home was sold. And if your claim is simple enough to file on your own, we’ll tell you.</p></div>
<div><h2>Common questions</h2>{faq_html(3)}<p><a href="/faq/">See all questions</a></p></div></div></section>
<section style="background:#e7f3ee"><div class="wrap"><h2>Ready when you are</h2><p>No countdowns, no pressure. If you’d like us to look, it takes about two minutes.</p><a class="btn" href="/check-my-funds/">Check for my funds</a></div></section>
{DIALOG}''')

def simple(path,title,desc,h1,inner,lead=''):
    page(path,title,desc,f'<div class="hero"><div class="wrap"><h1>{h1}</h1>{f"<p class=lead>{lead}</p>" if lead else ""}</div></div><section><div class="wrap">{inner}</div></section>')

simple('/how-it-works/','How it works | North Peak Recovery','Our simple four-step process for recovering foreclosure and tax sale surplus funds.','How it works',
 how_cards()+'''<div class="grid g2" style="margin-top:1.5rem"><div class="card"><h3>What we’ll ask for later (not to check)</h3><ul><li>Photo ID</li><li>Proof you owned the home (deed, mortgage or tax records; we can often find these)</li><li>The county’s claim forms, often notarized</li><li>For heirs: death certificate and estate documents</li></ul></div>
<div class="card"><h3>What you’ll always get</h3><ul><li>The amount the records show, and who holds it</li><li>Your options, including filing yourself</li><li>A written agreement before anything is filed</li><li>Updates at each stage</li></ul></div></div><p style="margin-top:1.5rem"><a class="btn" href="/check-my-funds/">Start a free check</a></p>''',
 'Calm, clear and in writing at every step.')

simple('/what-are-surplus-funds/','What are surplus funds? | North Peak Recovery','A plain-English guide to foreclosure and tax sale surplus funds, overages and excess proceeds.','What are surplus funds?',
 f'''<div class="grid g2"><div><p>When a property is sold at a forced sale, such as a mortgage foreclosure, a sheriff’s sale, a trustee’s sale or a tax sale, the sale pays off what was owed. If the winning bid is higher than the debt, costs and valid liens, the remainder is <strong>surplus funds</strong>.</p>
<h2>Who is entitled?</h2><p>Usually the former owner of record. Junior lienholders may have claims first, and heirs or an estate may claim if the owner has passed away.</p>
<h2>Who holds the money?</h2><p>Depending on the state and sale type, it may be the foreclosure trustee, the clerk of court, the county treasurer or tax collector, or, after time passes, the state’s unclaimed property office.</p>
<h2>Foreclosure vs. tax sale</h2><p><strong>Mortgage foreclosures</strong> can be judicial (through a court) or non-judicial (through a trustee). <strong>Tax sales</strong> happen when property taxes go unpaid. In 2023 the U.S. Supreme Court held in <em>Tyler v. Hennepin County</em> that a county can’t keep more than the tax debt, and many states have updated their laws since.</p>
<h2>Deadlines</h2><p>Many states set claim deadlines, and after that the money may go to the county or state. Rules vary by state and county, and we’ll check yours for free.</p></div><div>{EXAMPLE}<p style="margin-top:1rem"><a class="btn" href="/check-my-funds/">See if any is yours</a></p></div></div>''')

# states index + pages
lis=''.join(f'<li><a href="/states/{s["slug"]}/">{s["name"]}</a></li>' for s in STATES)
simple('/states/','State guides | North Peak Recovery','Surplus funds guides for all 50 states and DC.','Surplus funds by state',
 f'<p>Surplus rules differ by state, and often by county. Choose a state for a short guide and a free check.</p><ul class="statelist">{lis}</ul>')
for s in STATES:
    n=s['name']; note=s.get('note')
    noteh=(f'<div class="card"><h3>A note on {n} rules</h3><p>{note["text"]}</p><p class="small">Source: <a href="{note["source"]}">{note["source"]}</a>. Summary only, not legal advice. Laws change; we confirm current rules on every file.</p></div>' if note else
      f'<div class="card"><h3>Rules in {n}</h3><p>Who holds the money, how to claim, any deadline, and whether fees are limited can depend on the type of sale and the county. <strong>Rules vary, and we’ll check for you.</strong></p></div>')
    page(f'/states/{s["slug"]}/',f'{n} surplus funds recovery | North Peak Recovery',
     f'Did a home sell at a foreclosure or tax sale in {n}? Find out free if surplus funds may be waiting for you.',
     f'''<div class="hero"><div class="wrap"><p class="kicker"><a href="/states/">State guides</a> › {n}</p><h1>Surplus funds in {n}</h1>
<p class="lead">If a home in {n} sold at a foreclosure or tax sale for more than was owed, the former owner or heirs may be able to claim the difference.</p></div></div>
<section><div class="wrap grid g2"><div>
<h2>How it usually works</h2><p>After the sale, the extra money is typically held by the foreclosure trustee, the clerk of court, or a county office until someone with a valid claim comes forward. Notices are often mailed to the old address, so many people never hear about it.</p>
{noteh}
<h2>Can I file myself?</h2><p>Often, yes. The office that handled the sale can tell you whether funds exist and what forms they need. If you’d rather have help, we’ll look for free and explain every option first.</p>
<p><a href="/what-are-surplus-funds/">Learn how surplus funds work</a> · <a href="/beware-of-scams/">How to avoid scams</a></p></div>
<div class="card"><h2 style="font-size:1.35rem">Let’s see if money is waiting for you in {n}</h2>{lead_form("s",n,hidden_state=True)}</div></div></section>''')

simple('/about/','About | North Peak Recovery','Who we are and why we do this work.','About North Peak Recovery',
 f'''<div class="grid g2"><div><p>Losing a home is hard. Finding out that some of its value may still be yours can be a real bright spot. North Peak Recovery exists to help people find that money and get it back the right way: patiently, honestly, and with licensed attorneys where the law requires.</p>
<h2>What we believe</h2><ul><li>You deserve the plain truth, including that you can often file yourself.</li><li>No pressure, no countdown timers, no upfront fees.</li><li>Follow every state’s rules, every time.</li></ul></div>
<div class="card"><h3>Our team</h3><p>Paul Brown, Co-Founder<br>Keefer Brown, Co-Founder</p><h3>Attorney partners</h3><p>North Peak Recovery works with many attorney partners, depending on the state and county, so they aren’t listed individually.</p></div></div>''')

simple('/faq/','FAQ | North Peak Recovery','Answers to common questions about surplus funds recovery.','Frequently asked questions',faq_html()+'<p style="margin-top:1rem"><a class="btn" href="/check-my-funds/">Start a free check</a></p>')

simple('/check-my-funds/','Check my funds | North Peak Recovery','A free, no-obligation check for foreclosure or tax sale surplus funds.','Let’s see if money is waiting for you',
 f'<div class="grid g2"><div class="card">{lead_form("c")}</div><div><h2>What happens next</h2>{how_cards().replace("g4","")}</div></div>','About two minutes. No cost, no pressure.')

simple('/beware-of-scams/','How to avoid surplus funds scams | North Peak Recovery','How to verify any surplus funds offer, including ours.','How to avoid surplus funds scams',
 '''<div class="grid g2"><div><h2>Warning signs</h2><ul><li>Asking for money upfront to “release” your funds</li><li>Asking for your Social Security number or bank login just to check</li><li>Pretending to be a court, county or government agency</li><li>Pressure to sign today, or refusing to show you the agreement</li><li>Won’t tell you the amount or who holds it</li></ul></div>
<div><h2>How to verify anyone, including us</h2><ol><li>Ask which office holds the funds and the case or sale number.</li><li>Call that office yourself using a number from its official website.</li><li>Read any agreement fully. You should see the fee in writing.</li><li>Remember you can usually file on your own for free.</li></ol><p>If you got a letter or call about surplus funds and aren’t sure, we’re happy to help you check, even if you never work with us.</p></div></div>''')

page('/loan-recovery/','Private loan recovery for lenders | North Peak Recovery','Attorney-led recovery for private money and hard money real estate lenders with non-performing loans.',
f'''<div class="hero"><div class="wrap"><p class="kicker">For private &amp; hard money lenders</p><h1>Recover capital from non-performing private real estate loans</h1>
<p class="lead">When a business-purpose real estate loan stops performing, we help lenders review their position, explore a workout or payoff, and pursue remedies through licensed attorneys.</p><a class="btn" href="#submit">Submit a loan for review</a></div></div>
<section><div class="wrap"><h2>How it works</h2><div class="grid g4">
<div class="card"><div class="step">1</div><h3>File review</h3><p>Note, deed of trust or mortgage, guaranties, payment history and title.</p></div>
<div class="card"><div class="step">2</div><h3>Strategy</h3><p>Options: workout, payoff negotiation, deed in lieu, foreclosure, or a judgment on guaranties.</p></div>
<div class="card"><div class="step">3</div><h3>Attorney action</h3><p>Licensed attorneys in the property’s state handle notices, filings and enforcement.</p></div>
<div class="card"><div class="step">4</div><h3>Resolution</h3><p>Recovery, reporting and close-out, with clear updates throughout.</p></div></div>
<p class="small" style="margin-top:1rem">We work with lenders on business-purpose loans secured by investment real estate. We don’t contact consumers on behalf of creditors, and enforcement is handled by licensed attorneys.</p></div></section>
<section id="submit" class="lender-band"><div class="wrap grid g2"><div><h2>Submit a loan for review</h2><p>Confidential.</p></div>
<form class="lead card" novalidate><input type="hidden" name="form" value="loan-recovery">
<label for="l-n">Your name</label><input id="l-n" name="name" required autocomplete="name"><label for="l-co">Company / lending entity</label><input id="l-co" name="company">
<label for="l-e">Email</label><input id="l-e" name="email" type="email" required autocomplete="email"><label for="l-p">Phone</label><input id="l-p" name="phone" type="tel" autocomplete="tel">
<label for="l-st">Property state</label><select id="l-st" name="state" required>{state_options()}</select>
<label for="l-a">Unpaid principal balance (approx.)</label><input id="l-a" name="balance" inputmode="numeric">
<label for="l-s">Loan status</label><select id="l-s" name="loan_status"><option>Past due</option><option>Matured, unpaid</option><option>In foreclosure</option><option>Post-sale deficiency</option><option>Other</option></select>
<label for="l-d">Anything else we should know?</label><textarea id="l-d" name="details" rows="3"></textarea>
<div class="check"><label><input type="checkbox" name="consent" value="yes" required><span>I confirm this is a business-purpose loan and agree to be contacted about it.</span></label></div>
<p class="err" aria-live="polite"></p><button class="btn" type="submit">Submit for review</button></form></div></section>''','lender')

legal=lambda t:t
simple('/privacy/','Privacy Policy | North Peak Recovery','How we collect and use information.','Privacy Policy',legal(f'<p>We collect the information you submit (name, contact details, property details) to research and respond to your inquiry. We do not sell your personal information. We use service providers (e.g., hosting, CRM) to operate. Phone and text contact happens only with your consent; reply STOP to opt out.</p>'))
simple('/terms/','Terms of Use | North Peak Recovery','Terms for using this website.','Terms of Use',legal(f'<p>This website provides general information, not legal advice. Using it does not create an attorney-client relationship or any agreement for services. Services are provided only under a separate signed written agreement.</p>'))
simple('/disclosures/','Disclosures | North Peak Recovery','Important disclosures.','Disclosures',legal(f'''<ul><li>North Peak Recovery is not a law firm and is not affiliated with any court, county or government agency.</li><li>You can claim surplus funds yourself without hiring anyone, often at no cost.</li><li>Legal services are provided by independent licensed attorneys.</li><li>Fees are set out in a written agreement before any filing, follow applicable state limits, and are paid only from a successful recovery.</li><li>Examples are illustrative. Results vary, and no outcome is guaranteed.</li></ul>'''))
page('/404.html','Page not found | North Peak Recovery','Page not found.','<div class="hero"><div class="wrap"><h1>We couldn’t find that page</h1><p class="lead">Let’s get you back on track.</p><a class="btn" href="/">Go home</a> <a class="btn ghost" href="/states/">State guides</a></div></div>')

# sitemap + robots
urls=['/','/how-it-works/','/what-are-surplus-funds/','/states/','/about/','/faq/','/check-my-funds/','/beware-of-scams/','/loan-recovery/','/privacy/','/terms/','/disclosures/']+[f'/states/{s["slug"]}/' for s in STATES]
open(os.path.join(ROOT,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE}{u}</loc></url>' for u in urls)+'</urlset>\n')
open(os.path.join(ROOT,'robots.txt'),'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
print('built',len(urls),'urls')
