# Findings on Experiment 4A Action Log

## How it's doing
- The PAP freeze entry captures the exact reruns, seeds, and public artifacts for the confirmatory H1 contrasts, so anyone can replay Loop 006 without guesswork (`analysis/decision_log.csv:22`).
- Loop 011 extends the log with the multinomial benchmark plus paired literature pulls, showing that modeling, documentation, and sourcing are moving together as the project readies H3 for promotion decisions (`analysis/decision_log.csv:29`).
- Confirmatory evidence is actually recorded: the male-vulnerability slope keeps its sign and passes BH control with q=5.8e-11, giving reviewers a concrete anchor back to the logged loop (`analysis/results.csv:21`).
- The sensitivity notebook already reports executed HC3/expanded-control reruns and queues the next bootstrap + anxiety-coding wave, so the action log is tied to a living robustness roadmap rather than ad-hoc notes (`analysis/sensitivity_notes.md:1`, `analysis/sensitivity_notes.md:20`).
- The manuscript mirrors the log by flagging the PAP-freeze status and stating that H2–H4 stay exploratory until they hit the promotion bar, keeping downstream readers aligned with the recorded actions (`reports/paper.md:1`, `reports/paper.md:6`).

## What could be better
- Each substantive loop is followed by an auto-log entry and even a few out-of-order duplicates (e.g., the second Loop 003 entry), which makes the CSV noisy and harder to audit quickly (`analysis/decision_log.csv:4`, `analysis/decision_log.csv:5`, `analysis/decision_log.csv:18`).
- Despite several measurement and literature loops, H2 and H4 still appear only as exploratory rows with `confirmatory=FALSE`, and the manuscript reiterates that they are not promoted yet—consider defining the evidence bar and logging concrete promotion tasks before more diagnostics (`analysis/results.csv:2`, `reports/paper.md:6`).
- The self-love construct flagged with α=0.42 is still slated for confirmatory use without any remediation plan logged, so reliability concerns could undercut H2 the moment it advances (`reports/paper.md:15`).
- The next robustness wave (bootstrap draws + alternative anxiety codings) exists only as a planning section, so it would help to schedule those as upcoming loops or tickets to avoid them stalling (`analysis/sensitivity_notes.md:20`).

## What's surprising
- Childhood class only becomes significant at the ≥$10M cutpoint in the partial proportional-odds run, implying extremely tail-heavy effects rather than a smooth gradient across wealth tiers (`analysis/results.csv:29`).
- Even after constructing and running the multinomial benchmark, the average marginal effect for the top category rounds to zero, reinforcing the counterintuitive lesson that a far more flexible model can still agree with the constrained PPO spec about null average impacts (`analysis/results.csv:30`).
- The HC3 sensitivity loop leaves the guidance-buffering slope almost unchanged at 0.068 with q≈4.5e-15, which is unusually stable for a moderation effect in a noisy observational setting (`analysis/results.csv:22`).
