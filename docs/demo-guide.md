# Demo rápida para o time

## Pré-requisitos

- UV instalado localmente (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- Docker (opcional) caso queira incluir o Grobid automaticamente.

## Passo a passo local

```bash
uv sync --dev
uv run pdf-extractor demo \
  --tool docling \
  --pdf "pdfs-reais/DM - Diet and exercise in the prevention and treatment of type 2 diabetes mellitus.pdf" \
  --artifact-dir artifacts/demo
```

Saída esperada:

- `artifacts/demo/DM - ...-docling.md` com o Markdown resumido (para compartilhar rapidamente).
- `artifacts/demo/DM - .../docling/text.md|tables.json|figures.json|summary.json` seguindo o padrão dos demais pipelines.

## Mostrando outras ferramentas

```bash
uv run pdf-extractor demo --tool pdfplumber --pdf "pdfs-reais/MOVIMENTO - The associations between sedentary behavior and risk of depression.pdf"
uv run pdf-extractor demo --tool marker \
  --pdf "pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
  --artifact-dir artifacts/demo-marker
```

> Dica: use `--artifact-dir artifacts/demo-<nome>` para manter resultados separados por rodada de validação.

## Via Docker Compose

```bash
docker compose build app  # garante a imagem atualizada
docker compose run --rm app uv run pdf-extractor demo \
  --tool marker \
  --pdf "/app/pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
  --artifact-dir /app/artifacts/demo-marker
```

- As saídas ficarão em `./artifacts/demo-marker/...` no host.
- Após a demo, execute `uv run pdf-extractor evaluate ...` ou abra `docs/comparativo.md` para revisar recomendações atualizadas.

