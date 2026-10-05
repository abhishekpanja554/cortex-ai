from uuid import UUID, uuid4

from app.core.pending_actions import create_pending_action, get_pending_action, resolve_pending_action

owner_id = UUID("f9219701-d6c8-4992-8ca5-32bb26dc7bb8")
wrong_owner_id = UUID("8eeb7cf2-bf09-4134-ab9d-629dc36af9bc")

print("--- create ---")
confirmation_id = create_pending_action(owner_id, "delete_note", {"note_id": "fake-note-id-for-testing"})
print(confirmation_id)

print("--- get (should be PENDING) ---")
print(get_pending_action(confirmation_id))

print("--- resolve with WRONG owner (should be None — doesn't belong to them) ---")
print(resolve_pending_action(confirmation_id, wrong_owner_id, approved=True))

print("--- confirm it's still PENDING after the wrong-owner attempt ---")
print(get_pending_action(confirmation_id))

print("--- resolve with correct owner, approved=True (should return tool_name/tool_args) ---")
print(resolve_pending_action(confirmation_id, owner_id, approved=True))

print("--- resolve AGAIN with correct owner (should be None — already resolved, no double-confirm) ---")
print(resolve_pending_action(confirmation_id, owner_id, approved=True))

print("--- final state (should be EXECUTED, resolved_at set) ---")
print(get_pending_action(confirmation_id))

print("--- reject path on a fresh pending action ---")
cid2 = create_pending_action(owner_id, "delete_note", {"note_id": "another-fake-id"})
print(resolve_pending_action(cid2, owner_id, approved=False))
print(get_pending_action(cid2))