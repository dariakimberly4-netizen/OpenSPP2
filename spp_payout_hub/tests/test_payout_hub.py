# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPayoutHub(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.viewer = cls.env["res.users"].create(
            {
                "name": "Payout Viewer",
                "login": "payout_hub_viewer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("spp_programs.group_programs_viewer").id,
                        ]
                    )
                ],
            }
        )
        cls.officer = cls.env["res.users"].create(
            {
                "name": "Payout Officer",
                "login": "payout_hub_officer",
                "group_ids": [
                    Command.set(
                        [
                            cls.env.ref("base.group_user").id,
                            cls.env.ref("spp_programs.group_programs_officer").id,
                        ]
                    )
                ],
            }
        )
        cls.plain_user = cls.env["res.users"].create(
            {
                "name": "Unassigned Staff",
                "login": "payout_hub_unassigned",
                "group_ids": [Command.set([cls.env.ref("base.group_user").id])],
            }
        )

    def test_viewer_receives_existing_actions(self):
        data = self.env["spp.program"].with_user(self.viewer).get_payout_hub_data()
        self.assertEqual(len(data["modules"]), 8)
        for module in data["modules"]:
            if module["available"]:
                action = self.env.ref(module["action"])
                self.assertEqual(action._name, "ir.actions.act_window")
                self.assertGreaterEqual(module["count"], 0)

    def test_registry_and_finance_menu_restrictions(self):
        data = self.env["spp.program"].with_user(self.viewer).get_payout_hub_data()
        modules = {item["key"]: item for item in data["modules"]}
        for key in ("registry", "reports"):
            self.assertFalse(modules[key]["available"])
            self.assertIsNone(modules[key]["action"])
            self.assertIsNone(modules[key]["count"])

    def test_counts_follow_record_rules(self):
        self.env["spp.program"].create({"name": "Hidden payout program"})
        self.env["ir.rule"].create(
            {
                "name": "Test payout isolation",
                "model_id": self.env.ref("spp_programs.model_spp_program").id,
                "domain_force": '[("id", "=", False)]',
            }
        )
        data = self.env["spp.program"].with_user(self.viewer).get_payout_hub_data()
        programs = next(item for item in data["modules"] if item["key"] == "programs")
        self.assertEqual(programs["count"], 0)

    def test_unauthorized_staff_rejected(self):
        with self.assertRaises(AccessError):
            self.env["spp.program"].with_user(self.plain_user).get_payout_hub_data()

    def test_public_user_rejected(self):
        with self.assertRaises(AccessError):
            self.env["spp.program"].with_user(self.env.ref("base.public_user")).get_payout_hub_data()

    def test_officer_metrics_match_permitted_records(self):
        env = self.env["spp.program"].with_user(self.officer).env
        data = env["spp.program"].get_payout_hub_data()
        metrics = {item["key"]: item["count"] for item in data["metrics"]}
        self.assertEqual(
            metrics["pending"],
            env["spp.entitlement"].search_count(
                [
                    ("state", "=", "pending_validation"),
                    ("is_cash_entitlement", "=", True),
                ]
            ),
        )
        self.assertEqual(metrics["paid"], env["spp.payment"].search_count([("status", "=", "paid")]))
        self.assertEqual(metrics["failed"], env["spp.payment"].search_count([("status", "=", "failed")]))

    def test_cash_card_count_matches_action_domain(self):
        env = self.env["spp.program"].with_user(self.viewer).env
        data = env["spp.program"].get_payout_hub_data()
        card = next(item for item in data["modules"] if item["key"] == "entitlements")
        self.assertEqual(card["count"], env["spp.entitlement"].search_count([("is_cash_entitlement", "=", True)]))
