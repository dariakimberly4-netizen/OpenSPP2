# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, api, models
from odoo.exceptions import AccessError


class PayoutHubProgram(models.Model):
    _inherit = "spp.program"

    @api.model
    def get_payout_hub_data(self):
        """Read-only summary; all searches retain the caller's record rules.

        Extend an existing model, so its existing ACLs apply. No additional
        tables, security grants, sudo, or payment state transitions are needed.
        """
        if not self.env.user.has_group("base.group_user"):
            raise AccessError(_("Sign in with a staff account to open the Payout Hub."))
        self.check_access("read")
        user = self.env.user
        registry_access = user.has_group("spp_registry.group_registry_viewer") or user.has_group(
            "spp_security.group_spp_admin"
        )
        finance_access = any(
            user.has_group(group)
            for group in (
                "spp_programs.group_programs_manager",
                "spp_programs.group_programs_validator",
                "spp_security.group_spp_admin",
            )
        )
        # Keep menu-level restrictions as well as model ACLs. Technical registry
        # read permission alone must not grant a standalone PII browsing surface.
        specs = [
            (
                "registry",
                _("Beneficiaries"),
                _("Register and update individuals"),
                "fa-users",
                "spp_registry.action_individuals_list",
                "res.partner",
                registry_access,
                [("is_registrant", "=", True), ("is_group", "=", False)],
            ),
            (
                "programs",
                _("Programs"),
                _("Assistance rules and budgets"),
                "fa-briefcase",
                "spp_programs.action_program_list",
                "spp.program",
                True,
                [],
            ),
            (
                "enrollment",
                _("Enrollment"),
                _("Beneficiary program memberships"),
                "fa-user-plus",
                "spp_programs.action_program_membership",
                "spp.program.membership",
                True,
                [],
            ),
            (
                "cycles",
                _("Payout cycles"),
                _("Dates and distribution rounds"),
                "fa-calendar",
                "spp_programs.action_cycle_list",
                "spp.cycle",
                True,
                [],
            ),
            (
                "entitlements",
                _("Cash approvals"),
                _("Review cash entitlements"),
                "fa-check-square-o",
                "spp_programs.action_entitlement",
                "spp.entitlement",
                True,
                [("is_cash_entitlement", "=", True)],
            ),
            (
                "batches",
                _("Payment batches"),
                _("Organize payment processing"),
                "fa-clone",
                "spp_programs.action_payment_batch",
                "spp.payment.batch",
                True,
                [],
            ),
            (
                "payments",
                _("Payments"),
                _("Track issued, paid and failed"),
                "fa-credit-card",
                "spp_programs.action_payment",
                "spp.payment",
                True,
                [],
            ),
            (
                "reports",
                _("Fund reports"),
                _("Review program fund entries"),
                "fa-bar-chart",
                "spp_programs.action_program_fund_report",
                "spp.program.fund.report.view",
                finance_access,
                [],
            ),
        ]
        modules = []
        for key, label, description, icon, action, model, allowed, domain in specs:
            count = None
            if allowed:
                try:
                    count = self.env[model].search_count(domain)
                except AccessError:
                    allowed = False
            modules.append(
                {
                    "key": key,
                    "label": label,
                    "description": description,
                    "icon": icon,
                    "action": action if allowed else None,
                    "count": count,
                    "available": allowed,
                }
            )
        metrics = []
        for key, label, model, domain in (
            (
                "pending",
                _("Awaiting approval"),
                "spp.entitlement",
                [("state", "=", "pending_validation"), ("is_cash_entitlement", "=", True)],
            ),
            ("paid", _("Paid payments"), "spp.payment", [("status", "=", "paid")]),
            ("failed", _("Failed payments"), "spp.payment", [("status", "=", "failed")]),
        ):
            try:
                count = self.env[model].search_count(domain)
            except AccessError:
                count = None
            metrics.append({"key": key, "label": label, "count": count})
        return {"modules": modules, "metrics": metrics}
