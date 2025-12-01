# PDF Extractor Local

Ferramenta interna para comparar diferentes bibliotecas de extração de conteúdo (texto, tabelas, figuras) em PDFs acadêmicos. Ela automatiza a execução das ferramentas, salva todos os artefatos e gera relatórios comparativos.

## Visão geral

- `src/pdf_extractor/cli.py`: CLI com três comandos principais (`extract`, `demo`, `evaluate`).
- `src/pdf_extractor/pipelines/manager.py`: orquestra os adaptadores e gerencia cache/persistência.
- `src/pdf_extractor/pipelines/adapters/`: cada adaptador encapsula uma ferramenta (Docling, MarkItDown, PyMuPDF, pdfplumber, Nougat, Marker, Grobid, Chandra).
- `artifacts/`: resultados organizados por PDF e ferramenta.
- `docs/`: materiais derivados, como relatórios e guias.

> **Importante:** O projeto deve ser executado exclusivamente via Docker Compose. As instruções abaixo assumem que você utilizará os serviços `app` e (opcionalmente) `grobid` definidos em `docker-compose.yml`.

## Executando via Docker

Ideal quando:
- Você está em macOS x86_64 e depende de Docling/Nougat/Marker.
- Precisa garantir versões consistentes (imagem inclui todos os modelos e CLIs).

Passos:
```bash
# Construir imagem (baixa modelos do Nougat e instala marker_single)
docker compose build app

# Subir serviços (app permanece ativo como shell e o Grobid fica disponível)
docker compose up -d app grobid

# Rodar extração completa dentro do contêiner já em execução
docker compose exec app uv run pdf-extractor extract \
  --pdf-dir /app/pdfs-reais \
  --artifact-dir /app/artifacts

# Demo isolada (Marker)
docker compose exec app uv run pdf-extractor demo \
  --tool marker \
  --pdf "/app/pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
  --artifact-dir /app/artifacts/demo-marker

# Demo isolada (Chandra)
docker compose exec app uv run pdf-extractor demo \
  --tool chandra \
  --pdf "/app/pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
  --artifact-dir /app/artifacts/demo-chandra

# Quando terminar, pare os serviços (o build só será necessário novamente se mudar o código)
docker compose stop app grobid
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
| Chandra | OCR multimodal preservando layout | Instale dentro do contêiner com `docker compose exec app uv pip install "git+https://github.com/datalab-to/chandra.git"` e configure `CHANDRA_*` conforme necessário |

Você escolhe quais rodar passando `--tools tool_a,tool_b`.

## Instalação do Chandra dentro do contêiner

O `chandra-ocr` não é instalado por padrão. Para utilizá-lo, entre no contêiner `app` e instale o pacote diretamente do GitHub:

```bash
docker compose exec app uv pip install "git+https://github.com/datalab-to/chandra.git"
```

O binário ficará disponível em `/root/.local/bin/chandra`. Ao executar comandos que usam o adaptador, informe o caminho explícito (ou defina um `.env` com `CHANDRA_CLI=/root/.local/bin/chandra`):

```bash
docker compose exec app env CHANDRA_CLI=/root/.local/bin/chandra \
  uv run pdf-extractor demo \
    --tool chandra \
    --pdf "/app/pdfs-reais/SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf" \
    --artifact-dir /app/artifacts/demo-chandra
```

Variáveis de ambiente úteis dentro do contêiner:

- `CHANDRA_CLI` (default: `chandra`): caminho do CLI.
- `CHANDRA_USE_UV_RUN` (default: `1`): mantém o uso de `uv run`.
- `CHANDRA_EXTRA_ARGS`: parâmetros adicionais para o CLI (ex.: `--max-pages 2`).
- `CHANDRA_TIMEOUT`: timeout em segundos.
- `CHANDRA_PRIMARY_MARKDOWN`: nome preferido do `.md` quando o CLI gera vários arquivos.

Os resultados do CLI (`attention.md`, `attention_metadata.json`, `images/`) são normalizados automaticamente pelo adaptador.

## Resolução de problemas comuns

- **Marker/Nougat não encontrados**: garanta que o contêiner `app` foi construído após as últimas alterações (`docker compose build app`) e que você está executando via `docker compose exec app ...`.
- **Chandra não encontrado**: instale o pacote dentro do contêiner (`docker compose exec app uv pip install "git+https://github.com/datalab-to/chandra.git"`) e informe `CHANDRA_CLI=/root/.local/bin/chandra` ao executar.
- **Grobid falha (`nodename nor servname provided`)**: suba o serviço (`docker compose up grobid`) e/ou configure `GROBID_URL=http://localhost:8070`.
- **Execuções repetidas não atualizam artefatos**: use `--overwrite` no comando `extract` para forçar reprocessamento.

## Próximos passos

- Integrar os artefatos (principalmente os de Docling) em pipelines de RAG.
- Ajustar/adicionar adaptadores para novas ferramentas.
- Automatizar benchmarks (CI) usando o comando `extract` e armazenar `comparativo.json`.

Caso tenha dúvidas ou precise rodar apenas uma parte do pipeline, abra um chat ou consulte o script `src/pdf_extractor/cli.py` para ver todas as opções disponíveis.
