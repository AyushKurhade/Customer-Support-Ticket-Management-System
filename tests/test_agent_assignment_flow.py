import unittest
from backend.app import create_app
from backend.config.db import execute_query, execute_single, execute_dml

class TestAgentAssignmentFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()

    def test_complete_customer_agent_flow(self):
        """
        Tests the complete end-to-end flow:
        1. Customer creates ticket.
        2. Verify ticket in MySQL.
        3. Agent views dashboard statistics (ensuring no 0s).
        4. Agent assigns ticket to herself ('Assign to Me').
        5. Verify status is 'In Progress' and assigned_agent_id is agent's ID.
        6. Verify ticket appears in My Tickets.
        7. Verify re-login / persistence.
        8. Verify another agent does not see it in their My Tickets.
        """
        # Step 1: Login as Customer
        login_cust = self.client.post('/api/auth/login', json={
            'email': 'alice@customer.com',
            'password': 'Password@123'
        })
        self.assertEqual(login_cust.status_code, 200)
        alice_id = login_cust.json['user']['user_id']

        # Customer creates a new ticket
        create_res = self.client.post('/api/customer/tickets', json={
            'subject': 'Network latency and packet drop on VPN gateway',
            'description': 'Customer experiencing heavy packet drop when connecting to office VPN.',
            'category_id': 3,  # Network
            'priority_id': 2   # Medium
        })
        self.assertEqual(create_res.status_code, 201)
        ticket_id = create_res.json['ticket']['ticket_id']
        self.assertIsNotNone(ticket_id)

        # Step 2: Verify ticket in MySQL
        db_ticket = execute_single("SELECT ticket_id, customer_id, assigned_agent_id, status_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
        self.assertIsNotNone(db_ticket)
        self.assertEqual(db_ticket['customer_id'], alice_id)
        self.assertIsNone(db_ticket['assigned_agent_id'])
        self.assertEqual(db_ticket['status_id'], 1)  # 1 = Open

        # Logout customer
        self.client.post('/api/auth/logout')

        # Step 3: Login as Agent Sarah
        login_agent = self.client.post('/api/auth/login', json={
            'email': 'sarah.agent@support.com',
            'password': 'Password@123'
        })
        self.assertEqual(login_agent.status_code, 200)
        sarah_id = login_agent.json['user']['user_id']
        self.assertEqual(sarah_id, 2)

        # Test Agent Dashboard Statistics (Support Triage & Ticket Queue)
        # Check /api/agent/stats
        agent_stats_res = self.client.get('/api/agent/stats')
        self.assertEqual(agent_stats_res.status_code, 200)
        stats = agent_stats_res.json.get('kpis', agent_stats_res.json)
        self.assertGreater(stats['total_tickets'], 0, "Total tickets must not be 0")
        self.assertGreater(stats['open_tickets'], 0, "Open tickets must not be 0")
        self.assertIn('in_progress_tickets', stats)
        self.assertIn('resolved_tickets', stats)
        self.assertIn('closed_tickets', stats)
        self.assertIn('assigned_tickets', stats)
        self.assertGreater(stats['unassigned_tickets'], 0, "Unassigned tickets must not be 0")

        # Also check /api/dashboard/stats
        dash_stats_res = self.client.get('/api/dashboard/stats')
        self.assertEqual(dash_stats_res.status_code, 200)
        dash_kpis = dash_stats_res.json['kpis']
        self.assertEqual(dash_kpis['total_tickets'], stats['total_tickets'])
        self.assertEqual(dash_kpis['open_tickets'], stats['open_tickets'])
        self.assertEqual(dash_kpis['assigned_tickets'], stats['assigned_tickets'])
        self.assertEqual(dash_kpis['unassigned_tickets'], stats['unassigned_tickets'])

        # Check /api/agent/tickets returns tickets with assigned_agent_id included
        tickets_res = self.client.get('/api/agent/tickets')
        self.assertEqual(tickets_res.status_code, 200)
        tickets = tickets_res.json['tickets']
        self.assertGreater(len(tickets), 0)
        for t in tickets:
            self.assertIn('assigned_agent_id', t, "Every ticket must have assigned_agent_id field")
            self.assertIn('status_name', t)

        # Find the newly created unassigned ticket
        created_ticket_in_queue = next((t for t in tickets if t['ticket_id'] == ticket_id), None)
        self.assertIsNotNone(created_ticket_in_queue)
        self.assertIsNone(created_ticket_in_queue['assigned_agent_id'])
        self.assertEqual(created_ticket_in_queue['status_name'], 'Open')

        # Step 4: Agent assigns ticket to herself ("Assign to Me")
        assign_res = self.client.post(f'/api/agent/tickets/{ticket_id}/claim')
        self.assertEqual(assign_res.status_code, 200)
        self.assertEqual(assign_res.json.get('assigned_agent_id'), sarah_id)

        # Step 5: Verify MySQL state after assignment
        updated_db_ticket = execute_single(
            "SELECT t.ticket_id, t.assigned_agent_id, t.status_id, s.status_name "
            "FROM Tickets t JOIN Ticket_Status s ON t.status_id = s.status_id "
            "WHERE t.ticket_id = %s;",
            (ticket_id,)
        )
        self.assertEqual(updated_db_ticket['assigned_agent_id'], sarah_id)
        self.assertEqual(updated_db_ticket['status_name'], 'In Progress')
        self.assertEqual(updated_db_ticket['status_id'], 2)

        # Verify Ticket_Status_History audit log
        history_entry = execute_single(
            "SELECT * FROM Ticket_Status_History WHERE ticket_id = %s ORDER BY history_id DESC LIMIT 1;",
            (ticket_id,)
        )
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry['new_status_id'], 2)

        # Step 6: Verify ticket appears in My Tickets
        # Test backend query with scope=mine
        my_tickets_res = self.client.get('/api/agent/tickets?scope=mine')
        self.assertEqual(my_tickets_res.status_code, 200)
        my_tickets = my_tickets_res.json['tickets']
        my_ticket_ids = [t['ticket_id'] for t in my_tickets]
        self.assertIn(ticket_id, my_ticket_ids, "Newly assigned ticket MUST appear in My Tickets")

        assigned_ticket_data = next(t for t in my_tickets if t['ticket_id'] == ticket_id)
        self.assertEqual(assigned_ticket_data['assigned_agent_id'], sarah_id)
        self.assertEqual(assigned_ticket_data['status_name'], 'In Progress')
        self.assertEqual(assigned_ticket_data['customer_name'], 'Alice Morgan (Customer)')
        self.assertEqual(assigned_ticket_data['category_name'], 'Network')
        self.assertEqual(assigned_ticket_data['priority_name'], 'Medium')

        # Test frontend filtering simulation (allTickets filtered by t.assigned_agent_id === currentAgent.user_id)
        all_tickets_res = self.client.get('/api/agent/tickets')
        all_tickets = all_tickets_res.json['tickets']
        client_side_my_tickets = [t for t in all_tickets if t['assigned_agent_id'] == sarah_id]
        client_side_ids = [t['ticket_id'] for t in client_side_my_tickets]
        self.assertIn(ticket_id, client_side_ids, "Ticket MUST appear in client-side My Tickets filtering")

        # Step 7: Logout and login again as Sarah - ticket must still appear
        self.client.post('/api/auth/logout')
        self.client.post('/api/auth/login', json={
            'email': 'sarah.agent@support.com',
            'password': 'Password@123'
        })
        persisted_res = self.client.get('/api/agent/tickets?scope=mine')
        self.assertIn(ticket_id, [t['ticket_id'] for t in persisted_res.json['tickets']])

        # Step 8: Login as another Agent (John Davis, user_id = 3)
        self.client.post('/api/auth/logout')
        login_john = self.client.post('/api/auth/login', json={
            'email': 'john.agent@support.com',
            'password': 'Password@123'
        })
        self.assertEqual(login_john.status_code, 200)
        john_id = login_john.json['user']['user_id']
        self.assertEqual(john_id, 3)

        john_my_tickets_res = self.client.get('/api/agent/tickets?scope=mine')
        john_my_ticket_ids = [t['ticket_id'] for t in john_my_tickets_res.json['tickets']]
        self.assertNotIn(ticket_id, john_my_ticket_ids, "Sarah's assigned ticket MUST NOT appear in John's My Tickets")

        john_all_tickets_res = self.client.get('/api/agent/tickets')
        john_client_side = [t for t in john_all_tickets_res.json['tickets'] if t['assigned_agent_id'] == john_id]
        self.assertNotIn(ticket_id, [t['ticket_id'] for t in john_client_side])

if __name__ == '__main__':
    unittest.main()

