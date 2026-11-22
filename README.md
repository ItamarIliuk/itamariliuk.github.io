# Projetos do LABRIOT

Public page: https://itamariliuk.github.io/

Index of the open project pages of LABRIOT (Laboratório de Robótica e IoT), UTFPR Ponta Grossa, Brazil, a member of
the NVIDIA Inception program:

- [ICU-GuardBot](https://itamariliuk.github.io/icu-guardbot/) — bedside robot that helps ICU nurses notice early signs of sepsis
- [Industrial Gauge Monitor (IGM)](https://itamariliuk.github.io/igm/) — reads analog pressure gauges by camera with NVIDIA Cosmos
- [Digital Twin Hands-on](https://itamariliuk.github.io/digital-twin-hands-on/) — UR10 palletizing digital twin and workshop materials
- [Earth-2 RS](https://itamariliuk.github.io/earth2-rs-eventos-severos/) — FourCastNet 3 hindcasts of severe weather in Rio Grande do Sul

This repository holds only the static page (`index.html` and `assets/`). Product names are trademarks of their owners;
these projects are not endorsed by NVIDIA or Universal Robots.

## Eventos

A seção "Onde estamos" desta página e a seção "Eventos" das páginas dos projetos saem de `eventos.json`. Para registrar uma participação, acrescente o evento ao arquivo e rode, com os repositórios dos projetos clonados em pastas irmãs:

```
python tools/atualizar_eventos.py
```

A data do dia decide o que aparece como "Próximo" e o que vira "Realizado"; rode de novo depois de cada evento e publique os sites que mudaram.
