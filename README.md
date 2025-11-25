# PDF Extractor Local

Ferramenta interna para comparar diferentes bibliotecas de extração de conteúdo (texto, tabelas, figuras) em PDFs acadêmicos. Ela automatiza a execução das ferramentas, salva todos os artefatos e gera relatórios comparativos.

## Visão geral

- `src/pdf_extractor/cli.py`: CLI com três comandos principais (`extract`, `demo`, `evaluate`).
- `src/pdf_extractor/pipelines/manager.py`: orquestra os adaptadores e gerencia cache/persistência.
- `src/pdf_extractor/pipelines/adapters/`: cada adaptador encapsula uma ferramenta (Docling, MarkItDown, PyMuPDF, pdfplumber, Nougat, Marker, Grobid).
- `artifacts/`: resultados organizados por PDF e ferramenta.
- `docs/`: materiais derivados, como relatórios e guias.

## Pré-requisitos

| Onde rodar? | Ferramentas necessárias |
|-------------|-------------------------|
| Ambiente local | [UV](https://github.com/astral-sh/uv) ≥ 0.4 e Python 3.11 |
| Contêiner | Docker + Docker Compose |

Os PDFs já estão em `pdfs-reais/`. Se quiser testar outros arquivos basta colocá-los nessa pasta ou apontar `--pdf-dir` para outro diretório.

## Fluxo recomendado

1. **Instalar dependências**
   ```bash
   uv sync --dev
   ```
   > Em macOS x86_64 algumas bibliotecas pesadas (Docling/Nougat/Marker) não possuem wheels. Use Docker nesses casos.

2. **Extrair conteúdo**
   - Todos os PDFs + todas as ferramentas:
     ```bash
     uv run pdf-extractor extract --pdf-dir pdfs-reais --artifact-dir artifacts
     ```
   - Subset de ferramentas:
     ```bash
     uv run pdf-extractor extract \
       --pdf-dir pdfs-reais \
       --artifact-dir artifacts \
       --tools docling,pymupdf
     ```
   - Somente uma ferramenta (ex.: Marker):
     ```bash
     uv run pdf-extractor extract --tools marker
     ```

3. **Demo rápida**
   ```bash
   uv run pdf-extractor demo \
     --tool ferramenta-para-teste \
     --pdf "pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
     --artifact-dir artifacts/demo-ferramenta-escolhida
   ```
   Gera um markdown consolidado em `artifacts/demo-ferramenta-escolhida/<PDF>-docling.md`.

4. **Gerar relatório comparativo**
   ```bash
   uv run pdf-extractor evaluate \
     --report-path artifacts/comparativo.json \
     --output-markdown docs/comparativo.md
   ```
   Usa o `comparativo.json` mais recente para produzir uma tabela com tempos, % de texto e observações.

## Executando via Docker

Ideal quando:
- Você está em macOS x86_64 e depende de Docling/Nougat/Marker.
- Precisa garantir versões consistentes (imagem inclui todos os modelos e CLIs).

Passos:
```bash
# Construir imagem (baixa modelos do Nougat e instala marker_single)
docker compose build app

# Rodar extração completa dentro do contêiner
docker compose run --rm app uv run pdf-extractor extract \
  --pdf-dir /app/pdfs-reais \
  --artifact-dir /app/artifacts

# Demo isolada (ex.: Marker)
docker compose run --rm app uv run pdf-extractor demo \
  --tool marker \
  --pdf "/app/pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
  --artifact-dir /app/artifacts/demo-marker
```

Serviços do `docker-compose.yml`:
- `app`: container principal com UV, PyTorch e todas as dependências.
- `grobid`: opcional. Suba com `docker compose up grobid` se quiser usar o adaptador Grobid.

Volumes mapeados:
- `./pdfs-reais` → `/app/pdfs-reais`
- `./artifacts` → `/app/artifacts`
- `./docs` → `/app/docs`

## Estrutura de artefatos

Para cada PDF/ferramenta:
- `text.md`: texto extraído (geralmente Markdown).
- `tables.json`: tabelas normalizadas (lista de `rows`, `caption`, `page`).
- `figures.json`: figuras/legendas.
- `summary.json`: métricas (tempo, nº de caracteres, nº de tabelas/figuras, notas).

Consolidação global:
- `artifacts/comparativo.json`: registro de todos os runs. É a entrada do comando `evaluate`.

## Ferramentas suportadas

| Ferramenta | Função principal | Observações |
|------------|------------------|-------------|
| Docling | Conversão completa (Markdown + tabelas/figuras) | Requer PyTorch ≥ 2.3 |
| MarkItDown | Conversão rápida para Markdown | Ótima para textos limpos |
| PyMuPDF | Extração textual+nativa | Identifica figuras por imagem |
| pdfplumber | Texto + tabelas (OCR leve) | Dependência mínima |
| Nougat | OCR científico → Markdown | CLI externo (`nougat`) |
| Marker | Extração multimodal (Surya) | Idealmente com GPU |
| Grobid | TEI + estrutura acadêmica | Precisa do serviço `grobid` ativo |

Você escolhe quais rodar passando `--tools tool_a,tool_b`.

## Resolução de problemas comuns

- **Marker/Nougat não encontrados**: confirme se está rodando dentro do contêiner ou em máquina com PyTorch compatível. Fora do Docker, `marker_single` e `nougat` precisam estar no PATH.
- **Grobid falha (`nodename nor servname provided`)**: suba o serviço (`docker compose up grobid`) e/ou configure `GROBID_URL=http://localhost:8070`.
- **Execuções repetidas não atualizam artefatos**: use `--overwrite` no comando `extract` para forçar reprocessamento.
- **Mac x86_64 travando no `uv sync`**: instale apenas dependências leves localmente (`uv sync --no-dev`) e processe via Docker.

## Próximos passos

- Integrar os artefatos (principalmente os de Docling) em pipelines de RAG.
- Ajustar/adicionar adaptadores para novas ferramentas.
- Automatizar benchmarks (CI) usando o comando `extract` e armazenar `comparativo.json`.

Caso tenha dúvidas ou precise rodar apenas uma parte do pipeline, abra um chat ou consulte o script `src/pdf_extractor/cli.py` para ver todas as opções disponíveis.
