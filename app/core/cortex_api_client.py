from uuid import UUID

import httpx


class CortexApiClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self._client = httpx.Client(
            base_url = base_url.rstrip("/"),
            headers = {"X-Internal-Api-Key": api_key},
            timeout = timeout,
        )

    def complete(self, job_id: UUID) -> None:
        res = self._client.post(f"internal/jobs/{job_id}/complete")
        res.raise_for_status()

    def fail(self, job_id: UUID, error_message: str) -> None:
        res = self._client.post(
            f"internal/jobs/{job_id}/fail",
            json={"errorMessage": error_message},
        )
        res.raise_for_status()

    def search_notes(self, owner_id: UUID, query: str, limit: int) -> list[dict]:
        res = self._client.post(
            "internal/search",
            json={
                "ownerId": str(owner_id),
                "query": query,
                "limit": limit
            }
        )
        res.raise_for_status()
        return res.json()

    def get_note(self, owner_id: UUID, note_id: UUID) -> dict:
        res = self._client.get(f"internal/notes/{note_id}", params={"ownerId" : str(owner_id)})
        res.raise_for_status()
        return res.json()["data"]

    def delete_note(self, owner_id: UUID, note_id: UUID) -> None:
        res = self._client.delete(f"internal/notes/{note_id}", params={"ownerId" : str(owner_id)})
        res.raise_for_status()

    def create_note(self, owner_id: UUID, title: str, body: str) -> dict:
        res = self._client.post(
            "internal/notes",
            params={"ownerId": str(owner_id)},
            json={"title": title, "body": body}
        )
        res.raise_for_status()
        return res.json()["data"]

    def update_note(self, owner_id: UUID, note_id: UUID, title: str, body: str) -> dict:
        res = self._client.put(
            f"internal/notes/{note_id}",
            params={"ownerId": str(owner_id)},
            json={"title": title, "body": body}
        )
        res.raise_for_status()
        return res.json()["data"]