# Inference & Quantization Benchmarks

## Quantization Stats

- Model directory: `models/quantized/8bit_model`
- Size on disk: *TBD*
- Memory footprint (GPU/CPU): *TBD*

## Inference Benchmarks

Refer to `docs/benchmarks.csv` for end-to-end latency comparisons:
```csv
engine,avg_latency_ms
pytorch,XXX
pytorch+flash,YYY
onnx,ZZZ
```

## FlashAttention Speedup

- FlashAttention enabled via `flash_attn_unpadded`: TBD× speedup

# FlashAttention Integration
- Add FlashAttention benchmark results to `docs/benchmarks.csv` once measurements are complete.
