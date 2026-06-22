import os
import re
from collections import Counter

import google.generativeai as genai

NOISE_PATTERNS = (
    "online learning center",
    "mcgraw-hill",
    "mhhe.com",
    "instructor resources",
    "representative for a secure password",
    "copyright",
    "all rights reserved",
    "isbn",
    "printed in",
    "library of congress",
)

STOPWORDS = {
    "about", "after", "again", "against", "also", "because", "been", "before", "being",
    "between", "both", "could", "does", "each", "from", "have", "into", "more", "most",
    "other", "over", "same", "should", "such", "than", "that", "their", "there", "these",
    "they", "this", "those", "through", "under", "using", "very", "were", "when", "where",
    "which", "while", "with", "would", "your",
}


def generate_notes(extracted_text: str) -> dict[str, str]:
    if not extracted_text.strip():
        raise ValueError("No text could be extracted from this document")

    cleaned_text = clean_document_text(extracted_text)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_notes(cleaned_text)

    return _generate_with_gemini(cleaned_text, api_key)


def _generate_with_gemini(cleaned_text: str, api_key: str) -> dict[str, str]:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    chunks = _chunk_text(cleaned_text, int(os.getenv("GEMINI_CHUNK_CHARS", "22000")))
    max_chunks = int(os.getenv("MAX_NOTE_CHUNKS", "80"))

    short_sections = []
    detailed_sections = []
    for index, chunk in enumerate(chunks[:max_chunks], start=1):
        prompt = f"""
You are making textbook study notes from chunk {index} of {len(chunks)}.
Cover EVERY topic and subtopic visible in this chunk. Do not select random sentences.

Output exactly this plain-text format:

SHORT NOTES
## Topic Heading
- One or two line gist of that topic.

DETAILED NOTES
## Topic Heading
- Main point in detail.
- Important definition, rule, list, example, or process.

Rules:
- Preserve textbook topic headings when visible.
- If headings are missing, create accurate topic headings from the content.
- Ignore publisher pages, URLs, copyright, instructor resources, acknowledgements, ads, and front matter.
- Do not mention that this is a chunk.
- Do not skip a topic just because it is small.

Text:
{chunk}
"""
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
        short_part, detailed_part = _split_ai_sections(raw)
        if short_part:
            short_sections.append(short_part)
        if detailed_part:
            detailed_sections.append(detailed_part)

    if not short_sections and not detailed_sections:
        return _fallback_notes(cleaned_text)

    return {
        "short_notes": "\n\n".join(short_sections).strip(),
        "detailed_notes": "\n\n".join(detailed_sections).strip(),
    }


def clean_document_text(text: str) -> str:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        lower = line.lower()
        if any(pattern in lower for pattern in NOISE_PATTERNS):
            continue
        if re.search(r"https?://|www\.|\.com", lower):
            continue
        if len(line) < 4:
            continue
        lines.append(line)
    return "\n".join(lines)


def _fallback_notes(extracted_text: str) -> dict[str, str]:
    topics = _extract_topics(extracted_text)
    if not topics:
        return {
            "short_notes": "- No clear textbook topics were detected. Add GEMINI_API_KEY for stronger AI notes.",
            "detailed_notes": extracted_text[:4000],
        }

    max_topics = int(os.getenv("MAX_FALLBACK_TOPICS", "160"))
    topics = topics[:max_topics]
    short_blocks = []
    detailed_blocks = []

    for topic in topics:
        sentences = _extract_sentences(topic["content"])
        if not sentences:
            continue

        gist = _make_gist(sentences)
        main_points = _topic_main_points(sentences)
        short_blocks.append(f"## {topic['heading']}\n- {gist}")
        detailed_blocks.append(
            f"## {topic['heading']}\n" + "\n".join(f"- {point}" for point in main_points)
        )

    if not short_blocks:
        ranked = _rank_sentences(_extract_sentences(extracted_text))[:30]
        short_blocks = [f"- {sentence}" for sentence in ranked[:15]]
        detailed_blocks = [f"## Extracted Main Points\n" + "\n".join(f"- {sentence}" for sentence in ranked)]

    detailed_blocks.append(
        "## Note Quality\n"
        "- These notes were generated without Gemini, so they are structured extractive notes from the textbook text.\n"
        "- Add GEMINI_API_KEY for complete abstractive notes across every topic and subtopic."
    )
    return {
        "short_notes": "\n\n".join(short_blocks),
        "detailed_notes": "\n\n".join(detailed_blocks),
    }


def _chunk_text(text: str, chunk_size: int) -> list[str]:
    lines = text.splitlines()
    chunks = []
    current = []
    current_len = 0
    for line in lines:
        line_len = len(line) + 1
        if current and current_len + line_len > chunk_size:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


def _split_ai_sections(text: str) -> tuple[str, str]:
    short_match = re.search(r"SHORT NOTES\s*(.*?)(?:DETAILED NOTES|$)", text, flags=re.IGNORECASE | re.DOTALL)
    detailed_match = re.search(r"DETAILED NOTES\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
    short = short_match.group(1).strip() if short_match else ""
    detailed = detailed_match.group(1).strip() if detailed_match else text.strip()
    return short, detailed


def _extract_topics(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    topics = []
    current_heading = "Overview"
    current_content = []

    for line in lines:
        if _is_heading(line):
            _append_topic(topics, current_heading, current_content)
            current_heading = _clean_heading(line)
            current_content = []
        else:
            current_content.append(line)

    _append_topic(topics, current_heading, current_content)

    return topics or _paragraph_topics(text)


def _append_topic(topics: list[dict[str, str]], heading: str, content_lines: list[str]) -> None:
    content = " ".join(content_lines).strip()
    if len(content) < 80:
        return
    if _is_noise(content):
        return
    topics.append({"heading": heading, "content": content})


def _paragraph_topics(text: str) -> list[dict[str, str]]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n{2,}", text) if len(paragraph.strip()) > 220]
    topics = []
    for index, paragraph in enumerate(paragraphs, start=1):
        sentences = _extract_sentences(paragraph)
        if not sentences:
            continue
        heading = _derive_heading(sentences[0], index)
        topics.append({"heading": heading, "content": paragraph})
    return topics


def _is_heading(line: str) -> bool:
    cleaned = _clean_heading(line)
    lower = cleaned.lower()
    if len(cleaned) < 4 or len(cleaned) > 95:
        return False
    if _is_noise(cleaned):
        return False
    if cleaned.endswith(".") and len(cleaned.split()) > 6:
        return False
    if re.match(r"^(chapter|section|part)\s+\d+", lower):
        return True
    if re.match(r"^\d+(\.\d+){0,4}\s+[A-Z][A-Za-z0-9,/() -]+$", cleaned):
        return True
    words = cleaned.split()
    if 2 <= len(words) <= 9:
        title_words = sum(1 for word in words if word[:1].isupper() or word.isupper())
        if title_words / len(words) >= 0.65:
            return True
    return False


def _clean_heading(line: str) -> str:
    line = re.sub(r"\s+", " ", line).strip(" -:\t")
    line = re.sub(r"^(chapter|section)\s+(\d+)\s*[:.-]?\s*", r"\1 \2: ", line, flags=re.IGNORECASE)
    return line[:95]


def _is_noise(text: str) -> bool:
    lower = text.lower()
    return any(pattern in lower for pattern in NOISE_PATTERNS) or bool(re.search(r"https?://|www\.|\.com", lower))


def _derive_heading(sentence: str, index: int) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z-]{3,}", sentence)
    useful = [word for word in words if word.lower() not in STOPWORDS][:6]
    if useful:
        return " ".join(useful).title()
    return f"Topic {index}"


def _make_gist(sentences: list[str]) -> str:
    if len(sentences) == 1:
        return sentences[0]
    return f"{sentences[0]} {sentences[1]}"


def _topic_main_points(sentences: list[str]) -> list[str]:
    ranked = _rank_sentences(sentences)
    selected = ranked[:10]
    if len(selected) < 4:
        selected = sentences[:8]
    return selected


def _extract_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    candidates = re.split(r"(?<=[.!?])\s+", normalized)
    sentences = []
    for candidate in candidates:
        sentence = candidate.strip(" -\t")
        lower = sentence.lower()
        if len(sentence) < 55 or len(sentence) > 360:
            continue
        if _is_noise(sentence):
            continue
        if sum(char.isalpha() for char in sentence) < 35:
            continue
        sentences.append(sentence)
    return sentences


def _rank_sentences(sentences: list[str]) -> list[str]:
    words = [
        word
        for sentence in sentences
        for word in re.findall(r"[a-zA-Z]{4,}", sentence.lower())
        if word not in STOPWORDS
    ]
    frequencies = Counter(words)
    scored = []
    for index, sentence in enumerate(sentences):
        terms = [
            word
            for word in re.findall(r"[a-zA-Z]{4,}", sentence.lower())
            if word not in STOPWORDS
        ]
        if not terms:
            continue
        score = sum(frequencies[word] for word in terms) / len(terms)
        scored.append((score, index, sentence))

    top = sorted(scored, key=lambda item: item[0], reverse=True)[:24]
    return [sentence for _, _, sentence in sorted(top, key=lambda item: item[1])]
