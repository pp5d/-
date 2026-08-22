import httpx

from app.config import settings


def build_prompt(question: str, contexts: list[str]) -> str:
    parts = ["以下是注塑机上位机领域的知识片段："]
    for i, c in enumerate(contexts, 1):
        parts.append(f"[{i}] {c}")
    parts.append(
        f"\n请仅基于以上知识片段回答用户问题，若片段中没有答案请明确说“知识库暂无相关内容”。\n用户问题：{question}"
    )
    return "\n".join(parts)


def generate(question: str, contexts: list[str]) -> str:
    prompt = build_prompt(question, contexts)
    r = httpx.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是注塑机上位机技术助手，只基于提供的知识片段回答，不编造。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
