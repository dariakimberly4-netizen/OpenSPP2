{
    "name": "OpenSPP Payout Hub",
    "summary": "Orbit workspace for beneficiary enrollment, payout cycles, approvals, and payment tracking",
    "version": "19.0.1.0.0",
    "category": "OpenSPP/Programs",
    "license": "LGPL-3",
    "author": "Kimberly Daria",
    "website": "https://github.com/dariakimberly4-netizen/OpenSPP2",
    "depends": ["spp_programs"],
    "data": ["views/payout_hub.xml"],
    "assets": {
        "web.assets_backend": [
            "spp_payout_hub/static/src/payout_hub.js",
            "spp_payout_hub/static/src/payout_hub.xml",
            "spp_payout_hub/static/src/payout_hub.scss",
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
