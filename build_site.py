#!/usr/bin/env python3
"""build_site.py - deterministic renderer for rajatbhatheja.is-a.dev.

Reads content.json (brand copy, source of truth) + posts.json (featured essays,
auto-pulled from Substack) and renders dist/index.html. No numbers or claims are
invented here - it only lays out the content it is given. OpenClaw edits the JSON
and re-runs this; it never hand-writes HTML.

Usage: python3 build_site.py   ->   dist/index.html
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")


def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return html.escape(str(s or ""), quote=True)


def _post_card(p):
    date = esc(p.get("date", ""))
    return f"""      <a class="card post" href="{esc(p.get('url'))}" target="_blank" rel="noopener">
        <div class="post-date">{date}</div>
        <h3>{esc(p.get('title'))}</h3>
        <p>{esc(p.get('blurb', ''))}</p>
        <span class="read">Read on The Data Muse &rarr;</span>
      </a>"""


def _writing_section(c, posts):
    w = c["writing"]
    if posts:
        cards = "\n".join(_post_card(p) for p in posts[:6])
        body = f'<div class="grid posts">\n{cards}\n    </div>'
    else:
        sub = c["brand"]["substack"]
        body = (f'<div class="card muse-cta">\n'
                f'      <h3>{esc(c["brand"]["substack_name"])}</h3>\n'
                f'      <p>{esc(w["intro"])}</p>\n'
                f'      <a class="btn primary" href="{esc(sub)}" target="_blank" rel="noopener">'
                f'{esc(w["cta"]["label"])} &rarr;</a>\n    </div>')
    return f"""  <section id="writing" class="section">
    <div class="wrap">
      <h2>{esc(w['title'])}</h2>
      <p class="lead">{esc(w['intro'])}</p>
      {body}
    </div>
  </section>"""


def render(c, posts):
    b = c["brand"]
    accent = b.get("accent", "#38BDF8")
    hero = c["hero"]
    about = c["about"]
    topics = c["topics"]
    connect = c["connect"]

    badges = "".join(f'<span class="badge">{esc(x)}</span>' for x in about.get("badges", []))
    about_body = "".join(f"<p>{esc(p)}</p>" for p in about.get("body", []))
    topic_cards = "\n".join(
        f'      <div class="card"><h3>{esc(t["h"])}</h3><p>{esc(t["p"])}</p></div>'
        for t in topics.get("items", []))
    connect_links = "".join(
        f'<a class="btn ghost" href="{esc(l["href"])}" target="_blank" rel="noopener">{esc(l["label"])}</a>'
        for l in connect.get("links", []))

    writing = _writing_section(c, posts)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(b['name'])} \u2014 {esc(b['role'])}</title>
<meta name="description" content="{esc(hero['sub'])}">
<meta property="og:title" content="{esc(b['name'])} \u2014 {esc(b['role'])}">
<meta property="og:description" content="{esc(hero['sub'])}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>
  :root{{ --accent:{accent}; --ink:#0f172a; --slate:#475569; --muted:#94a3b8;
          --line:#e2e8f0; --bg:#ffffff; --soft:#f8fafc; }}
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
        color:var(--ink);background:var(--bg);line-height:1.6;-webkit-font-smoothing:antialiased}}
  a{{color:inherit;text-decoration:none}}
  .wrap{{max-width:920px;margin:0 auto;padding:0 22px}}
  .section{{padding:64px 0;border-top:1px solid var(--line)}}
  h1,h2,h3{{line-height:1.2;margin:0 0 12px}}
  h2{{font-size:26px}}
  .lead{{color:var(--slate);max-width:640px;margin:0 0 28px}}
  /* nav */
  nav{{position:sticky;top:0;background:rgba(255,255,255,.86);backdrop-filter:blur(8px);
       border-bottom:1px solid var(--line);z-index:10}}
  nav .wrap{{display:flex;align-items:center;justify-content:space-between;height:60px}}
  nav .name{{font-weight:700}}
  nav .links a{{color:var(--slate);margin-left:20px;font-size:15px}}
  nav .links a:hover{{color:var(--ink)}}
  /* hero */
  .hero{{padding:96px 0 72px}}
  .kicker{{color:var(--accent);font-weight:700;letter-spacing:.4px;font-size:14px;text-transform:uppercase}}
  .hero h1{{font-size:44px;letter-spacing:-.5px;margin-top:10px}}
  .hero p{{color:var(--slate);font-size:19px;max-width:640px}}
  .cta-row{{margin-top:28px;display:flex;gap:12px;flex-wrap:wrap}}
  .btn{{display:inline-block;padding:11px 18px;border-radius:10px;font-weight:600;font-size:15px;
        border:1px solid var(--line);transition:transform .05s ease, box-shadow .2s ease}}
  .btn:hover{{transform:translateY(-1px)}}
  .btn.primary{{background:var(--accent);border-color:var(--accent);color:#04212e;
                box-shadow:0 6px 20px rgba(56,189,248,.35)}}
  .btn.ghost:hover{{border-color:var(--accent);color:var(--accent)}}
  .badges{{margin-top:22px;display:flex;gap:8px;flex-wrap:wrap}}
  .badge{{font-size:13px;color:var(--slate);background:var(--soft);border:1px solid var(--line);
          padding:5px 11px;border-radius:999px}}
  /* cards */
  .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
  .card{{background:var(--soft);border:1px solid var(--line);border-radius:14px;padding:20px}}
  .card h3{{font-size:18px}}
  .card p{{color:var(--slate);margin:0;font-size:15px}}
  .post .post-date{{color:var(--muted);font-size:13px;margin-bottom:6px}}
  .post .read{{display:inline-block;margin-top:12px;color:var(--accent);font-weight:600;font-size:14px}}
  .post:hover{{border-color:var(--accent);box-shadow:0 8px 24px rgba(15,23,42,.06)}}
  .muse-cta{{text-align:left}}
  .muse-cta .btn{{margin-top:14px}}
  .connect .cta-row{{margin-top:8px}}
  footer{{padding:40px 0;border-top:1px solid var(--line);color:var(--muted);font-size:14px}}
  footer .wrap{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}}
  @media(max-width:640px){{ .hero h1{{font-size:34px}} .grid{{grid-template-columns:1fr}} h2{{font-size:22px}} }}
</style>
</head>
<body>
<nav><div class="wrap">
  <span class="name">{esc(b['name'])}</span>
  <div class="links">
    <a href="#about">About</a>
    <a href="#writing">Writing</a>
    <a href="#connect">Connect</a>
  </div>
</div></nav>

<header class="hero"><div class="wrap">
  <div class="kicker">{esc(hero['kicker'])}</div>
  <h1>{esc(hero['headline'])}</h1>
  <p>{esc(hero['sub'])}</p>
  <div class="cta-row">
    <a class="btn primary" href="{esc(hero['primary_cta']['href'])}" target="_blank" rel="noopener">{esc(hero['primary_cta']['label'])}</a>
    <a class="btn ghost" href="{esc(hero['secondary_cta']['href'])}" target="_blank" rel="noopener">{esc(hero['secondary_cta']['label'])}</a>
  </div>
  <div class="badges">{badges}</div>
</div></header>

<section id="about" class="section"><div class="wrap">
  <h2>{esc(about['title'])}</h2>
  {about_body}
</div></section>

{writing}

<section id="topics" class="section"><div class="wrap">
  <h2>{esc(topics['title'])}</h2>
  <div class="grid">
{topic_cards}
  </div>
</div></section>

<section id="connect" class="section connect"><div class="wrap">
  <h2>{esc(connect['title'])}</h2>
  <p class="lead">{esc(connect['body'])}</p>
  <div class="cta-row">{connect_links}</div>
</div></section>

<footer><div class="wrap">
  <span>&copy; 2026 {esc(b['name'])}</span>
  <span>{esc(b['footer_handle'])} &middot; thedatamuse.substack.com</span>
</div></footer>
</body>
</html>
"""


def main():
    c = _load("content.json")
    try:
        posts = (_load("posts.json") or {}).get("posts", [])
    except Exception:
        posts = []
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(c, posts))
    print(f"built {out} ({len(posts)} featured post(s))")


if __name__ == "__main__":
    main()
