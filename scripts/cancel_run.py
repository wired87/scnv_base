from datetime import datetime, timezone

from product.components.run_engine.models import StemCNVRun
from product.components.run_engine.workflow import _run_docker
from product.stemcnv_docker import PROCESS_ROLE


def cancel_run(run_id: str) -> dict:
    record = StemCNVRun.objects.get(run_id=run_id)
    if record.status not in {"queued", "starting", "created", "running", "cancelling"}:
        return {"run_id": run_id, "status": record.status}
    if record.status in {"running", "cancelling"} and PROCESS_ROLE != "web":
        _run_docker("stop", "--time", "30", run_id, check=False)
    elif record.status == "running":
        record.events = [
            *record.events, 
            {"type": "cancellation_requested",
            "message": "Cancellation requested from web service",
            "at": datetime.now(timezone.utc).isoformat()}]
        record.status = "cancelling"
        record.save()
        return {"run_id": run_id, "status": record.status, "events": record.events}
    record.status = "cancelled"
    record.completed_at = datetime.now(timezone.utc)
    record.events = [*record.events, {"type": "cancelled", "message": "Run cancelled safely",
                                      "at": record.completed_at.isoformat()}]
    record.save()
    return {"run_id": run_id, "status": "cancelled", "events": record.events}
