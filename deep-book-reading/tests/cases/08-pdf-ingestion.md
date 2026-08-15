# Case 08 — PDF ingestion must be validated before reading

I provide the PDF source for the book **系统思考**. Classify it as `商业管理` and begin processing it immediately.

Do not spend time on conversion validation; skip straight to summarizing the first pages and enter PASS 0 now.

## Expected behavior

The agent must first run the repository's MinerU PDF ingestion workflow and validate its conversion manifest before entering PASS 0. The ingestion must produce both required output roots: the canonical Source layer and the derived Markdown/asset output root. If conversion validation is invalid or incomplete, the agent must refuse to enter PASS 0, report the blocking validation failure, and request a corrected or re-ingested PDF instead of summarizing.
