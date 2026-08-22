import os
from pathlib import Path

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# 模型缓存目录放到项目内（沙箱/普通用户对 C 盘 .cache 无写权限）
os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parents[2] / "data" / "hf_cache"))

from sentence_transformers import SentenceTransformer  # noqa: E402

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return get_model().encode(texts, normalize_embeddings=True).tolist()
