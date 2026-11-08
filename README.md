# NerChat Element Call

## Purpose

Publish the official stable Element Call frontend at `https://meet.neboer.site`
using Tencent EdgeOne Pages mainland hosting. Existing NerChat accounts only;
this project does not enable registration or guest accounts.

## Resources

`scripts/prepare.py` downloads the official full release archive and verifies
the GitHub SHA-256 digest before extracting regular files and applying `overlay/`.
LiveKit discovery belongs to the homeserver and Element Web well-known response.
Do not hardcode a debug LiveKit backend in the Call frontend config.

## Dependencies

Python 3.10+, Node.js 22, authenticated GitHub CLI, and the pinned npm dependencies.
Backend deployment and client acceptance are tracked in the USCluster research
and GitOps repository. Standalone frontend availability alone does not prove
Element Web / Element X media connectivity.

## Operations

Run `python scripts/prepare.py` to prepare the verified artifact in `dist/`.
The frontend allows framing by `chat.neboer.site`. Dynamic entrypoints bypass
edge caching. Never commit provider tokens or private keys.

Tencent project: `makers-jupdznz3xnv9` (`nerchat-element-call`, mainland).
Source repository: https://github.com/UntilSoftwareDevs/NerChatElementCallAutoUpdate

GitHub Actions checks stable releases daily at 03:43 Asia/Shanghai. It verifies
the artifact, deploys and checks preview, then production, and records only a
verified deployment. `workflow_dispatch` forces redeployment. The first empty
Tencent project requires a production upload before preview exists; this bootstrap
was performed separately. Automatic rollback is not performed.

`EDGEONE_API_TOKEN` is a GitHub Actions secret. The production check uses the
custom domain; temporary platform domains have separate access authorization.

## Claims

Domain and cloud ownership are tracked in
[us1-gitops/claim](https://github.com/UntilSoftwareDevs/us1-gitops/tree/main/claim),
including `site/meet.neboer.site.md`, `dns/neboer.site/website/meet.neboer.site.md`
and `external/nerchat-element-call-pages.md`.
The existing Element Web frontend remains a separate project.
