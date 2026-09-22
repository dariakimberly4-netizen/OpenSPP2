# Payout Hub

A payout-focused workspace inside OpenSPP. Staff sign in through the normal Odoo
login, then open **Programs → Payout Hub**. Eight orbit buttons open existing
OpenSPP screens: individual beneficiaries, programs, enrollment memberships,
payout cycles, cash approvals, payment batches, payments, and fund reports.

The center opens payout cycles. The ring becomes a readable card layout on smaller
screens. A single gold **New** announcement can be dismissed; the dismissal is a
device preference, not beneficiary data.

Counters show pending cash approvals, paid payments, and failed payments across
records the signed-in staff member can read. They are record counts, not unique
beneficiary totals or peso totals. Refresh retrieves the latest figures.

All records remain in OpenSPP's PostgreSQL database. Existing permissions and
record rules remain in force. The module extends `spp.program`; it defines no new
models or access grants, so it intentionally has no `ir.model.access.csv`.
Registry and fund-report shortcuts preserve the original menu-role restrictions.

This module provides navigation and summaries. It does not transfer money, add a
payment provider, bypass approvals, or certify the upstream payment engine. Actual
payment execution requires the program's configured payment manager/provider.
