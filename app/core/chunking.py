import tiktoken


def chunk_text(text: str, chunk_size_tokens: int, chunk_overlap_tokens: int) -> list[str]:
    if not text:
        return []

    if chunk_size_tokens <= chunk_overlap_tokens:
        raise ValueError(
            "chunk_size_tokens must be strictly greater than chunk_overlap_tokens to prevent infinite loops.")
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text, disallowed_special=())
    if len(tokens) <= chunk_size_tokens:
        return [text]

    chunks = []
    step_size = chunk_size_tokens - chunk_overlap_tokens
    for i in range(0, len(tokens), step_size):
        window_tokens = tokens[i: i + chunk_size_tokens]
        chunk_str = encoding.decode(window_tokens)
        chunks.append(chunk_str)
        if i + chunk_size_tokens >= len(tokens):
            break

    return chunks