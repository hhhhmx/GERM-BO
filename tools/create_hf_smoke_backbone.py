from pathlib import Path

from transformers import BertConfig, BertModel, BertTokenizerFast


def main() -> None:
    output_dir = Path("local_assets/hf_smoke_backbone")
    output_dir.mkdir(parents=True, exist_ok=True)

    vocab_path = output_dir / "vocab.txt"
    vocab_tokens = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "A", "C", "G", "T", "N"]
    vocab_path.write_text("\n".join(vocab_tokens) + "\n", encoding="utf-8")

    tokenizer = BertTokenizerFast(
        vocab_file=str(vocab_path),
        do_lower_case=False,
        tokenize_chinese_chars=False,
    )
    tokenizer.save_pretrained(str(output_dir))

    config = BertConfig(
        vocab_size=len(vocab_tokens),
        hidden_size=32,
        num_hidden_layers=2,
        num_attention_heads=4,
        intermediate_size=64,
        max_position_embeddings=256,
        pad_token_id=0,
    )
    model = BertModel(config)
    model.save_pretrained(str(output_dir))
    print(output_dir.as_posix())


if __name__ == "__main__":
    main()
