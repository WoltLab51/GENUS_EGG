from __future__ import annotations

from html import escape

from genus_egg.cockpit.cockpit_snapshot import CockpitSnapshot


class CockpitHtmlRenderer:
    def render(self, snapshot: CockpitSnapshot) -> str:
        rows = [
            ("Memories", snapshot.memory_count),
            ("Ledger Entries", snapshot.ledger_entry_count),
            ("Habitat Manifests", snapshot.habitat_manifest_count),
            ("Resource Snapshots", snapshot.resource_snapshot_count),
            ("Habitat Readiness Reports", snapshot.habitat_readiness_report_count),
            ("Reaction Outcomes", snapshot.reaction_outcome_count),
            ("Observations", snapshot.observation_count),
            ("Capability Needs", snapshot.capability_need_count),
            ("Capability Proposals", snapshot.capability_proposal_count),
            ("Code Change Proposals", snapshot.code_change_proposal_count),
            ("Shadow Plans", snapshot.shadow_plan_count),
            ("Fitness Evaluations", snapshot.fitness_evaluation_count),
            ("Patch Approvals", snapshot.patch_approval_count),
            ("Sandbox Patches", snapshot.sandbox_patch_count),
            ("Test Runs", snapshot.test_run_count),
            ("Evidence Records", snapshot.evidence_record_count),
            ("Evidence Chains", snapshot.evidence_chain_count),
            ("Git Status Reports", snapshot.git_status_count),
            ("Git Preparations", snapshot.git_preparation_count),
            ("GitHub Draft PRs", snapshot.github_draft_pr_count),
            ("Activation Requests", snapshot.activation_request_count),
            ("Activation Decisions", snapshot.activation_decision_count),
        ]
        table_rows = "\n".join(
            f"<tr><th>{escape(label)}</th><td>{value}</td></tr>"
            for label, value in rows
        )
        latest_habitat = escape(snapshot.latest_habitat_id or "none")
        latest_score = (
            str(snapshot.latest_fitness_score)
            if snapshot.latest_fitness_score is not None
            else "none"
        )
        activation = escape(snapshot.activation_state)
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>GENUS EGG Inspection Cockpit</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1f2937; }}
    main {{ max-width: 920px; margin: 0 auto; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #d1d5db; padding: 0.65rem; text-align: left; }}
    .boundary {{ margin-top: 1.5rem; padding: 1rem; border: 1px solid #d1d5db; }}
  </style>
</head>
<body>
  <main>
    <h1>GENUS EGG Inspection Cockpit</h1>
    <table>
      {table_rows}
    </table>
    <section class="boundary">
      <p>Latest Habitat: {latest_habitat}</p>
      <p>Latest Fitness Score: {latest_score}</p>
      <p>Activation: {activation}</p>
      <p>Mode: read-only</p>
    </section>
  </main>
</body>
</html>
"""
