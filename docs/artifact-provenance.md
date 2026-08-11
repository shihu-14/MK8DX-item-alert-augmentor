# Artifact Provenance

## Current Status

| Artifact | Known source | Redistribution status |
| --- | --- | --- |
| Promoted item checkpoint | Local Item_Detection.v9 training notes | Unconfirmed; do not publish |
| Promoted gate checkpoint | Local Face-Detection.v5 training notes | Unconfirmed; do not publish |
| Six alert PNG files | Present in repository before refactor | Source and permission unknown |
| Gameplay datasets and videos | Local and not tracked | Source/permission metadata absent |
| YOLOv8n base checkpoint | Ultralytics upstream name recorded | Review upstream terms before redistribution |

GitHub Release `models-v1` is a planned distribution location, not a published
release. `models/manifest.toml` intentionally leaves URLs empty.

Before publication, record artifact creator/source, dataset source and consent,
upstream model/version/license, modifications, intended audience, and explicit
redistribution authorization. Project ownership must also choose a repository
license; this refactor does not make that legal decision.
