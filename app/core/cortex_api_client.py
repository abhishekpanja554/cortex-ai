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