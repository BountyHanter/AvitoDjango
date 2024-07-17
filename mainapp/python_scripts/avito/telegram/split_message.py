def split_message(text, max_length=1224):
    parts = []
    while len(text) > max_length:
        chunk = text[:max_length]
        last_newline_index = chunk.rfind('\n\n')
        if last_newline_index != -1:
            chunk = text[:last_newline_index + 2]
        parts.append(chunk)
        text = text[len(chunk):]
    parts.append(text)
    return parts
