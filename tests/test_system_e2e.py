"""
Comprehensive End-to-End (E2E) System Test Suite
================================================
Verifies all 10 architectural layers of the Customer Support Ticket Management System:
 1. Database Schema & Object Verification (Tables, Views, Procedures, Functions, Triggers)
 2. Authentication & Role-Based Access Control (RBAC)
 3. Master Data Services (Categories, Priorities, Statuses)
 4. Customer Module Workflow (Ticket Creation, Comments, View History)
 5. Database Trigger & Audit Automation (History logging, Timestamp recording)
 6. Agent Module Workflow (Queue Triage, Internal Notes privacy, Status update, Resolution)
 7. Admin Module Workflow (Assignment SP execution, Priority escalation, KPI metrics)
 8. Search & Dynamic Multi-Filter Engine
 9. Analytical SQL Reports & RFC-4180 CSV Data Export
10. AI / NLP Component & Frontend Page Routing
"""

import unittest
import json
from backend.app import create_app
from backend.config.db import execute_query

class TestSystemEndToEnd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes the Flask test client."""
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    # -------------------------------------------------------------------------
    # 1. Database Schema & Object Integrity Tests
    # -------------------------------------------------------------------------
    def test_01_database_tables_exist(self):
        """Verifies all 7 core 3NF relational tables exist in MySQL."""
        expected_tables = {
            'users', 'categories', 'priorities', 'ticket_status',
            'tickets', 'ticket_comments', 'ticket_status_history'
        }
        rows = execute_query("SHOW TABLES")
        actual_tables = {list(r.values())[0].lower() for r in rows}
        for table in expected_tables:
            self.assertIn(table, actual_tables, f"Missing table: {table}")

    def test_02_database_views_exist(self):
        """Verifies all 3 operational database views exist."""
        expected_views = {'vw_opentickets', 'vw_agentticketsummary', 'vw_customertickethistory'}
        rows = execute_query("SHOW FULL TABLES WHERE TABLE_TYPE LIKE 'VIEW'")
        actual_views = {list(r.values())[0].lower() for r in rows}
        for view in expected_views:
            self.assertIn(view, actual_views, f"Missing view: {view}")

    def test_03_stored_routines_exist(self):
        """Verifies stored procedures and deterministic functions exist."""
        sp_rows = execute_query("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
        procedures = {r['Name'].lower() for r in sp_rows}
        self.assertIn('sp_createticket', procedures)
        self.assertIn('sp_assignticket', procedures)
        self.assertIn('sp_updateticketstatus', procedures)

        fn_rows = execute_query("SHOW FUNCTION STATUS WHERE Db = DATABASE()")
        functions = {r['Name'].lower() for r in fn_rows}
        self.assertIn('fn_calculateresolutiontime', functions)
        self.assertIn('fn_getslastatus', functions)

    def test_04_database_triggers_exist(self):
        """Verifies audit and SLA timestamp triggers exist."""
        trg_rows = execute_query("SHOW TRIGGERS")
        triggers = {r['Trigger'].lower() for r in trg_rows}
        self.assertIn('trg_ticket_initial_history_log', triggers)
        self.assertIn('trg_ticket_status_resolved_timestamp', triggers)
        self.assertIn('trg_ticket_status_history_log', triggers)

    # -------------------------------------------------------------------------
    # 2. Authentication & RBAC Tests
    # -------------------------------------------------------------------------
    def test_05_auth_login_customer(self):
        """Customer login succeeds and issues session token."""
        res = self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'Password@123'
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['user']['role'], 'customer')

    def test_06_auth_login_invalid_password(self):
        """Invalid credentials return 401 Unauthorized."""
        res = self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'WrongPassword999'
        })
        self.assertEqual(res.status_code, 401)

    def test_07_rbac_customer_forbidden_from_admin(self):
        """Customers cannot access protected admin routes (403 Forbidden)."""
        # Login as customer
        self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'Password@123'
        })
        # Attempt admin action
        res = self.client.get('/api/admin/users')
        self.assertEqual(res.status_code, 403)

    # -------------------------------------------------------------------------
    # 3. Master Data Services
    # -------------------------------------------------------------------------
    def test_08_master_data_endpoints(self):
        """Verifies categories, priorities, and statuses endpoints."""
        res_cat = self.client.get('/api/master/categories')
        self.assertEqual(res_cat.status_code, 200)
        self.assertGreaterEqual(len(res_cat.json['categories']), 6)

        res_prio = self.client.get('/api/master/priorities')
        self.assertEqual(res_prio.status_code, 200)
        self.assertEqual(len(res_prio.json['priorities']), 4)

        res_stat = self.client.get('/api/master/statuses')
        self.assertEqual(res_stat.status_code, 200)
        self.assertEqual(len(res_stat.json['statuses']), 4)

    # -------------------------------------------------------------------------
    # 4. Customer Module & Trigger Verification
    # -------------------------------------------------------------------------
    def test_09_customer_create_ticket_and_trigger(self):
        """Tests ticket creation and verifies trigger trg_Ticket_Initial_History_Log."""
        # Authenticate as customer
        self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'Password@123'
        })

        # Create ticket
        res = self.client.post('/api/customer/tickets', json={
            'subject': 'E2E Automated Test Ticket',
            'category_id': 1,
            'priority_id': 3,
            'description': 'Automated end-to-end integration testing ticket verification.'
        })
        self.assertEqual(res.status_code, 201)
        ticket_data = res.json.get('ticket', {})
        ticket_id = ticket_data.get('ticket_id') or res.json.get('ticket_id')
        self.assertIsNotNone(ticket_id, f"Ticket ID should not be None: {res.json}")

        # Verify trigger automatically inserted row in Ticket_Status_History
        history = execute_query(
            "SELECT * FROM Ticket_Status_History WHERE ticket_id = %s",
            (ticket_id,)
        )
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]['old_status_id'], None)
        self.assertEqual(history[0]['new_status_id'], 1)  # 1 = Open

        # Customer adds comment
        c_res = self.client.post(f'/api/customer/tickets/{ticket_id}/comments', json={
            'comment_text': 'Customer follow-up note in automated test.'
        })
        self.assertEqual(c_res.status_code, 201)

        # Store ticket_id on test class for subsequent agent tests
        TestSystemEndToEnd.created_ticket_id = ticket_id

    # -------------------------------------------------------------------------
    # 5. Agent Module & Privacy Verification
    # -------------------------------------------------------------------------
    def test_10_agent_workflow_and_internal_notes_privacy(self):
        """Tests agent queue, internal notes privacy, and ticket resolution."""
        ticket_id = getattr(TestSystemEndToEnd, 'created_ticket_id', None)
        self.assertIsNotNone(ticket_id, "Ticket ID from previous test missing")

        # 1. Login as Agent Sarah
        self.client.post('/api/auth/login', json={
            'email': 'sarah.agent@support.com',
            'password': 'Password@123'
        })

        # 2. Agent adds private internal note
        note_res = self.client.post(f'/api/agent/tickets/{ticket_id}/comments', json={
            'comment_text': 'Confidential staff note: Hardware diagnostic verified.',
            'is_internal': True
        })
        self.assertEqual(note_res.status_code, 201)

        # 3. Customer logs in and views ticket details
        self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'Password@123'
        })
        cust_view = self.client.get(f'/api/customer/tickets/{ticket_id}')
        self.assertEqual(cust_view.status_code, 200)
        comments = cust_view.json.get('comments', [])
        # Ensure internal note is NOT visible to customer
        for c in comments:
            self.assertNotIn('Confidential staff note', c['comment_text'])

        # 4. Agent logs back in and updates status to In Progress
        self.client.post('/api/auth/login', json={
            'email': 'sarah.agent@support.com',
            'password': 'Password@123'
        })
        stat_res = self.client.put(f'/api/agent/tickets/{ticket_id}/status', json={
            'status_name': 'In Progress'
        })
        self.assertEqual(stat_res.status_code, 200)

        # 5. Agent resolves ticket
        res_res = self.client.post(f'/api/agent/tickets/{ticket_id}/resolve', json={
            'resolution_summary': 'Resolved during automated test suite execution.'
        })
        self.assertEqual(res_res.status_code, 200)

        # 6. Verify trigger trg_Ticket_Status_Resolved_Timestamp populated resolved_at
        ticket_row = execute_query(
            "SELECT status_id, resolved_at FROM Tickets WHERE ticket_id = %s",
            (ticket_id,)
        )
        self.assertEqual(ticket_row[0]['status_id'], 3)  # 3 = Resolved
        self.assertIsNotNone(ticket_row[0]['resolved_at'])

    # -------------------------------------------------------------------------
    # 6. Admin Module & Stored Procedure Verification
    # -------------------------------------------------------------------------
    def test_11_admin_assignment_and_dashboard_stats(self):
        """Verifies admin ticket assignment and live dashboard analytics."""
        ticket_id = getattr(TestSystemEndToEnd, 'created_ticket_id', None)

        # Login as Admin
        self.client.post('/api/auth/login', json={
            'email': 'admin@support.com',
            'password': 'Password@123'
        })

        # Reassign ticket using stored procedure sp_AssignTicket
        assign_res = self.client.post(f'/api/admin/tickets/{ticket_id}/assign', json={
            'agent_id': 3  # John Davis
        })
        self.assertEqual(assign_res.status_code, 200)

        # Verify in database
        t_row = execute_query("SELECT assigned_agent_id FROM Tickets WHERE ticket_id = %s", (ticket_id,))
        self.assertEqual(t_row[0]['assigned_agent_id'], 3)

        # Check Dashboard stats
        dash_res = self.client.get('/api/dashboard/stats')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn('kpis', dash_res.json)
        self.assertIn('charts', dash_res.json)

    # -------------------------------------------------------------------------
    # 7. Search & Filter Engine
    # -------------------------------------------------------------------------
    def test_12_search_and_filtering(self):
        """Tests full-text search and multi-criteria filters."""
        self.client.post('/api/auth/login', json={
            'email': 'admin@support.com',
            'password': 'Password@123'
        })

        # Search by subject keyword
        res_q = self.client.get('/api/search/tickets?q=monitor')
        self.assertEqual(res_q.status_code, 200)
        self.assertIsInstance(res_q.json.get('tickets'), list)

        # Filter by priority
        res_prio = self.client.get('/api/search/tickets?priority=Critical')
        self.assertEqual(res_prio.status_code, 200)

    # -------------------------------------------------------------------------
    # 8. Analytical Reports & Dynamic CSV Export
    # -------------------------------------------------------------------------
    def test_13_reports_and_csv_export(self):
        """Tests all 5 analytical report endpoints and CSV export."""
        self.client.post('/api/auth/login', json={
            'email': 'admin@support.com',
            'password': 'Password@123'
        })

        endpoints = [
            '/api/reports/category',
            '/api/reports/status',
            '/api/reports/priority',
            '/api/reports/agents',
            '/api/reports/resolution-time'
        ]
        for ep in endpoints:
            r = self.client.get(ep)
            self.assertEqual(r.status_code, 200, f"Failed on {ep}")

        # Test CSV export
        csv_res = self.client.get('/api/reports/export?type=category')
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn('text/csv', csv_res.headers.get('Content-Type'))
        self.assertIn('attachment', csv_res.headers.get('Content-Disposition'))

    # -------------------------------------------------------------------------
    # 9. AI Component Inference & DB Mapping
    # -------------------------------------------------------------------------
    def test_14_ai_prediction_and_foreign_key_mapping(self):
        """Tests local ML inference and dynamic database entity resolution."""
        # Check metadata
        info_res = self.client.get('/api/ai/model-info')
        self.assertEqual(info_res.status_code, 200)
        self.assertIn('Multinomial Naive Bayes', info_res.json['model_info']['algorithm'])

        # Predict Hardware inquiry
        hw_res = self.client.post('/api/ai/predict-category', json={
            'text': 'External monitor screen is black and hdmi cable has no signal'
        })
        self.assertEqual(hw_res.status_code, 200)
        self.assertEqual(hw_res.json['category_name'], 'Hardware')
        self.assertEqual(hw_res.json['category_id'], 1)

        # Predict Account inquiry
        acc_res = self.client.post('/api/ai/predict-category', json={
            'text': 'Locked out of active directory after multiple failed password attempts'
        })
        self.assertEqual(acc_res.status_code, 200)
        self.assertEqual(acc_res.json['category_name'], 'Account')
        self.assertEqual(acc_res.json['category_id'], 4)

    # -------------------------------------------------------------------------
    # 10. Frontend Static Page Delivery
    # -------------------------------------------------------------------------
    def test_15_frontend_page_routing(self):
        """Verifies all HTML frontend portals are served correctly."""
        pages = [
            '/',
            '/login.html',
            '/customer_portal.html',
            '/agent_portal.html',
            '/admin_dashboard.html',
            '/reports.html'
        ]
        for page in pages:
            res = self.client.get(page)
            self.assertEqual(res.status_code, 200, f"Failed to serve {page}")
            self.assertGreater(len(res.data), 1000, f"Page {page} is unexpectedly empty")

if __name__ == '__main__':
    unittest.main(verbosity=2)
