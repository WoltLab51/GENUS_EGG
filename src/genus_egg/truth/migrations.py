from __future__ import annotations

import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_inputs (
    input_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meaning_candidates (
    meaning_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_input_id TEXT NOT NULL,
    intent TEXT NOT NULL,
    content TEXT,
    interpretation_confidence TEXT NOT NULL,
    needs_clarification INTEGER NOT NULL,
    adapter_version TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_results (
    validation_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_meaning_id TEXT NOT NULL,
    result TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reactions (
    reaction_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    source_validation_id TEXT,
    reaction_type TEXT NOT NULL,
    context TEXT NOT NULL,
    reaction_state TEXT NOT NULL,
    resolver_mode TEXT NOT NULL,
    cube_coord INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reaction_products (
    product_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    produced_by_reaction_id TEXT NOT NULL,
    product_type TEXT NOT NULL,
    continuation_policy TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_objects (
    memory_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    memory_state TEXT NOT NULL,
    source_product_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ledger_entries (
    ledger_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    step INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_kind TEXT,
    target_id TEXT,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habitat_manifest (
    habitat_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL,
    hostname TEXT NOT NULL,
    os_name TEXT NOT NULL,
    python_version TEXT NOT NULL,
    repo_path TEXT,
    data_path TEXT NOT NULL,
    sqlite_path TEXT NOT NULL,
    network_allowed INTEGER NOT NULL,
    git_available INTEGER NOT NULL,
    github_allowed INTEGER NOT NULL,
    model_access TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    habitat_id TEXT NOT NULL,
    cpu_count INTEGER,
    cpu_label TEXT NOT NULL,
    memory_total_mb INTEGER,
    memory_available_mb INTEGER,
    disk_total_mb INTEGER NOT NULL,
    disk_free_mb INTEGER NOT NULL,
    temperature_celsius REAL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habitat_readiness_reports (
    report_id TEXT PRIMARY KEY,
    habitat_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    checks_json TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reaction_outcomes (
    outcome_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    final_status TEXT NOT NULL,
    final_product_type TEXT,
    success INTEGER NOT NULL,
    reason_code TEXT,
    duration_ms INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS observation_records (
    observation_id TEXT PRIMARY KEY,
    chain_id TEXT NOT NULL,
    observation_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capability_needs (
    need_id TEXT PRIMARY KEY,
    source_observation_id TEXT,
    need_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capability_proposals (
    proposal_id TEXT PRIMARY KEY,
    need_id TEXT NOT NULL,
    proposal_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS code_change_proposals (
    code_proposal_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    title TEXT NOT NULL,
    rationale TEXT NOT NULL,
    allowed_paths_json TEXT NOT NULL,
    forbidden_paths_json TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shadow_test_plans (
    shadow_plan_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    status TEXT NOT NULL,
    planned_checks_json TEXT NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fitness_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    shadow_plan_id TEXT NOT NULL,
    score INTEGER NOT NULL,
    criteria_scores_json TEXT NOT NULL,
    rationale TEXT NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patch_approvals (
    approval_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    approved_by TEXT NOT NULL,
    approval_scope TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patch_risk_assessments (
    risk_assessment_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    rationale TEXT NOT NULL,
    blocked INTEGER NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sandbox_patches (
    patch_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    approval_id TEXT NOT NULL,
    risk_assessment_id TEXT NOT NULL,
    status TEXT NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS patch_file_changes (
    file_change_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    target_path TEXT NOT NULL,
    change_type TEXT NOT NULL,
    content_preview TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_runs (
    test_run_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    command_name TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_results (
    test_result_id TEXT PRIMARY KEY,
    test_run_id TEXT NOT NULL,
    result TEXT NOT NULL,
    passed INTEGER NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_records (
    evidence_id TEXT PRIMARY KEY,
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    code_proposal_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_chains (
    evidence_chain_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    evidence_ids_json TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS git_status_reports (
    git_status_id TEXT PRIMARY KEY,
    repo_path TEXT NOT NULL,
    current_branch TEXT,
    head_commit TEXT,
    dirty INTEGER NOT NULL,
    remotes_json TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS git_branch_preparations (
    git_preparation_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    status TEXT NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS github_draft_prs (
    github_draft_pr_id TEXT PRIMARY KEY,
    patch_id TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    repository TEXT NOT NULL,
    status TEXT NOT NULL,
    is_draft INTEGER NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activation_requests (
    activation_request_id TEXT PRIMARY KEY,
    code_proposal_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    activation TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activation_decisions (
    activation_decision_id TEXT PRIMARY KEY,
    activation_request_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    status TEXT NOT NULL,
    activation TEXT NOT NULL,
    rationale TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reaction_spec_candidates (
    candidate_id TEXT PRIMARY KEY,
    activation_request_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_compatibility_checks (
    compatibility_check_id TEXT PRIMARY KEY,
    activation_request_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
"""


def apply_migrations(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()
