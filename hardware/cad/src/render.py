"""STL/메시를 PNG로 렌더 — Claude 육안 검증용 (W0-T02p P0).

사용: uv run python src/render.py <in.stl> <out.png> [--views iso,front,side,top]
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

log = logging.getLogger("render")

# (elev, azim) — +Z 위, +Y 정면 (W0-T02p P3 원점 규약)
VIEWS = {
    "iso": (25, -60),
    "front": (0, -90),
    "side": (0, 0),
    "top": (90, -90),
}


def render(mesh: trimesh.Trimesh, out: Path, views: list[str], max_faces: int = 60000) -> None:
    if len(mesh.faces) > max_faces:
        # matplotlib는 고폴리에서 매우 느림 — 렌더 전용으로만 간략화
        mesh = mesh.simplify_quadric_decimation(face_count=max_faces)
    tris = mesh.vertices[mesh.faces]
    normals = mesh.face_normals
    light = np.array([0.3, -0.5, 0.8])
    light /= np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(normals @ light, 0, 1)
    colors = np.stack([shade * 0.55, shade * 0.7, shade * 0.9, np.ones_like(shade)], axis=1)

    lo, hi = mesh.bounds
    center, span = (lo + hi) / 2, (hi - lo).max() / 2

    fig = plt.figure(figsize=(4 * len(views), 4), dpi=110)
    for i, name in enumerate(views, 1):
        ax = fig.add_subplot(1, len(views), i, projection="3d")
        ax.add_collection3d(Poly3DCollection(tris, facecolors=colors, edgecolor="none"))
        for setlim, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), center):
            setlim(c - span, c + span)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(*VIEWS[name])
        ax.set_title(name)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
    fig.suptitle(f"{out.stem}  bbox={np.round(hi - lo, 1).tolist()} mm  faces={len(mesh.faces)}")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    log.info("rendered %s", out)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    p = argparse.ArgumentParser()
    p.add_argument("src", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--views", default="iso,front,side,top")
    a = p.parse_args()
    try:
        mesh = trimesh.load_mesh(a.src, force="mesh")
    except Exception as e:  # 파일 손상·포맷 오류
        log.error("load failed: %s: %s", a.src, e)
        return 1
    views = a.views.split(",")
    bad = [v for v in views if v not in VIEWS]
    if bad:
        log.error("unknown views: %s (allowed: %s)", bad, list(VIEWS))
        return 2
    render(mesh, a.out, views)
    return 0


if __name__ == "__main__":
    sys.exit(main())
