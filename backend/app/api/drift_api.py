from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from ..services.drift import CONFIGS, SNAPSHOTS, register, snapshot, compare, dashboard, seed
router = APIRouter()
class RegIn(BaseModel):
    name: str
    expected_text: str
    format: str = "json"
class SnapIn(BaseModel):
    name: str
    observed_text: str
    format: Optional[str] = None
@router.post("/configs")
def add_cfg(body: RegIn):
    return register(body.name, body.expected_text, body.format)
@router.get("/configs")
def list_cfg():
    return {"total": len(CONFIGS), "configs": list(CONFIGS.values())}
@router.post("/snapshots")
def add_snap(body: SnapIn):
    return snapshot(body.name, body.observed_text, body.format)
@router.get("/snapshots")
def list_snaps(config_name: str = ""):
    items = SNAPSHOTS
    if config_name:
        items = [s for s in items if s["config_name"] == config_name]
    return {"total": len(items), "snapshots": items}
@router.get("/compare")
def do_compare(name: str, snapshot_id: int):
    return compare(name, snapshot_id)
@router.post("/seed")
def do_seed():
    return {"seeded": seed()}
@router.get("/dashboard")
def dash():
    return dashboard()
