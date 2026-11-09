"""P0 스모크 테스트 — CAD 파이프라인 전 구간 동작 확인 (W0-T02p).

CadQuery 생성 → STEP/STL export → trimesh 무결성 → manifold3d boolean → PNG 렌더.
아래 수치는 파이프라인 검증용 더미 형상이며 설계값이 아니다 (설계값은 params/*.yaml, P1에서 정의).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import cadquery as cq
import manifold3d as m3d
import numpy as np
import trimesh

from render import render

log = logging.getLogger("p0_smoke")

ROOT = Path(__file__).resolve().parents[2]  # /Users/heebiny/canduck/hardware
OUT = ROOT / "models" / "out" / "p0"
REPORT = ROOT / "cad" / "reports" / "p0"


def build() -> cq.Workplane:
    # 더미: 포켓 + 관통홀 + 필렛이 있는 브래킷 (OCCT 필렛 동작 확인 포함)
    return (
        cq.Workplane("XY")
        .box(30, 20, 20)
        .edges("|Z").fillet(2.0)
        .faces(">Z").workplane()
        .rect(23.4, 12.8).cutBlind(-15)
        .faces("<X").workplane(centerOption="CenterOfBoundBox")
        .hole(8.0)
    )


def check_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load_mesh(path, force="mesh")
    if not mesh.is_watertight:
        raise RuntimeError(f"not watertight: {path}")
    log.info("watertight=%s volume=%.1f mm3 bbox=%s", mesh.is_watertight, mesh.volume,
             np.round(mesh.extents, 2).tolist())
    return mesh


def manifold_boolean(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    src = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32),
                                tri_verts=np.asarray(mesh.faces, np.uint32)))
    cutter = m3d.Manifold.cylinder(40, 3, 3, 32).translate([0, 0, -20])  # Z 관통 Ø6
    res = (src - cutter).to_mesh()
    out = trimesh.Trimesh(vertices=res.vert_properties[:, :3], faces=res.tri_verts)
    if not out.is_watertight or out.volume >= mesh.volume:
        raise RuntimeError("manifold boolean result invalid")
    log.info("manifold boolean ok: volume %.1f -> %.1f mm3", mesh.volume, out.volume)
    return out


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        part = build()
        step, stl = OUT / "smoke.step", OUT / "smoke.stl"
        cq.exporters.export(part, str(step))
        cq.exporters.export(part, str(stl), tolerance=0.01, angularTolerance=0.1)
        log.info("exported %s, %s", step, stl)
        mesh = check_mesh(stl)
        cut = manifold_boolean(mesh)
        cut_stl = OUT / "smoke_cut.stl"
        cut.export(cut_stl)
        render(cut, REPORT / "smoke_cut.png", ["iso", "front", "top"])
    except Exception:
        log.exception("P0 smoke FAILED")
        return 1
    log.info("P0 smoke OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
