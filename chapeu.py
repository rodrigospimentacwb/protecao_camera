"""Chapéu de chuva para a câmera lâmpada Durawell (E27) pendurada no bocal de sobrepor.

Montagem (de cima para baixo): chapa da haste -> CHAPÉU -> bocal -> câmera.
O disco plano do chapéu fica preso entre a chapa e o bocal pelos mesmos 2 parafusos do bocal.
A aba sai a 45° por fora do bocal e vira uma saia vertical que desce pelo corpo parado da
câmera e termina acima da linha preta (cabeça que gira), então não entra na imagem nem
atrapalha o giro. A borda de baixo da saia é a pingadeira.

Impressão: disco plano na mesa (face que encosta na chapa para baixo), aba crescendo para
cima e para fora a 45° -> sem suporte. PETG branco, 3-4 perímetros.

Todas as medidas em mm. Ajuste os PARÂMETROS e rode:
    .venv/bin/python chapeu.py
Gera em desenhos/estilos/: curto.stl/.3mf, saia.stl/.3mf e corte_curto.png / corte_saia.png.
(O estilos.py gera estes e todos os outros estilos de uma vez.)
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# ---------------- PARÂMETROS ----------------
BOCAL_D = 75.0          # diâmetro da base do bocal (= chapa da haste)  CONFERIR no visor
BOCAL_H = 20.0          # altura do bocal
BOCAL_FOLGA = 1.5       # folga radial entre o bocal e o começo da aba
FURO_ENTRE = 53.0       # distância entre centros dos furos do bocal
FURO_D = 4.5            # furo de passagem (furo do bocal = 4 mm)
FIO_D = 12.0            # furo central para o fio (sai por cima, entre os parafusos)

DISCO_T = 3.0           # espessura do disco preso entre chapa e bocal
PAREDE = 2.4            # espessura da aba (medida perpendicular à superfície)
ANGULO = 45.0           # inclinação da aba em relação à horizontal (45 = imprime sem suporte)

# Dois modelos:
#   "curto": aba larga Ø130 a 45° e pingadeira de 6 mm (altura 32,6 mm)
#   "saia":  aba Ø110 e saia vertical descendo pelo corpo parado da câmera
ABA_D = {"curto": 130.0, "saia": 110.0}   # diâmetro externo da aba
PINGADEIRA = 6.0        # (curto) altura da pingadeira vertical na borda

# A saia vertical desce pelo corpo parado da câmera e termina acima da cabeça que gira.
CAM_ATE_LINHA = 65.0    # do fim da rosca (boca do bocal) até a linha preta (início da cabeça)
FIM_ACIMA_LINHA = 10.0  # a saia termina esta distância acima da linha preta

# Só para a prévia (silhueta aproximada da câmera)
CAM_D = 70.0
SEG = 180

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desenhos", "estilos")


def perfil(modelo):
    """Meia-seção (r, z) na posição de impressão: z = 0 é a face que encosta na chapa."""
    aba_d = ABA_D[modelo]
    t, w = DISCO_T, PAREDE
    tan = np.tan(np.radians(ANGULO))
    wh = w / np.sin(np.radians(ANGULO))      # espessura medida na horizontal
    r0 = BOCAL_D / 2 + BOCAL_FOLGA           # onde a aba começa (por dentro)
    rb = aba_d / 2 - w                       # raio interno da pingadeira
    zt = t + (rb - r0) * tan                 # altura da aba (por dentro) na borda
    if modelo == "curto":
        z_fim = zt + PINGADEIRA
    else:
        z_fim = t + BOCAL_H + CAM_ATE_LINHA - FIM_ACIMA_LINHA   # fim da saia, medido da chapa
        assert z_fim > zt + 2, "saia curta demais: aumente CAM_ATE_LINHA ou diminua ABA_D"
    r_out0 = r0 + wh - t / tan               # face de fora da aba na mesa
    z_out_b = (aba_d / 2 - r_out0) * tan     # face de fora encontrando a pingadeira
    pts = [
        (FIO_D / 2, 0), (r_out0, 0),
        (aba_d / 2, z_out_b), (aba_d / 2, z_fim),
        (rb, z_fim), (rb, zt),
        (r0, t), (FIO_D / 2, t),
    ]
    return pts, z_fim


def chapeu(modelo):
    pts, _ = perfil(modelo)
    corpo = CrossSection([pts]).revolve(SEG)
    furo = Manifold.cylinder(DISCO_T * 3, FURO_D / 2, FURO_D / 2, 48).translate([0, 0, -DISCO_T])
    for x in (-FURO_ENTRE / 2, FURO_ENTRE / 2):
        corpo = corpo - furo.translate([x, 0, 0])
    return corpo


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=np.array(mesh.tri_verts))


def previa_corte(path, modelo):
    """Corte lateral montado (posição de uso): chapa em cima, câmera pendurada embaixo."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle

    pts, altura = perfil(modelo)
    fig, ax = plt.subplots(figsize=(8, 7))
    for s in (1, -1):
        uso = [(s * r, -z) for r, z in pts]             # vira: z para baixo
        ax.add_patch(Polygon(uso, closed=True, fc="#2f6f6a", ec="k", lw=0.6))
    # chapa da haste
    ax.add_patch(Rectangle((-BOCAL_D / 2, 0), BOCAL_D, 4, fc="#999", ec="k", lw=0.5))
    # bocal
    ax.add_patch(Rectangle((-BOCAL_D / 2, -DISCO_T - BOCAL_H), BOCAL_D, BOCAL_H, fc="#ddd", ec="k", lw=0.5))
    # câmera (silhueta aproximada)
    z0 = -DISCO_T - BOCAL_H
    rc = CAM_D / 2
    cam = [(-14, z0), (14, z0), (rc, z0 - 30), (rc, z0 - CAM_ATE_LINHA - 50),
           (rc * 0.7, z0 - CAM_ATE_LINHA - 62), (-rc * 0.7, z0 - CAM_ATE_LINHA - 62),
           (-rc, z0 - CAM_ATE_LINHA - 50), (-rc, z0 - 30)]
    ax.add_patch(Polygon(cam, closed=True, fc="#f4f4f4", ec="#555", lw=0.8, ls="--"))
    ax.plot([-rc, rc], [z0 - CAM_ATE_LINHA] * 2, color="k", lw=1.5)
    # parafusos
    for x in (-FURO_ENTRE / 2, FURO_ENTRE / 2):
        ax.plot([x, x], [3, -DISCO_T - 6], color="#b33", lw=2)
    ax.set_aspect("equal")
    ax.set_xlim(-80, 80)
    ax.set_ylim(z0 - CAM_ATE_LINHA - 75, 15)
    ax.set_title(f"Chapéu {modelo} Ø{ABA_D[modelo]:.0f}, altura {altura:.1f} mm (corte, posição de uso)")
    ax.grid(alpha=0.3)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for modelo in ABA_D:
        tm = to_trimesh(chapeu(modelo))
        assert tm.is_watertight, "malha não fechada"
        tm.export(os.path.join(OUT, f"{modelo}.stl"))
        tm.export(os.path.join(OUT, f"{modelo}.3mf"))
        previa_corte(os.path.join(OUT, f"corte_{modelo}.png"), modelo)
        print(f"{modelo:6s} ~{tm.volume / 1000 * 1.27:.0f} g PETG, tamanho {np.ptp(tm.vertices, axis=0).round(1)} mm")
