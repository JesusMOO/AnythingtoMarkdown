from pathlib import Path


_MARKER_READY = False
_SURYA_CHECKPOINTS = (
    "DETECTOR_MODEL_CHECKPOINT",
    "LAYOUT_MODEL_CHECKPOINT",
    "OCR_ERROR_MODEL_CHECKPOINT",
    "RECOGNITION_MODEL_CHECKPOINT",
    "TABLE_REC_MODEL_CHECKPOINT",
)


def marker_initialization_required() -> bool:
    global _MARKER_READY

    if _MARKER_READY:
        return False

    try:
        from surya.common.s3 import check_manifest
        from surya.settings import settings
    except ImportError:
        return True

    cache_dir = Path(settings.MODEL_CACHE_DIR)
    for checkpoint_name in _SURYA_CHECKPOINTS:
        checkpoint = getattr(settings, checkpoint_name, "")
        if checkpoint.startswith("s3://"):
            if not check_manifest(str(cache_dir / checkpoint.removeprefix("s3://"))):
                return True
            continue
        if checkpoint and not Path(checkpoint).exists():
            return True

    _MARKER_READY = True
    return False


def ensure_marker_ready() -> None:
    global _MARKER_READY

    if _MARKER_READY:
        return

    from surya.models import load_predictors

    load_predictors()
    _MARKER_READY = True
