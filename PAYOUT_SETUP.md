# Start your Payout Hub

This fork is an Odoo 19 application with PostgreSQL, not a GitHub Pages website.
The new `spp_payout_hub` add-on uses the existing OpenSPP records and workflows.

## Local installation

Install Docker Desktop with Docker Compose, then clone **this fork**:

```sh
git clone https://github.com/dariakimberly4-netizen/OpenSPP2.git
cd OpenSPP2
git checkout feat/payout-hub
```

Create a root `.env` file containing:

```dotenv
ODOO_INIT_MODULES=spp_payout_hub
```

Then run:

```sh
docker compose --profile ui up -d --build
```

Open `http://localhost:8069`. The upstream development environment uses
`admin` / `admin`; change the password before entering real records. Open
**Programs → Payout Hub**. If the database was already initialized, activate developer
mode, update the Apps list, find **OpenSPP Payout Hub**, and install it.

No fabricated beneficiary records are installed. Zero counts are expected until
you configure a program and enter records. Existing upstream demo modules are
optional and should use a separate test database.

## Payout workflow

1. **Beneficiaries:** register individuals and their required identifiers.
2. **Programs:** configure assistance, eligibility, currency, disbursement journal,
   managers, and approval rules. Configure PHP currency for a peso-based program.
3. **Enrollment:** use the program's enrollment workflow; the membership screen
   lists its results.
4. **Payout cycles:** create a cycle from a program and set its dates.
5. **Cash approvals:** prepare entitlements from the cycle, submit them, and let
   authorized approvers review them.
6. **Payment batches:** use the configured payment manager to generate/process
   payment records and batches.
7. **Payments:** monitor recorded outcomes. An issued or sent payment is not proof
   that a beneficiary was paid; reconcile actual payment-provider results.
8. **Fund reports:** review program fund entries with an authorized finance role.

Use the native list search, filters, export, and record forms within each module.
Return through **Programs → Payout Hub**. Staff can only open modules allowed by
both their existing menu roles and model permissions. Give users their appropriate
OpenSPP roles; there is no shared one-tap administrator login.

## Hosting

A fork stores source code; it does not start the application. A live shared system
needs an Odoo/PostgreSQL server, HTTPS, backups, and configured staff accounts.
The repository's Docker Compose is a development setup with default credentials;
do not expose it directly to the internet. No live deployment is included in this
change, and no payment-provider credentials are requested or embedded.

## Validation

Run the module's integration/security tests in an environment with Docker:

```sh
./spp t spp_payout_hub
node --test spp_payout_hub/tests/payout_hub_client.test.mjs
```

Manual installation checks: sign in as viewer, officer, and finance manager;
check role-locked shortcuts; open all allowed cards and return; compare counts
with the corresponding filtered lists; dismiss the New notice and reload; resize
the browser and test keyboard navigation. This checkout's `AGENTS.md` references
`docs/principles/` and `.Codex/` resources that are absent from the fork.
