# Proteção de chuva para câmera lâmpada E27

Chapéu impresso em 3D que protege da chuva uma câmera lâmpada (Durawell, rosca E27) pendurada num bocal de sobrepor, sem tampar a lente.

## Fixação

Montagem, de cima para baixo: **chapa da haste → chapéu → bocal → câmera**.

- O disco plano do chapéu (3 mm) fica entre a chapa e o bocal, preso pelos mesmos 2 parafusos do bocal (furos de 4,5 mm a 53 mm entre centros). Use parafusos uns 3 mm mais compridos.
- O fio sai pelo furo central de 12 mm.
- Passe silicone neutro entre a chapa e o disco e em volta do fio, para a água não escorrer até os bornes do bocal.

## Estilos

Todos ficam em `desenhos/estilos/`, em `.stl` e `.3mf`. Escolha o seu favorito. A imagem `comparacao.png` mostra todos lado a lado.

| Estilo | Tamanho | PETG |
|---|---|---|
| `curto` | Ø130 × 33 mm | ~60 g |
| `sino_curto` | Ø130 × 34 mm | ~60 g |
| `pagode_curto` | Ø128 × 38 mm | ~67 g |
| `facetado_curto` | Ø131 × 33 mm | ~56 g |
| `saia` | Ø110 × 78 mm | ~100 g |
| `sino` | Ø120 × 78 mm | ~96 g |
| `pagode` | Ø120 × 78 mm | ~110 g |
| `facetado` | Ø116 × 78 mm | ~94 g |

- **Curtos**: aba larga terminando perto da boca do bocal. Protegem o bocal e a parte de cima da câmera.
- **Com saia**: descem pelo corpo parado da câmera e terminam 10 mm acima da linha preta, onde começa a cabeça que gira. Protegem mais com chuva de lado.

`corte_curto.png` e `corte_saia.png` mostram o corte montado no bocal e na câmera.

## Impressão

- Disco plano na mesa e sem suporte. Nenhum trecho passa de 45°, e o script confere isso.
- PETG branco ou de cor clara, com 3 ou 4 perímetros. Para durar mais no sol forte, ASA é melhor.

## Gerar de novo

```bash
uv venv .venv && uv pip install --python .venv/bin/python manifold3d trimesh numpy matplotlib pillow shapely networkx lxml
.venv/bin/python estilos.py
```

As medidas ficam no topo do `chapeu.py`. O diâmetro do bocal (`BOCAL_D = 75`) foi estimado pela foto: confira com o paquímetro. Os perfis dos estilos ficam no `estilos.py`, em funções `perfil_*`.
