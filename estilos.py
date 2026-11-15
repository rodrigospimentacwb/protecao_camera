"""Variações de estilo do chapéu (mesma fixação e medidas do chapeu.py).

Cada estilo é um perfil (r, z) da face de FORA. A parede é tirada por offset (shapely),
então o mesmo código serve para qualquer curva. z = 0 é a face que encosta na chapa;
z cresce para baixo no uso (na impressão, para cima: disco na mesa).

Regra de impressão sem suporte: nenhum trecho do perfil pode passar de 45° (|dr/dz| <= 1).

    .venv/bin/python estilos.py
Gera em desenhos/estilos/: <estilo>.stl, <estilo>.3mf e comparacao.png
"""
import os
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from manifold3d import Manifold, CrossSection

from chapeu import (BOCAL_D, BOCAL_H, BOCAL_FOLGA, FURO_ENTRE, FURO_D, FIO_D, DISCO_T,
                    PAREDE, CAM_ATE_LINHA, FIM_ACIMA_LINHA, CAM_D, to_trimesh)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desenhos", "estilos")
H = DISCO_T + BOCAL_H + CAM_ATE_LINHA - FIM_ACIMA_LINHA      # 78: fim da saia
R_BOCAL = BOCAL_D / 2 + BOCAL_FOLGA                           # 39: folga do bocal
R_CAM = CAM_D / 2 + 4                                         # 39: folga do corpo da câmera
R0 = R_BOCAL + PAREDE * np.sqrt(2) - DISCO_T + 0.3                # início da aba na mesa (45°)


def spline(pts, n=24):
    """Catmull-Rom passando pelos pontos (curva suave)."""
    p = np.array(pts, float)
    p = np.vstack([p[0] * 2 - p[1], p, p[-1] * 2 - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-2])
    return [tuple(q) for q in out]


# ---------------- ESTILOS (perfil de fora, de z = 0 até z = H) ----------------
def perfil_sino():
    """Tulipa: ombro arredondado, cintura leve e barra que abre no fim."""
    return [(R0, 0)] + spline([(R0 + 6, 6), (48.5, 10.5), (51, 20), (50.5, 38), (49, 52),
                                (52, 66), (60, H)])


def perfil_pagode():
    """Três beirais, como telhado de pagode (o chapéu chinês em camadas). Cada ponta pinga."""
    return [(R0, 0), (52, 0 + 52 - R0),          # 1º beiral a 45°
            (46, 19), (46, 26),                  # volta para dentro e desce
            (56, 36), (49, 43), (49, 52),        # 2º beiral
            (60, 63), (53, 70), (53, H)]         # 3º beiral e barra


def perfil_facetado():
    """Perfil simples; o estilo vem das 8 faces torcidas (ver FACES/TORCAO)."""
    return [(R0, 0)] + spline([(R0 + 6, 6), (49, 12.5), (52, 26), (52, 56), (56, H)])


# ---- versões curtas: aba larga (~Ø130) terminando perto da boca do bocal, como a 1ª ideia ----
def perfil_liso_curto():
    """O chapéu curto original: aba reta a 45° e pingadeira de 6 mm."""
    return [(R0, 0), (65, 65 - R0), (65, 65 - R0 + 6)]


def perfil_sino_curto():
    """Guarda-chuva: ombro a 45° que vai abrindo em curva até a borda."""
    return [(R0, 0)] + spline([(R0 + 6, 6), (50, 11), (56, 17.5), (61, 24), (64, 30), (65, 34)])


def perfil_pagode_curto():
    """Dois beirais, chapéu chinês em camadas."""
    return [(R0, 0), (52, 52 - R0),              # 1º beiral a 45°
            (47, 52 - R0 + 5.1), (47, 19),       # volta para dentro
            (64, 36), (62, 38)]                  # 2º beiral (pingadeira em ponta)


def perfil_facetado_curto():
    return [(R0, 0)] + spline([(R0 + 6, 6), (51, 13), (56, 21), (59.5, 29), (60.5, 33)])


ESTILOS = {
    # nome: (perfil, faces (0 = redondo), torção total em graus)
    "sino": (perfil_sino, 0, 0),
    "pagode": (perfil_pagode, 0, 0),
    "facetado": (perfil_facetado, 8, 40),
    "liso_curto": (perfil_liso_curto, 0, 0),
    "sino_curto": (perfil_sino_curto, 0, 0),
    "pagode_curto": (perfil_pagode_curto, 0, 0),
    "facetado_curto": (perfil_facetado_curto, 8, 25),
}


# ---------------- GEOMETRIA ----------------
def secao(perfil, escala=1.0, conferir=True):
    c = [(r * escala, z) for r, z in perfil]
    rN, H = c[-1]                                # cada estilo tem a sua altura
    meio = [(0, 0)] + c + [(rN, H + 10), (0, H + 10)]
    cheio = unary_union([Polygon(meio), Polygon([(-r, z) for r, z in meio])])
    oco = cheio.buffer(-PAREDE, join_style=2, mitre_limit=3).intersection(box(-500, DISCO_T, 500, H + 20))
    casca = cheio.intersection(box(0, 0, 500, H)).difference(oco)
    if not conferir:
        return casca
    # conferências de encaixe e de impressão (no perfil real; com faces, vale para as faces planas)
    assert oco.contains(box(-R_BOCAL, DISCO_T + 0.01, R_BOCAL, DISCO_T + BOCAL_H)), "aba encosta no bocal"
    assert oco.contains(box(-R_CAM, DISCO_T + BOCAL_H, R_CAM, H)), "saia encosta na câmera"
    for (r1, z1), (r2, z2) in zip(c[1:], c[2:]):
        if z2 > z1:
            assert abs(r2 - r1) <= (z2 - z1) * 1.02 + 1e-6, f"trecho passa de 45°: {(r1, z1)} -> {(r2, z2)}"
    return casca


def para_crosssection(geom):
    polys = getattr(geom, "geoms", [geom])
    contornos = []
    for p in polys:
        ext = list(p.exterior.coords)[:-1]
        if Polygon(ext).exterior.is_ccw is False:
            ext = ext[::-1]
        contornos.append(ext)
        for h in p.interiors:
            hh = list(h.coords)[:-1]
            if Polygon(hh).exterior.is_ccw:
                hh = hh[::-1]
            contornos.append(hh)
    return CrossSection(contornos)


def chapeu_estilo(nome):
    perfil, faces, torcao = ESTILOS[nome]
    pts = perfil()
    # com faces, o perfil vira o raio dos cantos: escala para as faces planas manterem a folga
    escala = 1 / np.cos(np.pi / faces) if faces else 1.0
    secao(pts)  # confere folgas e 45°
    corpo = para_crosssection(secao(pts, escala, conferir=False)).revolve(faces or 180)
    if faces:
        corpo = corpo.rotate([0, 0, 180 / faces])
        if torcao:
            corpo = corpo.refine(6)

            def torce(v):
                a = np.radians(torcao) * v[2] / pts[-1][1]
                c, s = np.cos(a), np.sin(a)
                return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])
            corpo = corpo.warp(torce)
    furo = Manifold.cylinder(DISCO_T * 3, FURO_D / 2, FURO_D / 2, 48).translate([0, 0, -DISCO_T])
    for x in (-FURO_ENTRE / 2, FURO_ENTRE / 2):
        corpo = corpo - furo.translate([x, 0, 0])
    corpo = corpo - Manifold.cylinder(DISCO_T * 3, FIO_D / 2, FIO_D / 2, 64).translate([0, 0, -DISCO_T])
    return corpo


# ---------------- PRÉVIA ----------------
def desenha(ax, tm, titulo):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    v = tm.vertices.copy()
    v[:, 2] = -v[:, 2]                                   # posição de uso
    t = trimesh.Trimesh(v, tm.faces[:, ::-1], process=False)
    luz = np.array([-0.5, -0.7, 0.5]); luz /= np.linalg.norm(luz)
    sh = 0.30 + 0.70 * np.clip(t.face_normals @ luz, 0, 1)
    cor = np.c_[np.outer(sh, [0.93, 0.93, 0.90]), np.ones(len(sh))]
    ax.add_collection3d(Poly3DCollection(v[t.faces], facecolors=cor, edgecolor="none"))
    ax.set_xlim(-60, 60); ax.set_ylim(-60, 60); ax.set_zlim(-95, 25)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=18, azim=-60)
    ax.axis("off")
    ax.set_title(titulo, fontsize=12)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(OUT, exist_ok=True)
    from chapeu import chapeu
    pecas = {"v1 (saia)": to_trimesh(chapeu("saia"))}
    for nome in ESTILOS:
        tm = to_trimesh(chapeu_estilo(nome))
        assert tm.is_watertight, nome
        tm.export(os.path.join(OUT, f"{nome}.stl"))
        tm.export(os.path.join(OUT, f"{nome}.3mf"))
        pecas[nome] = tm
        ext = np.ptp(tm.vertices, axis=0)
        print(f"{nome:9s} Ø{max(ext[:2]):.0f} x {ext[2]:.0f} mm, ~{tm.volume / 1000 * 1.27:.0f} g")

    fig = plt.figure(figsize=(18, 10), facecolor="#2b2f33")
    for i, (nome, tm) in enumerate(pecas.items()):
        ax = fig.add_subplot(2, 4, i + 1, projection="3d", facecolor="#2b2f33")
        desenha(ax, tm, nome)
        ax.title.set_color("white")
    fig.savefig(os.path.join(OUT, "comparacao.png"), dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
