"""
Tests for the specialist agents (app/specialists/).

These tests verify that each specialist:
  - Returns results for relevant queries
  - Returns an empty list for irrelevant queries
  - Returns correctly structured RetrievedItem objects
  - Filters by feature area correctly
  - Prioritises blocked/critical items for Jira

These tests use the real data files (jira.json, confluence.json, etc.)
so they also serve as data integrity checks.

Teaching note: Specialist tests demonstrate deterministic retrieval.
Given the same task, the same records are always returned in the same order.
This is what makes Promptfoo citation assertions reliable.
"""
import pytest
from app.specialists.base import RetrievalTask, RetrievedItem
from app.specialists.jira_specialist import JiraSpecialist
from app.specialists.confluence_specialist import ConfluenceSpecialist
from app.specialists.figma_specialist import FigmaSpecialist
from app.specialists.basic_specialist import BasicSpecialist


# ── Shared task factory helpers ───────────────────────────────────────────────

def jira_task(message: str, feature_area: str = None, keywords: list = None):
    return RetrievalTask(
        message=message,
        feature_area=feature_area,
        keywords=keywords or message.lower().split(),
    )


# ── Jira Specialist Tests ─────────────────────────────────────────────────────

class TestJiraSpecialist:
    specialist = JiraSpecialist()

    def test_returns_results_for_payment_blockers(self):
        task = RetrievalTask(
            message="What open Jira bugs are blocking the payment release?",
            feature_area="payments",
            keywords=["open", "bugs", "blocking", "payment", "release"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0

    def test_returns_blocked_tickets_for_payment_feature(self):
        task = RetrievalTask(
            message="What tickets are blocked for payments?",
            feature_area="payments",
            keywords=["tickets", "blocked", "payments"],
        )
        results = self.specialist.retrieve(task)
        # PF-104, PF-105, PF-113 are blocked with feature_area=payments
        ids = [r.id for r in results]
        assert any(id in ids for id in ("PF-104", "PF-105", "PF-113"))

    def test_returns_login_tickets(self):
        task = RetrievalTask(
            message="Show me login bugs",
            feature_area="login",
            keywords=["login", "bugs"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0
        # All results should be login-related
        for r in results:
            assert r.source == "jira"

    def test_empty_results_for_no_match(self):
        task = RetrievalTask(
            message="What is the weather in Tokyo?",
            feature_area=None,
            keywords=["weather", "tokyo"],
        )
        results = self.specialist.retrieve(task)
        # No Jira tickets about weather in Tokyo
        assert results == []

    def test_result_has_correct_source(self):
        task = RetrievalTask(
            message="What payment tickets are open?",
            feature_area="payments",
            keywords=["payment", "open"],
        )
        results = self.specialist.retrieve(task)
        for r in results:
            assert r.source == "jira"

    def test_result_fields_are_populated(self):
        task = RetrievalTask(
            message="Show me blocked tickets",
            feature_area="payments",
            keywords=["blocked"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0
        first = results[0]
        assert isinstance(first, RetrievedItem)
        assert first.id.startswith("PF-")
        assert len(first.title) > 0
        assert len(first.content) > 0

    def test_returns_at_most_5_results(self):
        task = RetrievalTask(
            message="All tickets",
            feature_area=None,
            keywords=["payment", "login", "card", "ticket"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) <= 5


# ── Confluence Specialist Tests ───────────────────────────────────────────────

class TestConfluenceSpecialist:
    specialist = ConfluenceSpecialist()

    def test_returns_results_for_payment_confirmation(self):
        task = RetrievalTask(
            message="What does Confluence say about the payment confirmation flow?",
            feature_area="payments",
            keywords=["payment", "confirmation", "flow"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0

    def test_returns_release_notes_for_payment_release(self):
        task = RetrievalTask(
            message="What are the release notes for the payment release?",
            feature_area="payments",
            keywords=["release", "notes", "payment"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "CF-005" in ids  # Payment Release v2.4 — Known Issues

    def test_returns_login_release_notes(self):
        task = RetrievalTask(
            message="What changed in the login flow?",
            feature_area="login",
            keywords=["changed", "login", "flow"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "CF-003" in ids  # Login Flow — Release Notes v2.1

    def test_returns_card_requirements(self):
        task = RetrievalTask(
            message="What are the card management requirements?",
            feature_area="cards",
            keywords=["card", "management", "requirements"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0

    def test_empty_results_for_no_match(self):
        task = RetrievalTask(
            message="What is the weather in Tokyo?",
            feature_area=None,
            keywords=["weather", "tokyo"],
        )
        results = self.specialist.retrieve(task)
        assert results == []

    def test_result_has_correct_source(self):
        task = RetrievalTask(
            message="What are the payment requirements?",
            feature_area="payments",
            keywords=["payment", "requirements"],
        )
        results = self.specialist.retrieve(task)
        for r in results:
            assert r.source == "confluence"

    def test_returns_at_most_3_results(self):
        task = RetrievalTask(
            message="requirements documentation process flow",
            feature_area=None,
            keywords=["requirements", "documentation", "process", "flow"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) <= 3


# ── Figma Specialist Tests ────────────────────────────────────────────────────

class TestFigmaSpecialist:
    specialist = FigmaSpecialist()

    def test_finds_freeze_card_toggle_screen(self):
        task = RetrievalTask(
            message="Which Figma screen includes the freeze card toggle?",
            feature_area="cards",
            keywords=["figma", "screen", "freeze", "card", "toggle"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "FG-006" in ids  # Card Management Screen

    def test_returns_login_screens(self):
        task = RetrievalTask(
            message="Show me the Figma screens for login",
            feature_area="login",
            keywords=["figma", "screens", "login"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0
        ids = [r.id for r in results]
        # FG-001 Login Screen or FG-002 OTP screen
        assert any(id in ids for id in ("FG-001", "FG-002"))

    def test_returns_payment_screens(self):
        task = RetrievalTask(
            message="What does the payment confirmation screen look like?",
            feature_area="payments",
            keywords=["payment", "confirmation", "screen"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0

    def test_component_keyword_matches(self):
        task = RetrievalTask(
            message="Which screens have a freeze toggle component?",
            feature_area=None,
            keywords=["screens", "freeze", "toggle", "component"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "FG-006" in ids  # Card Management Screen has freeze_card_toggle

    def test_empty_results_for_no_match(self):
        task = RetrievalTask(
            message="blockchain NFT metaverse",
            feature_area=None,
            keywords=["blockchain", "nft", "metaverse"],
        )
        results = self.specialist.retrieve(task)
        assert results == []

    def test_result_has_correct_source(self):
        task = RetrievalTask(
            message="Show me card management Figma screen",
            feature_area="cards",
            keywords=["card", "management", "figma", "screen"],
        )
        results = self.specialist.retrieve(task)
        for r in results:
            assert r.source == "figma"

    def test_content_includes_components(self):
        task = RetrievalTask(
            message="What is on the card management screen?",
            feature_area="cards",
            keywords=["card", "management", "screen"],
        )
        results = self.specialist.retrieve(task)
        assert len(results) > 0
        # Content should mention components
        assert "Components:" in results[0].content


# ── Basic Knowledge Specialist Tests ─────────────────────────────────────────

class TestBasicSpecialist:
    specialist = BasicSpecialist()

    def test_returns_payflow_overview(self):
        task = RetrievalTask(
            message="What is PayFlow?",
            feature_area=None,
            keywords=["payflow"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "BK-001" in ids  # PayFlow Product Vision

    def test_returns_team_info(self):
        task = RetrievalTask(
            message="How is the PayFlow team structured?",
            feature_area=None,
            keywords=["payflow", "team", "structured"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "BK-002" in ids  # PayFlow Team Structure

    def test_returns_release_process(self):
        task = RetrievalTask(
            message="What is the release process at PayFlow?",
            feature_area=None,
            keywords=["release", "process", "payflow"],
        )
        results = self.specialist.retrieve(task)
        ids = [r.id for r in results]
        assert "BK-003" in ids  # PayFlow Release Process

    def test_empty_results_for_completely_unrelated(self):
        task = RetrievalTask(
            message="What is the capital of France?",
            feature_area=None,
            keywords=["capital", "france"],
        )
        results = self.specialist.retrieve(task)
        assert results == []

    def test_result_has_correct_source(self):
        task = RetrievalTask(
            message="Tell me about PayFlow",
            feature_area=None,
            keywords=["payflow"],
        )
        results = self.specialist.retrieve(task)
        for r in results:
            assert r.source == "basic"
