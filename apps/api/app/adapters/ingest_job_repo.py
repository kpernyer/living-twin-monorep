from typing import Any, Dict, List, Optional


class IngestJobRepository:
    def create_job(self, job: Dict[str, Any]) -> None:
        raise NotImplementedError

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def list_jobs(self, tenant_id: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        raise NotImplementedError


class InMemoryIngestJobRepo(IngestJobRepository):
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, job: Dict[str, Any]) -> None:
        self._jobs[job["jobId"]] = job

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        if job_id in self._jobs:
            self._jobs[job_id].update(updates)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

    def list_jobs(self, tenant_id: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        jobs = [
            j
            for j in self._jobs.values()
            if j.get("tenantId") == tenant_id and j.get("userId") == user_id
        ]
        jobs.sort(key=lambda j: j.get("updatedAt", 0), reverse=True)
        return jobs[:limit]


class FirestoreIngestJobRepo(IngestJobRepository):
    def __init__(self, project_id: Optional[str] = None):
        from google.cloud import firestore  # lazy import

        self._db = firestore.Client(project=project_id) if project_id else firestore.Client()
        self._col = self._db.collection("ingest_jobs")

    def create_job(self, job: Dict[str, Any]) -> None:
        self._col.document(job["jobId"]).set(job)

    def update_job(self, job_id: str, updates: Dict[str, Any]) -> None:
        self._col.document(job_id).update(updates)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        doc = self._col.document(job_id).get()
        return doc.to_dict() if doc.exists else None

    def list_jobs(self, tenant_id: str, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = (
            self._col.where("tenantId", "==", tenant_id)
            .where("userId", "==", user_id)
            .order_by("updatedAt", direction="DESCENDING")
            .limit(limit)
        )
        return [d.to_dict() for d in q.stream()]
