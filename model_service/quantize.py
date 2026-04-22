import argparse
from pathlib import Path
from typing import Any, Sequence


def default_quant_config() -> dict[str, Any]:
    return {
        "zero_point": True,
        "q_group_size": 128,
        "w_bit": 4,
        "version": "GEMM",
    }


def quantize_model(model_path: str, output_path: str, quant_config: dict[str, Any] | None = None) -> None:
    config = quant_config or default_quant_config()

    try:
        import torch
        from awq import AutoAWQForCausalLM
        from transformers import AutoTokenizer
    except ImportError as exc:  # pragma: no cover - exercised only in real quantization runs
        raise ImportError(
            "quantize_model requires torch, transformers, and awq to be installed"
        ) from exc

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoAWQForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    model.quantize(tokenizer, quant_config=config)
    model.save_quantized(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Quantize a model with AWQ")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--output_path", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    quantize_model(args.model_path, args.output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
