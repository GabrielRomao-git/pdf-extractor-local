# Comparativo de Ferramentas
_Gerado em 2025-11-22T23:59:35.931856+00:00_

## Recomendação
- 1ª escolha: **docling**
- Fallbacks: markitdown, pymupdf

## Ranking por Ferramenta
| Ferramenta | Tempo médio (s) | % texto médio | Qualidade tabelas | Sucesso (%) |
| --- | --- | --- | --- | --- |
| docling | 55.41 | 99.4% | 0.0% | 100.0% |
| grobid | 9.77 | 45.6% | 68.4% | 100.0% |
| marker | 42.55 | 0.1% | 0.0% | 0.0% |
| markitdown | 3.64 | 89.5% | 0.0% | 100.0% |
| nougat | 32.03 | 2.6% | 0.0% | 0.0% |
| pdfplumber | 2.76 | 84.8% | 0.0% | 100.0% |
| pymupdf | 6.99 | 88.7% | 13.4% | 100.0% |

## Detalhes por PDF
### ALIMENTAÇÃO - The impact of nutrition and lifesytle modification on health.pdf
| Ferramenta | Tempo (s) | % texto | Tabelas | Figuras | Notas |
| --- | --- | --- | --- | --- | --- |
| docling | 64.03 | 100.0% | 6 (0%) | 0 | - |
| markitdown | 4.12 | 71.4% | 0 (0%) | 0 | - |
| pymupdf | 4.86 | 71.0% | 0 (0%) | 5 | - |
| pdfplumber | 3.10 | 70.0% | 0 (0%) | 0 | - |
| grobid | 35.29 | 29.3% | 1 (100%) | 2 | - |
| nougat | 34.95 | 2.0% | 0 (0%) | 0 | Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
/app/.venv/lib/python3.11/site-packages/torch/functional.py:505: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]

  0%|          | 0/8 [00:00<?, ?it/s]
  0%|          | 0/8 [00:15<?, ?it/s]
Traceback (most recent call last):
  File "/app/.venv/bin/nougat", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/predict.py", line 167, in main
    model_output = model.inference(
                   ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/nougat/model.py", line 592, in inference
    decoder_output = self.decoder.model.generate(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 120, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 1758, in generate
    result = self._sample(
             ^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 2394, in _sample
    model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'
-> Cannot close object, library is destroyed. This may cause a memory leak! |
| marker | 72.01 | 0.1% | 0 (0%) | 0 | Marker retornou código 137: Detecting bboxes:   0%|          | 0/2 [00:00<?, ?it/s] |

### ALIMENTAÇÃO- Journal of Internal Medicine - 2023 - Hu - Diet strategies for promoting healthy aging and longevity  An epidemiological.pdf
| Ferramenta | Tempo (s) | % texto | Tabelas | Figuras | Notas |
| --- | --- | --- | --- | --- | --- |
| docling | 60.79 | 100.0% | 3 (0%) | 0 | - |
| markitdown | 4.03 | 89.4% | 0 (0%) | 0 | - |
| pymupdf | 15.08 | 89.1% | 0 (0%) | 4 | - |
| pdfplumber | 4.38 | 84.7% | 8 (0%) | 0 | - |
| grobid | 5.05 | 42.1% | 2 (100%) | 3 | - |
| nougat | 33.56 | 1.2% | 0 (0%) | 0 | Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
/app/.venv/lib/python3.11/site-packages/torch/functional.py:505: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]

  0%|          | 0/24 [00:00<?, ?it/s]
  0%|          | 0/24 [00:12<?, ?it/s]
Traceback (most recent call last):
  File "/app/.venv/bin/nougat", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/predict.py", line 167, in main
    model_output = model.inference(
                   ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/nougat/model.py", line 592, in inference
    decoder_output = self.decoder.model.generate(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 120, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 1758, in generate
    result = self._sample(
             ^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 2394, in _sample
    model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'
-> Cannot close object, library is destroyed. This may cause a memory leak! |
| marker | 36.57 | 0.1% | 0 (0%) | 0 | Marker retornou código 137: Detecting bboxes:   0%|          | 0/6 [00:00<?, ?it/s] |

### DM - Diet and exercise in the prevention and treatment of type 2 diabetes mellitus.pdf
| Ferramenta | Tempo (s) | % texto | Tabelas | Figuras | Notas |
| --- | --- | --- | --- | --- | --- |
| pymupdf | 7.56 | 100.0% | 3 (67%) | 0 | - |
| markitdown | 3.58 | 99.6% | 0 (0%) | 0 | - |
| docling | 32.59 | 98.3% | 0 (0%) | 0 | - |
| pdfplumber | 2.79 | 98.3% | 2 (0%) | 0 | - |
| grobid | 3.17 | 61.2% | 0 (0%) | 5 | - |
| nougat | 32.82 | 3.4% | 0 (0%) | 0 | Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
/app/.venv/lib/python3.11/site-packages/torch/functional.py:505: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]

  0%|          | 0/11 [00:00<?, ?it/s]
  0%|          | 0/11 [00:13<?, ?it/s]
Traceback (most recent call last):
  File "/app/.venv/bin/nougat", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/predict.py", line 167, in main
    model_output = model.inference(
                   ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/nougat/model.py", line 592, in inference
    decoder_output = self.decoder.model.generate(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 120, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 1758, in generate
    result = self._sample(
             ^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 2394, in _sample
    model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak!
-> Cannot close object, library is destroyed. This may cause a memory leak! |
| marker | 33.80 | 0.1% | 0 (0%) | 0 | Marker retornou código 137: Detecting bboxes:   0%|          | 0/3 [00:00<?, ?it/s] |

### MOVIMENTO - The associations between sedentary behavior and risk of depression.pdf
| Ferramenta | Tempo (s) | % texto | Tabelas | Figuras | Notas |
| --- | --- | --- | --- | --- | --- |
| docling | 51.29 | 100.0% | 3 (0%) | 0 | - |
| markitdown | 3.19 | 86.8% | 0 (0%) | 0 | - |
| pymupdf | 3.35 | 84.2% | 0 (0%) | 4 | - |
| pdfplumber | 1.80 | 82.9% | 0 (0%) | 0 | - |
| grobid | 2.59 | 43.3% | 4 (75%) | 2 | - |
| nougat | 30.76 | 3.3% | 0 (0%) | 0 | Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
/app/.venv/lib/python3.11/site-packages/torch/functional.py:505: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]

  0%|          | 0/10 [00:00<?, ?it/s]
  0%|          | 0/10 [00:13<?, ?it/s]
Traceback (most recent call last):
  File "/app/.venv/bin/nougat", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/predict.py", line 167, in main
    model_output = model.inference(
                   ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/nougat/model.py", line 592, in inference
    decoder_output = self.decoder.model.generate(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 120, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 1758, in generate
    result = self._sample(
             ^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 2394, in _sample
    model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'
-> Cannot close object, library is destroyed. This may cause a memory leak! |
| marker | 35.52 | 0.2% | 0 (0%) | 0 | Marker retornou código 137: Detecting bboxes:   0%|          | 0/3 [00:00<?, ?it/s] |

### SONO - Fisiologia do sono, fisiopatologia e higiene do sono.pdf
| Ferramenta | Tempo (s) | % texto | Tabelas | Figuras | Notas |
| --- | --- | --- | --- | --- | --- |
| markitdown | 3.28 | 100.0% | 0 (0%) | 0 | - |
| pymupdf | 4.12 | 99.2% | 0 (0%) | 11 | - |
| docling | 68.36 | 98.8% | 3 (0%) | 0 | - |
| pdfplumber | 1.75 | 87.9% | 0 (0%) | 0 | - |
| grobid | 2.72 | 51.9% | 3 (67%) | 9 | - |
| nougat | 28.08 | 3.1% | 0 (0%) | 0 | Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
/app/.venv/lib/python3.11/site-packages/torch/functional.py:505: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at /pytorch/aten/src/ATen/native/TensorShape.cpp:4317.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]

  0%|          | 0/11 [00:00<?, ?it/s]
  0%|          | 0/11 [00:11<?, ?it/s]
Traceback (most recent call last):
  File "/app/.venv/bin/nougat", line 10, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/predict.py", line 167, in main
    model_output = model.inference(
                   ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/nougat/model.py", line 592, in inference
    decoder_output = self.decoder.model.generate(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/torch/utils/_contextlib.py", line 120, in decorate_context
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 1758, in generate
    result = self._sample(
             ^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/transformers/generation/utils.py", line 2394, in _sample
    model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'
-> Cannot close object, library is destroyed. This may cause a memory leak! |
| marker | 34.87 | 0.2% | 0 (0%) | 0 | Marker retornou código 137: Detecting bboxes:   0%|          | 0/3 [00:00<?, ?it/s] |
