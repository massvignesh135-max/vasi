from __future__ import annotations

import html


def format_html_preview(exports):
    """
    Convert exported document data into an HTML preview.
    """

    if not exports:
        return "<p>No document generated yet.</p>"

    if isinstance(exports, str):
        return exports

    if isinstance(exports, dict):
        parts = []

        for key, value in exports.items():
            parts.append(
                f"<h3>{html.escape(str(key))}</h3>"
                f"<p>{html.escape(str(value))}</p>"
            )

        return "\n".join(parts)

    return f"<pre>{html.escape(str(exports))}</pre>"