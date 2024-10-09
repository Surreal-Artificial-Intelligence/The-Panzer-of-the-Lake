from typing import List, Optional
import pymupdf
from pathlib import Path
import re


class DocumentEngine:
    def __init__(self, chunk_size: Optional[int] = None, overlap: Optional[int] = None):
        """
        Initializes the document processor with chunking options.

        :param chunk_size: The size of each chunk. If None, split by paragraph.
        :param overlap: The number of overlapping tokens/characters between chunks (useful for preserving context).
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks = {}

    def preprocess_document(self, document: Path) -> List[str]:
        """Chunks the input document into smaller sections"""

        pages = self.read_pdf(document)
        chunks = self.chunk_text(pages)
        return chunks

    def chunk_text(self, pages: List[str]):
        """Chunks a text chunk."""
        text = "".join(pages)
        if self.chunk_size and self.overlap:
            chunks = []
            for i in range(0, len(text), self.chunk_size - self.overlap):
                chunks.append(text[i: i + self.chunk_size])

        else:
            # Default: split by paragraphs
            chunks = text.split("\n\n")

        print("no. of chunks: ", len(chunks))
        self.chunks = chunks
        return chunks

    def read_pdf(self, file_str: Path) -> List[str]:
        """Reads text from a PDF file."""

        if not file_str.exists():
            raise FileNotFoundError()
        try:
            doc = pymupdf.open(file_str)
            out = []
            for page in doc:  # iterate the document pages
                text = page.get_text()
                out.append(text)
            return out
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return ["Error"]

    def remove_characters(self, text: str) -> str:
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map symbols
            "\U0001f1e0-\U0001f1ff"  # flags (iOS)
            "\U00002500-\U00002bef"  # chinese char
            "\U00002702-\U000027b0"
            "\U00002702-\U000027b0"
            "\U000024c2-\U0001f251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2b55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+",
            flags=re.UNICODE,
        )

        return emoji_pattern.sub(" ", text)
