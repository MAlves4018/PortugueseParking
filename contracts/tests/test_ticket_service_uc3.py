from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock, patch

from core.services import ITicketService
from contracts.services import TicketService


class TicketServiceUC3Tests(TestCase):
    """
    UC3 – Occasional tickets (cash device).

    Tests focus on:
      - price calculation (get_occasional_pricing)
      - payment (pay_occasional_ticket)
      - exit logic for occasional tickets
    """

    def setUp(self):
        self.pricing_service = MagicMock()
        self.payment_service = MagicMock()

        self.slot_repo = MagicMock()
        self.vehicle_repo = MagicMock()
        self.contract_repo = MagicMock()
        self.movement_repo = MagicMock()
        self.gate_repo = MagicMock()

        self.service: ITicketService = TicketService(
            pricing_service=self.pricing_service,
            payment_service=self.payment_service,
            slot_repo=self.slot_repo,
            vehicle_repo=self.vehicle_repo,
            contract_repo=self.contract_repo,
            movement_repo=self.movement_repo,
            gate_repo=self.gate_repo,
        )

    @patch("contracts.services.OccasionalTicket")
    def test_get_occasional_pricing_calls_pricing_service(
        self,
        mock_ticket_model,
    ):
        """
        UC3 – price calculation (happy path):

        The service should:
          - find the active occasional ticket
          - call pricing_service.get_occasional_price(...)
          - store amount_due on the ticket
        """

        # Fake ticket
        fake_ticket = MagicMock()
        fake_slot = MagicMock()
        fake_slot.id = "slot-oc-1"
        fake_ticket.slot = fake_slot

        # Realistic entry_time (30 minutes ago) so that
        # "now - entry_time" works without TypeError.
        fake_ticket.entry_time = timezone.now() - timedelta(minutes=30)

        # Chain: select_related().filter().order_by().first() -> fake_ticket
        qs = MagicMock()
        qs.order_by.return_value.first.return_value = fake_ticket
        (
            mock_ticket_model.objects
            .select_related
            .return_value
            .filter
            .return_value
        ) = qs

        # Price returned by pricing service
        self.pricing_service.get_occasional_price.return_value = 3.50

        # Act
        result = self.service.get_occasional_pricing("oc-11-22")

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["amount"], 3.50)

        self.pricing_service.get_occasional_price.assert_called_once()
        fake_ticket.save.assert_called_once_with(update_fields=["amount_due"])

    @patch("contracts.services.OccasionalTicket")
    def test_get_occasional_pricing_no_ticket_found(
        self,
        mock_ticket_model,
    ):
        """
        UC3 – price calculation:

        If there is no active occasional ticket for the plate,
        the service must return a failure result and never call
        the pricing service.
        """

        # Chain returns None as "first" ticket
        qs = MagicMock()
        qs.order_by.return_value.first.return_value = None
        (
            mock_ticket_model.objects
            .select_related
            .return_value
            .filter
            .return_value
        ) = qs

        result = self.service.get_occasional_pricing("oc-11-22")

        self.assertFalse(result["success"])
        self.assertIn("No active occasional ticket", result["reason"])
        self.pricing_service.get_occasional_price.assert_not_called()

    def test_pay_occasional_ticket_uses_payment_service(self):
        """
        UC3 – payment at cash device (happy path):

        The service should:
          - reuse get_occasional_pricing(...)
          - call payment_service.process_payment(...)
          - update ticket with payment information and deadline
        """

        # Fake ticket returned by get_occasional_pricing
        fake_ticket = MagicMock()
        fake_amount = 7.25

        # Replace only the internal pricing method with a stub
        self.service.get_occasional_pricing = MagicMock(
            return_value={
                "success": True,
                "ticket": fake_ticket,
                "amount": fake_amount,
                "duration_minutes": 30,
            }
        )

        self.payment_service.process_payment.return_value = True

        # Act
        result = self.service.pay_occasional_ticket("oc-11-22")

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["amount"], fake_amount)
        self.assertIs(result["ticket"], fake_ticket)

        # Payment service must be called exactly once
        self.payment_service.process_payment.assert_called_once_with(
            customer_id=None,
            amount=fake_amount,
        )

        # Ticket must be saved with payment fields and exit_deadline
        fake_ticket.save.assert_called_once()
        self.assertIn("deadline", result)

    def test_pay_occasional_ticket_payment_failed(self):
        """
        UC3 – payment at cash device:

        If the payment service rejects the transaction,
        the service must return a failure result and the ticket
        must not be updated as paid.
        """

        fake_ticket = MagicMock()
        fake_amount = 10.0

        # Stub pricing info as successful
        self.service.get_occasional_pricing = MagicMock(
            return_value={
                "success": True,
                "ticket": fake_ticket,
                "amount": fake_amount,
                "duration_minutes": 60,
            }
        )

        # Payment fails
        self.payment_service.process_payment.return_value = False

        result = self.service.pay_occasional_ticket("oc-11-22")

        self.assertFalse(result["success"])
        self.assertIn("Payment failed", result["reason"])

        self.payment_service.process_payment.assert_called_once_with(
            customer_id=None,
            amount=fake_amount,
        )
        # Ticket is not saved as "paid"
        fake_ticket.save.assert_not_called()

    # --------- EXIT LOGIC FOR OCCASIONAL TICKETS --------- #

    @patch("contracts.services.OccasionalTicket")
    def test_exit_with_occasional_ticket_not_paid(
        self,
        mock_ticket_model,
    ):
        """
        UC3 – exit with occasional ticket:

        If the ticket exists but is not paid, the service must
        deny exit and should not modify the ticket.
        """

        fake_ticket = MagicMock()
        fake_ticket.is_paid = False  # unpaid ticket

        qs = MagicMock()
        qs.order_by.return_value.first.return_value = fake_ticket
        (
            mock_ticket_model.objects
            .select_for_update
            .return_value
            .select_related
            .return_value
            .filter
            .return_value
        ) = qs

        result = self.service.exit_with_occasional_ticket(
            license_plate="oc-11-22",
            gate_id="gate-1",
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("Ticket not paid", result["reason"])

        # Ticket should not be saved in this case
        fake_ticket.save.assert_not_called()

    @patch("contracts.services.OccasionalTicket")
    def test_exit_with_occasional_ticket_grace_period_expired(
        self,
        mock_ticket_model,
    ):
        """
        UC3 – exit with occasional ticket:

        If the ticket is paid but the grace period has expired,
        the service must reset payment fields and deny exit.
        """

        fake_ticket = MagicMock()
        fake_ticket.is_paid = True  # already paid
        fake_ticket.is_within_grace_period = False  # grace period expired

        qs = MagicMock()
        qs.order_by.return_value.first.return_value = fake_ticket
        (
            mock_ticket_model.objects
            .select_for_update
            .return_value
            .select_related
            .return_value
            .filter
            .return_value
        ) = qs

        result = self.service.exit_with_occasional_ticket(
            license_plate="oc-11-22",
            gate_id="gate-1",
        )

        self.assertFalse(result["success"])
        self.assertFalse(result["open_gate"])
        self.assertIn("Grace period expired", result["reason"])

        # Ticket must be saved with reset payment fields
        fake_ticket.save.assert_called_once()
        call_kwargs = fake_ticket.save.call_args.kwargs
        self.assertIn("update_fields", call_kwargs)

    @patch("contracts.services.OccasionalTicket")
    def test_exit_with_occasional_ticket_success(
        self,
        mock_ticket_model,
    ):
        """
        UC3 – exit with occasional ticket (happy path):

        If the ticket is paid and still within grace period,
        the service must mark the ticket as closed and allow exit.
        """

        fake_ticket = MagicMock()
        fake_ticket.is_paid = True
        fake_ticket.is_within_grace_period = True

        qs = MagicMock()
        qs.order_by.return_value.first.return_value = fake_ticket
        (
            mock_ticket_model.objects
            .select_for_update
            .return_value
            .select_related
            .return_value
            .filter
            .return_value
        ) = qs

        result = self.service.exit_with_occasional_ticket(
            license_plate="oc-11-22",
            gate_id="gate-1",
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["open_gate"])
        self.assertIn("Exit granted", result["reason"])

        # Ticket must be saved with exit_time and is_closed=True
        fake_ticket.save.assert_called_once()
        call_kwargs = fake_ticket.save.call_args.kwargs
        self.assertIn("update_fields", call_kwargs)
