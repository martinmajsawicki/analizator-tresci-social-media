"""Moduł do czytania plików źródłowych (txt, md, docx, pdf)."""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SourceFile:
    """Reprezentacja pliku źródłowego."""
    path: Path
    name: str
    extension: str
    size_bytes: int
    modified_time: datetime

    @property
    def size_human(self) -> str:
        """Zwraca rozmiar w czytelnej formie."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes}B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes // 1024}KB"
        else:
            return f"{self.size_bytes // (1024 * 1024)}MB"

    @property
    def modified_date(self) -> str:
        """Zwraca datę modyfikacji."""
        return self.modified_time.strftime("%Y-%m-%d")


class FileReader:
    """Czytnik plików źródłowych."""

    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.docx', '.pdf'}

    def __init__(self, default_folder: Optional[Path] = None):
        """
        Inicjalizacja czytnika.

        Args:
            default_folder: Domyślny folder z plikami (domyślnie: posts/)
        """
        if default_folder is None:
            self.default_folder = Path(__file__).parent.parent / "posts"
        else:
            self.default_folder = Path(default_folder)

        # Upewnij się że folder istnieje
        self.default_folder.mkdir(parents=True, exist_ok=True)

    def list_files(self, folder: Optional[Path] = None) -> List[SourceFile]:
        """
        Listuje pliki źródłowe w folderze.

        Args:
            folder: Folder do przeszukania (domyślnie: default_folder)

        Returns:
            Lista plików posortowana po dacie modyfikacji (najnowsze pierwsze)
        """
        target_folder = folder or self.default_folder

        if not target_folder.exists():
            return []

        files = []
        for item in target_folder.iterdir():
            if item.is_file() and item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                stat = item.stat()
                files.append(SourceFile(
                    path=item,
                    name=item.name,
                    extension=item.suffix.lower(),
                    size_bytes=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                ))

        # Sortuj po dacie modyfikacji (najnowsze pierwsze)
        files.sort(key=lambda f: f.modified_time, reverse=True)
        return files

    def read_file(self, file_path: Path) -> str:
        """
        Czyta zawartość pliku.

        Args:
            file_path: Ścieżka do pliku

        Returns:
            Zawartość pliku jako string

        Raises:
            FileNotFoundError: Jeśli plik nie istnieje
            ValueError: Jeśli format nie jest obsługiwany
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {path}")

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Nieobsługiwany format: {extension}. "
                f"Obsługiwane: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        if extension in {'.txt', '.md'}:
            return self._read_text(path)
        elif extension == '.docx':
            return self._read_docx(path)
        elif extension == '.pdf':
            return self._read_pdf(path)

        raise ValueError(f"Nieobsługiwany format: {extension}")

    def _read_text(self, path: Path) -> str:
        """Czyta plik tekstowy (txt, md)."""
        encodings = ['utf-8', 'cp1250', 'iso-8859-2', 'latin-1']

        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        # Fallback - czytaj z ignorowaniem błędów
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_docx(self, path: Path) -> str:
        """Czyta plik Word (.docx)."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "Brak biblioteki python-docx. Zainstaluj: pip install python-docx"
            )

        doc = Document(path)
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n\n'.join(paragraphs)

    def _read_pdf(self, path: Path) -> str:
        """Czyta plik PDF."""
        # Próbuj PyPDF2 najpierw
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return '\n\n'.join(text_parts)
        except ImportError:
            pass

        # Próbuj pdfplumber jako fallback
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n\n'.join(text_parts)
        except ImportError:
            pass

        raise ImportError(
            "Brak biblioteki do PDF. Zainstaluj: pip install PyPDF2 lub pip install pdfplumber"
        )

    def is_valid_path(self, path_str: str) -> bool:
        """Sprawdza czy ścieżka jest prawidłowa i plik istnieje."""
        try:
            path = Path(path_str).expanduser().resolve()
            return path.exists() and path.is_file()
        except Exception:
            return False

    def get_file_info(self, path_str: str) -> Optional[SourceFile]:
        """Zwraca informacje o pliku na podstawie ścieżki."""
        try:
            path = Path(path_str).expanduser().resolve()
            if not path.exists() or not path.is_file():
                return None

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                return None

            stat = path.stat()
            return SourceFile(
                path=path,
                name=path.name,
                extension=path.suffix.lower(),
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
            )
        except Exception:
            return None


def format_file_list(files: List[SourceFile], max_name_length: int = 45) -> str:
    """
    Formatuje listę plików do wyświetlenia.

    Args:
        files: Lista plików
        max_name_length: Maksymalna długość nazwy pliku

    Returns:
        Sformatowany string z listą plików
    """
    if not files:
        return "  (brak plików)"

    lines = []
    for i, f in enumerate(files, 1):
        name = f.name
        if len(name) > max_name_length:
            name = name[:max_name_length - 3] + "..."

        # Wyrównaj kolumny
        line = f"  [{i}] {name:<{max_name_length}}  ({f.modified_date}, {f.size_human})"
        lines.append(line)

    return '\n'.join(lines)
