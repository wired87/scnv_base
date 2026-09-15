from datetime import datetime, timezone
import pprint
from scripts.stemcnv_docker import _collect_events
from scripts.utils import _run_docker
from datetime import datetime, timezone
import pprint

def _emit_console_events(old_events, new_events):
    """Print only newly added events to console."""
    if not old_events:
        for ev in new_events:
            print(f"[{ev['at']}] {ev['type']}: {ev['message']}")
        return

    old_len = len(old_events)
    new_items = new_events[old_len:]

    for ev in new_items:
        print(f"[{ev['at']}] {ev['type']}: {ev['message']}")

def _update_docker_state(run_id, events, last_log_message):
    # --- FETCH BASIC DOCKER STATE ---
    state = _run_docker("inspect", "-f", "{{.State.Status}}|{{.State.ExitCode}}", run_id, check=False)
    
    container_status, exit_code = state.stdout.strip().split("|", 1)

    # --- FETCH LOGS ---
    logs = _run_docker("logs", "--tail", "500", run_id, check=False)
    log_text = logs.stdout + logs.stderr

    # --- PARSE WORKFLOW EVENTS ---
    events = _collect_events(log_text, events)

    public_status = container_status
    event = None
    now_iso = datetime.now(timezone.utc).isoformat()

    # --- CLASSIFICATION: DOCKER STATES ---
    if container_status in ("running", "paused", "restarting", "dead", "created"):
        event = {
            "type": container_status,
            "message": log_text,
            "at": now_iso
        }
    elif container_status == "exited":
        public_status = "complete" if exit_code == "0" else "failed"

        # Mapping von Exit-Codes auf Event-Typen
        exit_code_map = {
            "0": "success",
            "1": "error",
            "137": "oom_killed",
            "143": "terminated",
            "255": "not_found"
        }
        event_type = exit_code_map.get(exit_code, f"exited_with_code_{exit_code}")

        event = {
            "type": event_type,
            "message": log_text,
            "at": now_iso
        }

    # --- LOG-EVENT HINZUFÜGEN & EMITTEN ---
    if event and last_log_message != event["message"]:
        print("############### NEW LOG EVENT DETECTED")
        pprint.pp(event)

        # Neue Event-Liste erstellen für die Emission der Konsole
        old_events = list(events)
        events.append(event)
        
        # Konsolenausgabe triggern
        _emit_console_events(old_events, events)
        
        # Zustand der letzten Log-Nachricht aktualisieren
        last_log_message = event["message"]

    return public_status, events, last_log_message