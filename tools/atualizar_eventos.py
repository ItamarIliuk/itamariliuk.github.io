"""Gera o bloco de eventos do LABRIOT em cada site a partir de eventos.json.

Uso (na pasta itamariliuk.github.io):  python tools/atualizar_eventos.py [AAAA-MM-DD]
A data (padrão: hoje) decide o que é "Próximo" e o que é "Realizado".
O bloco fica entre <!-- eventos:inicio --> e <!-- eventos:fim -->; o CSS entre /* eventos:inicio */ e /* eventos:fim */.
Os sites dos projetos ficam em pastas irmãs desta.
"""
import datetime as dt
import html
import io
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IRMAS = os.path.dirname(AQUI)
HUB = "https://itamariliuk.github.io/#eventos"
MESES = {"pt": "jan fev mar abr mai jun jul ago set out nov dez".split(),
         "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()}

# site: (pasta, CSS externo ou None se o CSS fica no <style> da página, projeto (None = hub), seção antes da qual entra)
SITES = {
    "hub": (AQUI, "assets/site.css", None, '<section id="projetos">'),
    "dt": (os.path.join(IRMAS, "digital-twin-hands-on"), "assets/site.css", "dt", '<section id="tech">'),
    "earth2": (os.path.join(IRMAS, "earth2-rs-eventos-severos"), "assets/site.css", "earth2", '<section id="reproduzir">'),
    "igm": (os.path.join(IRMAS, "igm"), None, "igm", '<section id="tech">'),
    "icu": (os.path.join(IRMAS, "icu-guardbot-site"), None, "icu", '<section id="tech">'),
    "pomar": (os.path.join(IRMAS, "drone-pomar"), "assets/site.css", "pomar", '<section id="parceria">'),
}

CSS = """/* eventos:inicio */
.eventos{list-style:none;margin:0;padding:0;display:grid;gap:14px}
.ev{display:grid;grid-template-columns:104px 1fr;gap:22px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px}
.ev.proximo{border-left:5px solid var(--brand)}
.ev .data{display:flex;flex-direction:column;align-items:center;justify-content:center;background:color-mix(in srgb,var(--brand) 13%,transparent);border-radius:10px;padding:12px 6px;align-self:start;text-align:center}
.ev .d{font-size:36px;font-weight:700;line-height:1;color:var(--brand)}
.ev .m{font-size:12px;font-weight:600;color:var(--muted);margin-top:5px;letter-spacing:.03em}
.ev .st{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--brand);border:1px solid currentColor;border-radius:999px;padding:1px 9px;margin-bottom:8px}
.ev.realizado .st{color:var(--muted)}
.ev h3{margin:0 0 2px;font-size:20px}
.ev .local{margin:0 0 8px;color:var(--muted);font-size:14px}
.ev .resumo{margin:0 0 12px}
.ev .foto{margin:0 0 14px;max-width:520px}
.ev .foto img{width:100%;height:auto;display:block;border-radius:10px;border:1px solid var(--line)}
.ev .foto figcaption{font-size:12px;color:var(--muted);margin-top:4px}
.ev .itens{list-style:none;margin:0 0 14px;padding:0;display:grid;gap:8px}
.ev .itens li{display:grid;grid-template-columns:56px 1fr;gap:10px;font-size:15px}
.ev .itens .h{font-weight:700;font-variant-numeric:tabular-nums;color:var(--brand)}
.ev .rodape{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;font-size:14px}
.ev .proj{display:flex;flex-wrap:wrap;gap:6px}
.ev .proj a{font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;border:1px solid var(--line);text-decoration:none;color:var(--text)}
.ev .rodape>a{font-weight:600}
.eventos-todos{margin:16px 0 0;font-size:15px}
@media (max-width:600px){.ev{grid-template-columns:1fr;gap:12px;padding:18px}.ev .data{flex-direction:row;gap:8px;align-items:baseline;justify-self:start;padding:8px 14px}.ev .d{font-size:28px}.ev .itens li{grid-template-columns:1fr;gap:0}}
/* eventos:fim */"""

TXT = {
    "hub_eyebrow": {"pt": "Eventos e atividades", "en": "Events and activities"},
    "hub_h2": {"pt": "Onde estamos", "en": "Where we are"},
    "hub_sub": {"pt": "Onde o LABRIOT apresenta os seus projetos. A lista cresce a cada participação e fica como histórico.",
                "en": "Where LABRIOT presents its projects. The list grows with each event and stays as a record."},
    "proj_h2": {"pt": "Eventos", "en": "Events"},
    "proj_sub": {"pt": "Onde este projeto é apresentado.", "en": "Where this project is presented."},
    "todos": {"pt": "Todas as participações do LABRIOT →", "en": "All LABRIOT events →"},
    "proximo": {"pt": "Próximo", "en": "Upcoming"},
    "realizado": {"pt": "Realizado", "en": "Past"},
    "nav": {"pt": "Eventos", "en": "Events"},
}


def bi(d, tag="span", cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f'<{tag}{c} lang="{l}">{html.escape(d[l], quote=False)}</{tag}>' for l in ("pt", "en"))


def evento_html(e, projs, hoje):
    data = dt.date.fromisoformat(e["data"])
    st = "proximo" if data >= hoje else "realizado"
    mes = {l: f"{MESES[l][data.month - 1]} · {data.year}" for l in ("pt", "en")}
    itens = "".join(f'<li><span class="h">{i["hora"]}</span>{bi(i)}</li>' for i in e["itens"])
    lk = e.get("link")  # opcional: evento sem página pública fica sem o link
    link = f'<a href="{lk["url"]}">{bi(lk)} ↗</a>' if lk else ""
    chips = "".join(f'<a href="{projs[p]["url"]}">{html.escape(projs[p]["nome"])}</a>' for p in e["projetos"])
    ft = e.get("foto")  # opcional: {"src": URL absoluta, "w", "h", "alt": texto, "credito": {"pt","en"}}
    foto = (f'<figure class="foto"><img src="{ft["src"]}" width="{ft["w"]}" height="{ft["h"]}" loading="lazy" '
            f'alt="{html.escape(ft["alt"])}"><figcaption>{bi(ft["credito"])}</figcaption></figure>') if ft else ""
    return (f'<li class="ev {st}" id="{e["id"]}">'
            f'<div class="data"><span class="d">{data.day}</span>{bi(mes, cls="m")}</div>'
            f'<div><span class="st">{bi(TXT[st])}</span><h3>{bi(e["titulo"])}</h3>'
            f'{bi(e["local"], "p", "local")}{bi(e["resumo"], "p", "resumo")}{foto}'
            f'<ul class="itens">{itens}</ul>'
            f'<div class="rodape"><span class="proj">{chips}</span>'
            f'{link}</div></div></li>')


def secao(proj, dados, hoje):
    evs = [e for e in dados["eventos"] if proj is None or proj in e["projetos"]]
    # próximos primeiro (do mais perto ao mais longe), depois os realizados (do mais recente ao mais antigo)
    prox = sorted((e for e in evs if dt.date.fromisoformat(e["data"]) >= hoje), key=lambda e: e["data"])
    pas = sorted((e for e in evs if dt.date.fromisoformat(e["data"]) < hoje), key=lambda e: e["data"], reverse=True)
    lis = "\n    ".join(evento_html(e, dados["projetos"], hoje) for e in prox + pas)
    if proj is None:
        topo = (f'  <p class="eyebrow">{bi(TXT["hub_eyebrow"])}</p>\n  <h2>{bi(TXT["hub_h2"])}</h2>\n'
                f'  {bi(TXT["hub_sub"], "p", "sub")}\n')
        fim = ""
    else:
        topo = f'  <h2>{bi(TXT["proj_h2"])}</h2>\n  {bi(TXT["proj_sub"], "p", "sub")}\n'
        fim = f'\n  <p class="eventos-todos"><a href="{HUB}">{bi(TXT["todos"])}</a></p>'
    return (f'<!-- eventos:inicio -->\n<section id="eventos"><div class="wrap">\n{topo}'
            f'  <ul class="eventos">\n    {lis}\n  </ul>{fim}\n</div></section>\n<!-- eventos:fim -->\n\n')


def troca_css(texto):
    if "/* eventos:inicio */" in texto:
        return re.sub(r"/\* eventos:inicio \*/.*?/\* eventos:fim \*/", lambda m: CSS, texto, flags=re.S)
    return None


def main():
    hoje = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today()
    dados = json.load(io.open(os.path.join(AQUI, "eventos.json"), encoding="utf-8"))
    for nome, (pasta, css, proj, ancora) in SITES.items():
        pag = os.path.join(pasta, "index.html")
        if not os.path.exists(pag):
            print("pulado (pasta não encontrada):", nome)
            continue
        s = io.open(pag, encoding="utf-8").read()
        bloco = secao(proj, dados, hoje)
        if "<!-- eventos:inicio -->" in s:
            s = re.sub(r"<!-- eventos:inicio -->.*?<!-- eventos:fim -->\n\n", lambda m: bloco, s, flags=re.S)
        else:
            assert s.count(ancora) == 1, (nome, ancora)
            s = s.replace(ancora, bloco + ancora)
        cab, sep, resto = s.partition("</nav>")
        if 'href="#eventos"' not in cab:
            s = cab + f'  <a href="#eventos">{bi(TXT["nav"])}</a>\n    ' + sep + resto
        if css is None:
            s = troca_css(s) or s.replace("</style>", CSS + "\n</style>", 1)
        else:
            cp = os.path.join(pasta, css)
            c = io.open(cp, encoding="utf-8").read()
            c = troca_css(c) or (c.rstrip("\n") + "\n\n" + CSS + "\n")
            io.open(cp, "w", encoding="utf-8", newline="").write(c)
        io.open(pag, "w", encoding="utf-8", newline="").write(s)
        print("ok", nome)


if __name__ == "__main__":
    main()
