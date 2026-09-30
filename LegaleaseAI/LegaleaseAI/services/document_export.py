from __future__ import annotations

from pathlib import Path

def export_all(
    text: str,
    output_dir: str | None = None,
    doc_type: str | None = None,
    logo_path: str | None = None,
):
    """
    Create simple export files from generated legal text.
    """

    if not text:
        text = ""

    if output_dir is None:
        output_dir = "exports"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = {}

    # TXT
    txt_path = output_path / "legal_document.txt"
    txt_path.write_text(text, encoding="utf-8")
    files["txt"] = txt_path

    # HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>LegalEase Document</title>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: Arial;">
{text}
    </pre>
</body>
</html>
"""

    html_path = output_path / "legal_document.html"
    html_path.write_text(html_content, encoding="utf-8")
    files["html"] = html_path

    return files