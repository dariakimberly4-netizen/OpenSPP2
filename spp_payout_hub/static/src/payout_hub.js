/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const NOTICE_KEY = "spp_payout_hub.welcome.v1";

export class PayoutHub extends Component {
    static template = "spp_payout_hub.PayoutHub";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        let notice = true;
        try {
            notice = localStorage.getItem(NOTICE_KEY) !== "dismissed";
        } catch {
            // Blocked device preferences do not prevent use of the workspace.
        }
        this.state = useState({ modules: [], metrics: [], loading: true, error: false, notice, opening: false });
        onWillStart(() => this.refresh());
    }

    async refresh() {
        this.state.loading = true;
        this.state.error = false;
        try {
            const data = await this.orm.call("spp.program", "get_payout_hub_data", []);
            this.state.modules = data.modules;
            this.state.metrics = data.metrics;
        } catch {
            this.state.error = true;
        } finally {
            this.state.loading = false;
        }
    }

    dismissNotice() {
        this.state.notice = false;
        try {
            localStorage.setItem(NOTICE_KEY, "dismissed");
        } catch {
            // Preference is optional; payout records are never stored here.
        }
    }

    async openModule(module) {
        if (!module.available || this.state.opening) return;
        this.state.opening = true;
        try {
            await this.action.doAction(module.action);
        } catch {
            this.notification.add(_t("Unable to open this module. Check your access or try again."), { type: "danger" });
        } finally {
            this.state.opening = false;
        }
    }

    async openOverview() {
        const module = this.state.modules.find((item) => item.key === "cycles");
        if (module) await this.openModule(module);
    }
}
registry.category("actions").add("spp_payout_hub.dashboard", PayoutHub);
