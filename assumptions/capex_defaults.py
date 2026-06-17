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

        "pre_op_pct": 0.15,

       

        # =====================================================
        # DEPLOYMENT PLAN
        # =====================================================

        "phase_1_racks": 300,

        "phase_2_racks": 300,

        "phase_3_racks": 400,

        "phase_1_year": 0,

        "phase_2_year": 3,

        "phase_3_year": 6,

        # =====================================================
        # CIVIL & INTERIORS
        # =====================================================

        "shell_cost_per_rack": 0.040,

        "interiors_cost_per_rack": 0.010,

        "security_system_cost_per_rack": 0.004,

        # Legacy Aggregated

        "civil_cost_per_rack": 0.054,

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

        # UPS

        "ups_module_cost": 250000,

        "ups_frame_cost": 1500000,

        # Battery

        "battery_unit_cost": 150000,

        # DG

        "dg_supply_cost": 15000000,

        "dg_acm_cost": 450000,

        "dg_installation_cost": 1200000,

        # Transformer

        "transformer_supply_cost": 7000000,

        "transformer_panel_cost": 2500000,

        # =====================================================
        # PDU & ELECTRICAL DISTRIBUTION
        # =====================================================

        "pdus_per_rack": 2,

        "pdu_panel_cost": 175000,

        "ups_db_per_20_racks": 4,

        "ups_db_cost": 17500,

        "lighting_per_rack": 2,

        "lighting_cost": 750,

        "earthing_per_rack": 1,

        "earthing_cost": 25000,

        # =====================================================
        # CABLING
        # =====================================================

        "cable_length_per_rack": 40,

        "cable_tray_per_rack": 20,

        "wiring_cost_per_ft": 2600,

        "cable_tray_cost_per_ft": 250,

        "ats_per_rack": 1,

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

        "mechanical_cost_per_rack": 0.00891,

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

        "dmz_switches_per_10_racks": 2,

        "core_switches_per_20_racks": 2,

        "server_switches_per_10_racks": 2,

        "load_balancers_per_rack": 1,

        "kvm_switches_per_rack": 2,

        "network_cable_ft_per_rack": 50,

        # ---------------------
        # NETWORK EQUIPMENT COSTS
        # ---------------------

        "dmz_switch_cost": 475000,

        "core_switch_cost": 1200000,

        "server_switch_cost": 850000,

        "load_balancer_cost": 150000,

        "kvm_switch_cost": 30000,

        "network_cable_cost_per_ft": 1000,

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

        "it_hardware_cost_per_rack": 0.021,

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