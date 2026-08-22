from app.services.embedding import embed_texts


def test_embed_dims():
    v = embed_texts(["模保报警怎么处理"])
    assert len(v) == 1
    assert len(v[0]) == 512  # bge-small-zh-v1.5 维度


def test_embed_normalized():
    v = embed_texts(["测试文本"])[0]
    norm = sum(x * x for x in v) ** 0.5
    assert abs(norm - 1.0) < 0.01
