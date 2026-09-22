# Review state contract

The configured state path is an index. Store each run's evidence manifest in a
`manifests` directory beside it. Write JSON atomically through a temporary file
and rename it only after the Org pending run exists.

## State index

```json
{
  "version": 1,
  "machine": "personal",
  "host": "machine-name",
  "sources": {
    "codex": {
      "watermark": {
        "timestamp": "2026-09-22T12:00:00Z",
        "session_id": "session",
        "turn_id": "turn",
        "event_id": "event"
      },
      "last_run_id": "run-id"
    }
  },
  "runs": [
    {
      "run_id": "run-id",
      "started_at": "2026-09-22T12:05:00Z",
      "status": "pending",
      "manifest": "manifests/run-id.json"
    }
  ]
}
```

Advance a healthy source only to its latest emitted event after both the Org run
and manifest have been written. A healthy source with no emitted event keeps its
existing watermark. A failed source never advances.

## Run manifest

```json
{
  "version": 1,
  "run_id": "run-id",
  "machine": "personal",
  "started_at": "2026-09-22T12:05:00Z",
  "boundary": {
    "codex": {
      "since": "2026-09-21T12:05:00Z",
      "until": "2026-09-22T12:05:00Z"
    }
  },
  "sources": {
    "codex": {"status": "healthy", "event_count": 4}
  },
  "evidence": [
    {
      "source": "codex",
      "session_id": "session",
      "turn_id": "turn",
      "event_id": "event",
      "timestamp": "2026-09-22T12:00:00Z",
      "sha256": "hash-of-normalised-event"
    }
  ],
  "decisions": []
}
```

Source status is `healthy`, `unavailable`, or `failed`. A failure also records a
privacy-safe error summary. On resolution, append one decision per pending case,
update, and lesson, then set the state-index run status to `complete`.
