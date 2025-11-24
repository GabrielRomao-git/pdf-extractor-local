Falha na ferramenta nougat: Nougat retornou código 1: WARNING:root:No GPU found. Conversion on CPU is very slow.
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
-> Cannot close object, library is destroyed. This may cause a memory leak!