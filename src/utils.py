# ==========================================================
# PROGRESS BAR
# ==========================================================

def progress_bar(done: int, total: int, width: int = 10) -> str:
    done = min(done, total)
    ratio = done / total

    filled = int(ratio * width)
    filled = min(filled, width)

    percent = int(ratio * 100)

    bar = "=" * filled + " " * (width - filled)
    return f"[{bar}] {percent:3d}%"
