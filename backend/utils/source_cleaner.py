import re


def clean_source_url(source):
    if not source:
        return None

    source = str(source).strip()

    # Markdown link: [text](https://example.com)
    match = re.search(r"\]\((https?://[^)]+)\)", source)
    if match:
        return match.group(1).strip()

    # Plain URL
    if source.startswith(("http://", "https://")):
        return source.rstrip(".,;)")

    return None


def clean_sources(sources):
    result = []

    for source in sources or []:
        url = clean_source_url(source)

        if url and url not in result:
            result.append(url)

    return result