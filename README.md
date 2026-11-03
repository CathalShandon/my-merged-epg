# Daily XMLTV EPG merger

Combines the public Teleonline compressed XMLTV EPG and your private XMLTV URL into `merged_epg.xml.gz` daily at 04:00 UTC (GitHub schedules may run late).

## Setup

1. Create a **public** GitHub repository, e.g. `my-merged-epg`, with default branch `main`.
2. Upload `merge_epg.py` and `.github/workflows/update-epg.yml` preserving the folder structure. Do **not** upload your private EPG URL anywhere in the repo.
3. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `PRIVATE_EPG_URL` and set its value to the **full second URL you provided**, including its username and password. Do not add quotation marks.
4. Under **Settings → Actions → General → Workflow permissions**, enable **Read and write permissions** if the repository settings require it.
5. Open **Actions → Update merged EPG → Run workflow**. Once the workflow completes, the output will be committed to the `main` branch.
6. Paste this into your IPTV player, replacing the placeholders:

   `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPOSITORY/main/merged_epg.xml.gz`

## Notes

- The public repository exposes the merged TV guide to anyone with the link. It does **not** contain your source credentials unless you mistakenly upload them.
- Both EPGs must be reachable from GitHub-hosted runners. If one is unavailable, the workflow fails and keeps the previously published file.
- Duplicate channel IDs use the first source's channel details. Duplicate programmes are identified by channel ID, start time, stop time, and title. Different IDs for the same channel are **not** automatically matched; your IPTV player must map the correct XMLTV IDs.
- GitHub scheduled runs can be delayed or disabled after extended repository inactivity. Run manually to verify updates.
- Large XMLTV files may exceed GitHub's practical file size limits or the runner's memory. The script is designed for ordinary-sized guides.
- To rotate your private EPG credentials, update the `PRIVATE_EPG_URL` secret.
