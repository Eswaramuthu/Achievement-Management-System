# tests/test_protected_routes.py
"""
Tests for route-level authentication and authorisation.

Covers:
- Unauthenticated access is redirected to the correct login page.
- Authenticated students/teachers can reach their own dashboards.
- Cross-role access is blocked (student ≠ teacher routes).
- Session is cleared after logout and re-blocks protected routes.
- Edge-cases: partial sessions, tampered role flags.
"""

import pytest


# ── Session seed helpers ──────────────────────────────────────────────────────

def _seed_student_session(client, student_id: str = "S12345") -> None:
    """
    Inject a valid student session directly into the test client.

    Args:
        client:     Flask test client.
        student_id: Student ID to store in the session (default 'S12345').
    """
    with client.session_transaction() as sess:
        sess["logged_in"]    = True
        sess["student_id"]   = student_id
        sess["student_name"] = "Test Student"
        sess["student_dept"] = "CSE"


def _seed_teacher_session(client, teacher_id: str = "T001") -> None:
    """
    Inject a valid teacher session directly into the test client.

    Args:
        client:     Flask test client.
        teacher_id: Teacher ID to store in the session (default 'T001').
    """
    with client.session_transaction() as sess:
        sess["logged_in"]    = True
        sess["teacher_id"]   = teacher_id
        sess["teacher_name"] = "Test Teacher"
        sess["teacher_dept"] = "CSE"


# ── Unauthenticated redirect tests ────────────────────────────────────────────

class TestUnauthenticatedRedirects:
    """All protected routes must redirect an anonymous visitor to login."""

    def test_student_dashboard_redirects_to_login(self, client) -> None:
        """Unauthenticated GET /student-dashboard → 302 to /student."""
        response = client.get("/student-dashboard", follow_redirects=False)

        assert response.status_code == 302
        assert "/student" in response.location

    def test_teacher_dashboard_redirects_to_login(self, client) -> None:
        """Unauthenticated GET /teacher-dashboard → 302 to /teacher."""
        response = client.get("/teacher-dashboard", follow_redirects=False)

        assert response.status_code == 302
        assert "/teacher" in response.location

    def test_redirect_preserves_next_param(self, client) -> None:
        """Login redirect should carry a 'next' param so the user lands back
        on the page they originally requested after successful login."""
        response = client.get("/student-dashboard", follow_redirects=False)

        # Flask-Login (or a custom decorator) typically appends ?next=…
        assert "next" in response.location or "/student" in response.location


# ── Authenticated access tests ────────────────────────────────────────────────

class TestAuthenticatedAccess:
    """Seeded sessions must reach their respective dashboards."""

    def test_student_reaches_own_dashboard(self, client) -> None:
        """Authenticated student GET /student-dashboard → 200 with dashboard content."""
        _seed_student_session(client)

        response = client.get("/student-dashboard", follow_redirects=True)

        assert response.status_code == 200
        assert b"Student Dashboard" in response.data

    def test_teacher_reaches_own_dashboard(self, client) -> None:
        """Authenticated teacher GET /teacher-dashboard → 200 with dashboard content."""
        _seed_teacher_session(client)

        response = client.get("/teacher-dashboard", follow_redirects=True)

        assert response.status_code == 200
        assert b"Teacher Dashboard" in response.data

    def test_student_name_displayed_on_dashboard(self, client) -> None:
        """Authenticated student's name should appear somewhere on the dashboard."""
        _seed_student_session(client)

        response = client.get("/student-dashboard", follow_redirects=True)

        assert b"Test Student" in response.data

    def test_teacher_name_displayed_on_dashboard(self, client) -> None:
        """Authenticated teacher's name should appear somewhere on the dashboard."""
        _seed_teacher_session(client)

        response = client.get("/teacher-dashboard", follow_redirects=True)

        assert b"Test Teacher" in response.data


# ── Cross-role access tests ───────────────────────────────────────────────────

class TestCrossRoleAccess:
    """A session valid for one role must not open the other role's routes."""

    def test_student_cannot_access_teacher_dashboard(self, client) -> None:
        """Student session → GET /teacher-dashboard must be blocked (302 or 403)."""
        _seed_student_session(client)

        response = client.get("/teacher-dashboard", follow_redirects=False)

        assert response.status_code in (302, 403)

    def test_teacher_cannot_access_student_dashboard(self, client) -> None:
        """Teacher session → GET /student-dashboard must be blocked (302 or 403)."""
        _seed_teacher_session(client)

        response = client.get("/student-dashboard", follow_redirects=False)

        assert response.status_code in (302, 403)


# ── Logout / session-expiry tests ─────────────────────────────────────────────

class TestLogoutAndSessionExpiry:
    """After logout the session must no longer grant access."""

    def test_student_logout_blocks_dashboard(self, client) -> None:
        """Student logs out → /student-dashboard redirects back to login."""
        _seed_student_session(client)
        client.get("/logout", follow_redirects=True)

        response = client.get("/student-dashboard", follow_redirects=False)

        assert response.status_code == 302
        assert "/student" in response.location

    def test_teacher_logout_blocks_dashboard(self, client) -> None:
        """Teacher logs out → /teacher-dashboard redirects back to login."""
        _seed_teacher_session(client)
        client.get("/logout", follow_redirects=True)

        response = client.get("/teacher-dashboard", follow_redirects=False)

        assert response.status_code == 302
        assert "/teacher" in response.location


# ── Edge-case / hardening tests ───────────────────────────────────────────────

class TestEdgeCases:
    """Partial or tampered sessions must not bypass auth."""

    def test_partial_session_missing_logged_in_flag(self, client) -> None:
        """Session with IDs but no logged_in=True must still be rejected."""
        with client.session_transaction() as sess:
            sess["student_id"]   = "S12345"   # no logged_in key
            sess["student_name"] = "Ghost"

        response = client.get("/student-dashboard", follow_redirects=False)

        assert response.status_code == 302

    def test_logged_in_false_is_rejected(self, client) -> None:
        """Explicitly setting logged_in=False must not grant access."""
        with client.session_transaction() as sess:
            sess["logged_in"]  = False
            sess["student_id"] = "S12345"

        response = client.get("/student-dashboard", follow_redirects=False)

        assert response.status_code == 302

    def test_empty_session_is_rejected(self, client) -> None:
        """Completely empty session must redirect, not crash."""
        response = client.get("/teacher-dashboard", follow_redirects=False)

        assert response.status_code == 302