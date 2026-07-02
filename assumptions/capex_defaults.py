def get_default_capex_assumptions():

    return {

        # =====================================================
        # SITE INFORMATION
        # =====================================================

        # Legacy
        # Keep temporarily until site sizing
        # engine is integrated everywhere

        "land_cost_crore": 50.0,

        # =====================================================
        # SITE SIZING
        # =====================================================

        # Core Site Parameters

        "sqft_per_rack": 50,

        "effective_area_multiplier": 2.0,

        "rack_floors": 3,

        "site_coverage_pct": 0.40,

        # Land Pricing
        # RAG-sourceable by location

        "land_cost_per_sqft_rs": 5000,

        # =====================================================
        # SITE LEVEL COSTS
        # =====================================================

        "consultancy_cost_crore": 10.0,

        "approval_cost_crore": 5.0,

        # Utility HT line + metering, facade/external works,
        # commissioning & testing, compound wall + landscaping
        "misc_infrastructure_cost_crore": 18.0,

        "pre_op_pct": 0.10,

       

        # =====================================================
        # DEPLOYMENT PLAN
        # Fit-out (electrical/mechanical/network/IT) deploys in
        # phases to stay ~20% ahead of the lease-up curve.
        # Civil/shell is built 100% in year 1 (see capex engine),
        # so these % apply only to the demand-driven fit-out.
        # =====================================================

        "phase_1_pct": 0.40,

        "phase_2_pct": 0.30,

        "phase_3_pct": 0.30,

        "phase_1_year": 0,

        "phase_2_year": 3,

        "phase_3_year": 6,

        # =====================================================
        # CIVIL & INTERIORS
        # =====================================================

        "shell_cost_per_rack": 0.063,

        "interiors_cost_per_rack": 0.015,

        "security_system_cost_per_rack": 0.007,

        # Legacy Aggregated

        "civil_cost_per_rack": 0.085,

        # =====================================================
        # ELECTRICAL
        # LEGACY FIELDS
        # KEEP UNTIL SIZING ENGINE IS INTEGRATED
        # =====================================================

        "electrical_components_cost_per_rack": 0.074,

        "ups_cost_per_rack": 0.026,

        "battery_cost_per_rack": 0.010,

        "electrical_cost_per_rack": 0.110,

        # =====================================================
        # ELECTRICAL SIZING ENGINE
        # =====================================================

        "contingency_pct": 0.10,

        # ---------------------
        # UPS
        # ---------------------

        "ups_frame_kva": 600,

        "ups_module_kva": 50,

        "ups_active_modules": 10,

        "ups_power_factor": 0.85,

        # ---------------------
        # BATTERY
        # ---------------------

        "battery_backup_hours": 0.25,

        "battery_unit_kwh": 10,

        # ---------------------
        # DG GENSET
        # ---------------------

        "dg_rated_kva": 2500,

        "dg_power_factor": 0.85,

        "dg_load_factor": 0.90,

        # ---------------------
        # TRANSFORMER
        # ---------------------

        "transformer_kva": 3500,

        "transformer_power_factor": 0.90,

        "transformer_load_factor": 0.80,

        # =====================================================
        # ELECTRICAL EQUIPMENT COSTS
        # =====================================================

        # UPS — DC-grade 500 kVA modular frame ~Rs 90L all-in (10x60k modules +
        # 30L frame). Market: DC-grade 500 kVA UPS Rs 85L-1.5Cr; the prior
        # Rs 40L/frame was bottom-of-range (non-DC-grade), ~2x low.

        "ups_module_cost": 600000,

        "ups_frame_cost": 3000000,

        # Battery

        "battery_unit_cost": 150000,

        # DG — 2500 kVA CPCB IV+ silent genset. Market: Cummins 2000 kVA silent
        # ~Rs 2.45 Cr; 2500 kVA ~Rs 2.8-3.5 Cr. Prior Rs 1.5 Cr supply was ~1.8x low.

        "dg_supply_cost": 28000000,

        "dg_acm_cost": 450000,

        "dg_installation_cost": 1200000,

        # Transformer — 3150-3500 kVA (market: Rs 33.6-45L for 3150 kVA). Prior
        # Rs 70L was ~1.5x high; corrected down (partly offsets UPS/DG increases).

        "transformer_supply_cost": 4500000,

        "transformer_panel_cost": 2500000,

        # =====================================================
        # PDU & ELECTRICAL DISTRIBUTION
        # =====================================================

        "pdus_per_rack": 2,

        "pdu_panel_cost": 65000,

        "ups_db_per_20_racks": 4,

        "ups_db_cost": 17500,

        "lighting_per_rack": 2,

        "lighting_cost": 750,

        "earthing_per_rack": 1,

        "earthing_cost": 1500,

        # =====================================================
        # CABLING
        # =====================================================

        "cable_length_per_rack": 40,

        "cable_tray_per_rack": 20,

        "wiring_cost_per_ft": 2600,

        "cable_tray_cost_per_ft": 250,

        "ats_per_rack": 0,

        "ats_cost": 36000,

        # =====================================================
        # IT HARDWARE SIZING
        # =====================================================

        "servers_per_rack": 20,

        "server_unit_cost": 425000,

        "storage_units_per_system": 2,

        "storage_unit_cost": 4250000,

        "racks_per_storage_system": 30,

        "perimeter_firewall_cost": 500000,

        "core_firewall_cost": 533333,

        "software_cost_per_rack": 1090000,

        # =====================================================
        # MECHANICAL
        # =====================================================

        # Cooling infrastructure per rack: CRAC/CRAH + chillers + cooling
        # towers/condensers + air purifiers, plus rack enclosures. Benchmarked
        # to CBRE mechanical cost (~₹8L/rack ≈ 13 Cr/MW at 6kW). The prior
        # 0.015 (₹1.5L) under-costed cooling ~5x vs the CBRE benchmark.
        "mechanical_cost_per_rack": 0.08,

                # =====================================================
        # NETWORK
        # LEGACY FIELD
        # KEEP UNTIL NETWORK SIZING ENGINE IS INTEGRATED
        # =====================================================

        "network_cost_per_rack": 0.050,

        # =====================================================
        # NETWORK SIZING ENGINE
        # =====================================================

        # ---------------------
        # NETWORK REQUIREMENTS
        # ---------------------

        # Perimeter switches: fixed count for the entire facility (HA pair).
        # 2 per 10 racks was architecturally wrong — perimeter equipment
        # doesn't scale per rack.
        "perimeter_switch_count": 4,

        # Spine/core switches: fixed count for the DC fabric (not per rack).
        # Scales slowly with DC size; 6 is right for a 1000-rack Tier III build.
        "spine_switch_count": 6,

        # Leaf switches for management/OOB network: 2 per 10-rack zone,
        # one primary + one standby. These scale with rack count.
        "server_switches_per_10_racks": 2,

        # Load balancers: 0 — in a colo model the DC operator does not
        # provision application-layer load balancers. Tenants bring their own.
        "load_balancers_per_rack": 0,

        # IP KVM per rack for out-of-band hardware management. 1 is standard;
        # 2 was double-counted.
        "kvm_switches_per_rack": 1,

        "network_cable_ft_per_rack": 50,

        # ---------------------
        # NETWORK EQUIPMENT COSTS
        # ---------------------

        "perimeter_switch_cost": 475000,

        "spine_switch_cost": 1200000,

        "server_switch_cost": 850000,

        "load_balancer_cost": 150000,

        "kvm_switch_cost": 30000,

        "network_cable_cost_per_ft": 1000,

        # ---------------------
        # MEET-ME ROOM / INTERCONNECTION INFRASTRUCTURE
        # ---------------------
        # Interconnection fit-out that ENABLES cross-connect revenue: patch /
        # distribution frames, backbone/riser fibre to the meet-me room, and
        # carrier cable entry. Incremental to the intra-rack cabling above.
        # Rs 50,000/rack — midpoint of the US structured-cabling benchmark
        # (~$500-700/rack interconnection layer), conservative given cheaper
        # Indian labour. The MMR *space* itself sits in the civil shell.
        "meet_me_room_cost_per_rack": 50000,

        # ---------------------
        # NETWORK CONTINGENCY
        # ---------------------

        "network_contingency_pct": 0.10,

        # =====================================================
        # SOFTWARE
        # =====================================================

        "dcim_cost_crore": 5.0,

        "dbims_cost_crore": 2.5,

        "virtualization_cost_crore": 5.0,

        # =====================================================
        # IT HARDWARE
        # =====================================================

        "server_refresh_cycle_years": 5,

        "storage_refresh_cycle_years": 5,

        "network_equipment_refresh_cycle_years": 5,

        "it_hardware_cost_per_rack": 0.003,

        # =====================================================
        # REPLACEMENT CYCLES
        # =====================================================

        "battery_replacement_cycle_years": 4,

        "mechanical_replacement_cycle_years": 6,

        "network_refresh_cycle_years": 5,

        "it_refresh_cycle_years": 5,

        # =====================================================
        # REPLACEMENT PERCENTAGES
        # =====================================================

        "battery_replacement_pct": 1.00,

        "mechanical_replacement_pct": 0.50,

        "network_refresh_pct": 1.00,

        "it_refresh_pct": 1.00,

        # =====================================================
        # ESCALATION ASSUMPTIONS
        # =====================================================

        "construction_cost_escalation": 0.05,

        "technology_cost_decline": -0.02,

        # =====================================================
        # DEPLOYMENT PLANNING
        # =====================================================

        "ultimate_capacity_racks": 1000,

        "deployment_strategy": "phased",

        # =====================================================
        # FINANCING PLACEHOLDERS
        # =====================================================

        "construction_period_years": 1,

        "capitalized_interest_pct": 0.0,

        # =====================================================
        # FUTURE RAG PLACEHOLDERS
        # =====================================================

        "location_cost_multiplier": 1.00,

        "market_construction_index": 1.00,

        "power_density_multiplier": 1.00,

        "vendor_pricing_adjustment": 1.00
    }


LOCATION_LAND_COST = {
    "Mumbai":    7000,
    "Pune":      4000,
    "Hyderabad": 3000,
    "Bangalore": 5000,
    "Chennai":   3500,
    "Delhi NCR": 5000,
}