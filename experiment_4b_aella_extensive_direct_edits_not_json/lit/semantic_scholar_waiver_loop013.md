# Semantic Scholar Access Waiver Request — Loop 019
Date: 2025-11-08
Status: draft (pending partner approval)

## Summary
Since Loop 008 the dedicated Semantic Scholar key stored in `.env` has rejected every authenticated `paper/search` request with HTTP 403. Each attempt complied with the 1 req/sec policy via `scripts/semantic_scholar_cli.py`, logged inputs/outputs under `lit/queries/loop_{loop}/`, and was referenced in `analysis/decision_log.csv`. We now have ≥12 consecutive failures paired with fallback DOI-backed evidence from CrossRef (Ross et al., 2019; Pandya, 2017; Turrisi et al., 2010; Larkin et al., 2024 preprint; Qu, 2024; Renu, 2023; Hulvershorn et al., 2009; Loecher et al., 2023; Merrill & Salazar, 2002; Eliassen, 2013) to keep the literature plan moving. To unblock PAP freeze we request a temporary waiver acknowledging these logged failures while ops works with Semantic Scholar support to restore the key.

## Attempt Log (Loops 008–018)
| Loop | Timestamp (UTC) | Query | Status | Artifact |
| --- | --- | --- | --- | --- |
| 008 | 2025-11-08T14:10:07Z | "childhood abuse self love adult wellbeing" | 403 Forbidden | `lit/queries/loop_008/query_001.json` |
| 009 | 2025-11-08T14:19:14Z | "childhood emotional abuse adult self love wellbeing" | 403 Forbidden | `lit/queries/loop_009/query_001.json` |
| 010 | 2025-11-08T14:27:55Z | "childhood abuse adult self love resilience wellbeing" | 403 Forbidden | `lit/queries/loop_010/query_001.json` |
| 011 | 2025-11-08T14:46:00Z | "childhood abuse self love adult wellbeing" | 403 Forbidden | `lit/queries/loop_011/query_001.json` |
| 012 | 2025-11-08T14:39:16Z | "childhood resilience religious adherence depression" | 403 Forbidden | `lit/queries/loop_012/query_001.json` |
| 013 | 2025-11-08T15:06:30Z | "childhood resilience spiritual support adult depression" | 403 Forbidden | `lit/queries/loop_013/query_001.json` |
| 014 | 2025-11-08T15:02:53Z | "childhood spirituality parental support adult depression" | 403 Forbidden | `lit/queries/loop_014/query_001.json` |
| 015 | 2025-11-08T15:11:56Z | "childhood parental guidance adult health" | 403 Forbidden | `lit/queries/loop_015/query_001.json` |
| 016 | 2025-11-08T15:36:56Z | "childhood emotional neglect adult self compassion" | 403 Forbidden | `lit/queries/loop_016/query_001.json` |
| 017 | 2025-11-08T16:57:20Z | "childhood religious participation adult depression support" | 403 Forbidden | `lit/queries/loop_017/query_001.json` |
| 018 | 2025-11-08T17:05:49Z | "childhood church attendance adult mental health support" | 403 Forbidden | `lit/queries/loop_018/query_001.json` |
| 019 | 2025-11-08T17:14:50Z | "childhood faith community adult resilience depression" | 403 Forbidden | `lit/queries/loop_019/query_001.json` |
| 020 | 2025-11-08T17:25:02Z | "childhood spiritual involvement adult depressive symptoms social support" | 403 Forbidden | `lit/queries/loop_020/query_001.json` |

_All JSON payloads include the endpoint, query params, and Semantic Scholar error body for reproducibility._

## Fallback Evidence & Bibliography Updates
- **Ross et al. (2019), DOI `10.1016/j.chiabu.2019.03.016`** — CrossRef metadata captured in `lit/queries/loop_012/crossref_query_001.json` and propagated to `lit/evidence_map.csv` / `lit/bibliography.bib`. Supports H3 by documenting self-compassion as a mediator between childhood maltreatment and adult depressive symptoms/self-worth.
- Existing DOI-backed sources for H1–H2 (Ezra et al., 2025; Thompson et al., 2015) and H3 (Islam et al., 2022) remain current and are cited with claim IDs `C1–C3`.
- **Pandya (2017), DOI `10.1080/15332985.2016.1222982`** — Captured via CrossRef (loop 014) to document spirituality/social-support interventions linked to childhood depression, reinforcing the H1 religiosity mechanism narrative.
- **Turrisi et al. (2010), DOI `10.7312/guil14080-006`** — Captured via CrossRef (loop 015) showing parental monitoring suppresses high-risk drinking among young adults; strengthens the H2 guidance→health justification while the S2 credential remains down.
- **Larkin et al. (2024 preprint), DOI `10.2139/ssrn.4703219`** — Captured via CrossRef (loop 016) linking morally injurious events and childhood emotional abuse/neglect to self-compassion deficits in civilian adults, bolstering H3’s mediator plan despite the S2 outage.
- **Qu (2024), DOI `10.1016/j.chiabu.2024.107020`** — Captured via CrossRef (loop 016) detailing how self-compassion and rejection sensitivity mediate emotional-abuse effects on loneliness; reinforces the planned mediator controls for H3 even though the sample is adolescent-focused.
- **Renu (2023), DOI `10.21275/SR23621004642`** — Captured via CrossRef (loop 016) summarizing how childhood trauma severity predicts adult depressive/self-worth outcomes, providing theory support for H3 while peer-reviewed sources continue to accumulate.
- **Hulvershorn et al. (2009), DOI `10.1093/med:psych/9780195332711.003.0004`** — Captured via CrossRef (loop 016) synthesizing how childhood mental health issues propagate into young adult outcomes, reinforcing the PAP’s planned control strategy.
- **Loecher et al. (2023), DOI `10.1089/jayao.2022.0097`** — Captured via CrossRef (loop 017) showing how ongoing parental engagement affects adolescent/young adult cancer survivors’ health-care transitions, strengthening H2’s evidence base while S2 access is blocked.
- **Merrill & Salazar (2002), DOI `10.1080/13674670110059569`** — Captured via CrossRef (loop 018) documenting how regular church attendance correlates with better adult mental health among Mormon and non-Mormon Utah residents, reinforcing H1's religiosity-support mechanism during the outage.
- **Eliassen (2013), DOI `10.1007/s13644-013-0110-9`** — Captured via CrossRef (loop 019) showing that weekly pre-teen religious attendance coupled with high stress exposure predicts lower young-adult depression through religious coping, strengthening H1's mechanism narrative while the S2 outage persists.
- **Kasen et al. (2014), DOI `10.1002/da.22131`** — Captured via CrossRef (loop 020) documenting that greater religiosity predicts improved psychosocial functioning among high-risk young adults, bolstering H1’s stress-buffering argument until Semantic Scholar access is restored.
- **Eliassen (2013), DOI `10.1007/s13644-013-0110-9`** — Captured via CrossRef (loop 019) showing that weekly pre-teen religious attendance coupled with high stress exposure predicts lower young-adult depression through religious coping, strengthening H1's mechanism narrative while the S2 outage persists.

## Request
1. **Waiver:** Allow continuation through PAP freeze relying on the documented CrossRef DOIs while Semantic Scholar restores API access. The attempt log above, paired with decision-log entries, demonstrates due diligence.
2. **Remediation Plan:**
   - Open support ticket with Semantic Scholar (ref: API key ending `***7d`).
   - Once access is restored, replay the queued queries (loop 008 onward) to confirm parity and add any newly returned papers to the evidence map/bibliography.
   - Update `analysis/decision_log.csv` and this memo with the resolution timestamp, then close backlog item N1 (query execution) and mark this waiver as satisfied.

## Contacts & Next Steps
- Owner: Research agent (this experiment)
- Dependencies: Ops team for API credential refresh
- Blocking artifacts: PAP freeze (status=draft) and confirmatory analyses until either a working key or an approved waiver is recorded in `artifacts/state.json` per governance rules.
