from app.services.policy_retrieval import retrieve_policies


def test_retrieval_ranks_mechanical_policy() -> None:
    policies = retrieve_policies("The cooling pump is vibrating near the rear seal.")
    policy_ids = [policy.policy_id for policy in policies]

    assert "POL-MECH-001" in policy_ids


def test_retrieval_falls_back_to_general_policy() -> None:
    policies = retrieve_policies("A maintenance request with no recognizable asset terms.")

    assert policies
    assert policies[0].policy_id == "POL-GEN-006"
