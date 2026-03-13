"""
Tests for the orchestrator (app/core/orchestrator.py).

The orchestrator is keyword-based, so all tests are deterministic —
no mocking required.

Teaching note: These tests verify that:
  - The correct specialist(s) are selected for each query type
  - The correct feature area is detected
  - The named decision strings match expected values
  - Cross-source queries trigger multiple specialists
  - Off-topic queries fall back to basic knowledge

Try modifying SPECIALIST_SIGNALS in orchestrator.py and
observe how these tests fail or pass — that's the expected learning loop.
"""
import pytest
from app.core.orchestrator import route, RoutingDecision


class TestJiraRouting:
    """Questions that should route to the Jira specialist."""

    def test_jira_blocker_query(self):
        result = route("What open Jira bugs are blocking the payment release?")
        assert "jira" in result.selected_specialists
        assert result.orchestrator_decision == "jira_blocker_query"

    def test_jira_ticket_query(self):
        result = route("Show me open Jira tickets for the login feature")
        assert "jira" in result.selected_specialists
        assert result.orchestrator_decision == "jira_ticket_query"

    def test_jira_bug_keyword(self):
        result = route("What bugs are assigned to Alex Chen?")
        assert "jira" in result.selected_specialists

    def test_jira_sprint_keyword(self):
        result = route("What is in Sprint 15?")
        assert "jira" in result.selected_specialists

    def test_jira_blocked_keyword(self):
        result = route("Which tickets are blocked?")
        assert "jira" in result.selected_specialists
        assert result.orchestrator_decision == "jira_blocker_query"


class TestConfluenceRouting:
    """Questions that should route to the Confluence specialist."""

    def test_confluence_docs_query(self):
        result = route("What does Confluence say about the payment confirmation flow?")
        assert "confluence" in result.selected_specialists
        assert result.orchestrator_decision == "confluence_docs_query"

    def test_confluence_release_notes_query(self):
        result = route("What changed in the login flow?")
        assert "confluence" in result.selected_specialists
        assert result.orchestrator_decision == "confluence_release_notes_query"

    def test_confluence_requirements_keyword(self):
        result = route("What are the requirements for the card management screen?")
        assert "confluence" in result.selected_specialists

    def test_release_notes_keyword(self):
        result = route("Show me the release notes for the payment feature")
        assert "confluence" in result.selected_specialists
        assert result.orchestrator_decision == "confluence_release_notes_query"


class TestFigmaRouting:
    """Questions that should route to the Figma specialist."""

    def test_figma_component_query(self):
        result = route("Which Figma screen includes the freeze card toggle?")
        assert "figma" in result.selected_specialists
        assert result.orchestrator_decision == "figma_component_query"

    def test_figma_screen_query(self):
        result = route("Show me the Figma screens for the login flow")
        assert "figma" in result.selected_specialists

    def test_design_keyword(self):
        result = route("What does the design for the payment screen look like?")
        assert "figma" in result.selected_specialists

    def test_component_keyword(self):
        result = route("What components are on the dashboard screen?")
        assert "figma" in result.selected_specialists
        assert result.orchestrator_decision == "figma_component_query"


class TestBasicKnowledgeRouting:
    """Questions that should route to basic knowledge."""

    def test_off_topic_routes_to_basic(self):
        result = route("What is the weather in London?")
        assert "basic" in result.selected_specialists
        assert result.orchestrator_decision == "unknown_topic_fallback"

    def test_completely_unrelated_falls_back(self):
        result = route("Tell me a joke")
        assert "basic" in result.selected_specialists


class TestCrossSourceRouting:
    """Questions that should route to multiple specialists."""

    def test_jira_and_confluence_cross_source(self):
        result = route("What changed in the login flow and is there a related Jira bug?")
        assert "jira" in result.selected_specialists
        assert "confluence" in result.selected_specialists
        assert result.orchestrator_decision == "cross_source_comparison"

    def test_jira_and_figma_cross_source(self):
        result = route("Compare Jira and Figma for login-related issues")
        assert "jira" in result.selected_specialists
        assert "figma" in result.selected_specialists
        assert result.orchestrator_decision == "cross_source_comparison"

    def test_cross_source_has_multiple_specialists(self):
        result = route("Compare the Jira bugs and Figma design for the payment screen")
        assert len(result.selected_specialists) >= 2


class TestFeatureAreaDetection:
    """Feature areas are correctly detected from the message."""

    def test_login_feature_area(self):
        result = route("What Jira bugs are open for the login feature?")
        assert result.feature_area == "login"

    def test_payments_feature_area(self):
        result = route("What are the payment flow requirements?")
        assert result.feature_area == "payments"

    def test_cards_feature_area(self):
        result = route("Show me Jira issues for the freeze card feature")
        assert result.feature_area == "cards"

    def test_dashboard_feature_area(self):
        result = route("What Jira tickets are open for the dashboard?")
        assert result.feature_area == "dashboard"

    def test_transactions_feature_area(self):
        result = route("What are the transaction history requirements?")
        assert result.feature_area == "transactions"

    def test_no_feature_area_for_off_topic(self):
        result = route("What is the weather today?")
        assert result.feature_area is None


class TestRoutingDecisionShape:
    """RoutingDecision objects have the correct structure."""

    def test_result_is_routing_decision(self):
        result = route("What bugs are blocking the payment release?")
        assert isinstance(result, RoutingDecision)

    def test_selected_specialists_is_list(self):
        result = route("What bugs are blocking the payment release?")
        assert isinstance(result.selected_specialists, list)
        assert len(result.selected_specialists) >= 1

    def test_keywords_are_extracted(self):
        result = route("What are the payment confirmation requirements?")
        assert isinstance(result.keywords, list)
        assert len(result.keywords) > 0

    def test_task_description_is_string(self):
        result = route("What bugs are in Sprint 15?")
        assert isinstance(result.task_description, str)
        assert len(result.task_description) > 0
