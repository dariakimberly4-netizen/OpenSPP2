import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

// Exercise the actual client controller without requiring a running Odoo browser.
// OWL rendering and Odoo ORM integration are separate installation checks.
const source = readFileSync(new URL('../static/src/payout_hub.js', import.meta.url), 'utf8')
    .replace(/^import .*;$/gm, '').replace('export class PayoutHub', 'class PayoutHub');
const sandbox = { Component: class {}, registry: { category: () => ({ add() {} }) }, _t: (s) => s };
vm.createContext(sandbox);
vm.runInContext(source + '\nglobalThis.Hub = PayoutHub;', sandbox);
const make = () => {
    const hub = new sandbox.Hub();
    hub.state = { loading: false, error: false, modules: [], metrics: [], opening: false, notice: true };
    hub.notification = { add() {} };
    return hub;
};

test('refresh loads server results and clears the loading state', async () => {
    const hub = make();
    hub.orm = { call: async (model, method) => {
        assert.equal(model, 'spp.program'); assert.equal(method, 'get_payout_hub_data');
        return { modules: [{ key: 'cycles' }], metrics: [{ count: 0 }] };
    } };
    await hub.refresh();
    assert.equal(hub.state.modules[0].key, 'cycles');
    assert.equal(hub.state.metrics[0].count, 0);
    assert.equal(hub.state.loading, false);
});

test('failed refresh shows unavailable state, and retry recovers', async () => {
    const hub = make();
    hub.orm = { call: async () => { throw Error('offline'); } };
    await hub.refresh();
    assert.equal(hub.state.error, true); assert.equal(hub.state.loading, false);
    hub.orm.call = async () => ({ modules: [], metrics: [] });
    await hub.refresh(); assert.equal(hub.state.error, false);
});

test('locked modules do not navigate', async () => {
    const hub = make();
    hub.action = { doAction() { assert.fail('locked action invoked'); } };
    await hub.openModule({ available: false });
});

test('navigation cannot be double-submitted and resets after failure', async () => {
    const hub = make(); let calls = 0; let reject;
    hub.action = { doAction: () => { calls++; return new Promise((_, no) => { reject = no; }); } };
    const module = { available: true, action: 'spp_programs.action_cycle_list' };
    const first = hub.openModule(module);
    await hub.openModule(module); assert.equal(calls, 1);
    reject(Error('denied')); await first;
    assert.equal(hub.state.opening, false);
});

test('center opens payout cycles', async () => {
    const hub = make(); let action;
    hub.state.modules = [{ key: 'cycles', available: true, action: 'spp_programs.action_cycle_list' }];
    hub.action = { doAction: async (value) => { action = value; } };
    await hub.openOverview(); assert.equal(action, 'spp_programs.action_cycle_list');
});

test('dismissal works even when browser storage is unavailable', () => {
    const hub = make(); hub.dismissNotice(); assert.equal(hub.state.notice, false);
});
