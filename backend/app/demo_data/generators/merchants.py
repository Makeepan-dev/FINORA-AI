from typing import List
from ..models.merchant import SyntheticMerchant, MerchantCategory

def generate_merchants() -> List[SyntheticMerchant]:
    raw_data = [
        # Groceries
        ("mer_fresh_harvest", "Fresh Harvest Organic Market", MerchantCategory.GROCERIES, "Organic produce and pantry staples", "https://freshharvest.synthetic-demo.net", 0.98),
        ("mer_metro_foods", "Metro Foods Supermarket", MerchantCategory.GROCERIES, "Neighborhood grocery and daily goods", "https://metrofoods.synthetic-demo.net", 0.96),
        ("mer_artisan_baker", "Golden Crust Bakery", MerchantCategory.GROCERIES, "Artisan breads, pastries and coffee", "https://goldencrust.synthetic-demo.net", 0.99),
        # Electronics
        ("mer_volt_circuits", "Volt Dynamics Tech", MerchantCategory.ELECTRONICS, "High-end developer displays and peripherals", "https://voltdynamics.synthetic-demo.net", 0.97),
        ("mer_hyper_audio", "HyperAcoustics Sound Labs", MerchantCategory.ELECTRONICS, "Studio headphones and active noise cancelling gear", "https://hyperacoustics.synthetic-demo.net", 0.95),
        ("mer_micro_gear", "Silicon Bay Electronics", MerchantCategory.ELECTRONICS, "Cables, chargers, hubs and smart devices", "https://siliconbay.synthetic-demo.net", 0.94),
        # Clothing & Apparel
        ("mer_nordic_threads", "Nordic Weave Apparel", MerchantCategory.CLOTHING, "Minimalist sustainable wool and cotton clothing", "https://nordicweave.synthetic-demo.net", 0.96),
        ("mer_urban_step", "Stride & Motion Footwear", MerchantCategory.CLOTHING, "Ergonomic sneakers and office athletic shoes", "https://stridemotion.synthetic-demo.net", 0.93),
        ("mer_trail_craft", "Terra Summit Outdoor", MerchantCategory.CLOTHING, "All-weather jackets, hiking apparel and gear", "https://terrasummit.synthetic-demo.net", 0.97),
        # Restaurants & Dining
        ("mer_tokyo_ramen", "Shibuya Umami Noodle Bar", MerchantCategory.RESTAURANTS, "Authentic tonkotsu ramen and small plates", "https://shibuyaumami.synthetic-demo.net", 0.98),
        ("mer_verde_bistro", "Verde Farm Table Bistro", MerchantCategory.RESTAURANTS, "Fresh Mediterranean bowls and seasonal salads", "https://verdebistro.synthetic-demo.net", 0.97),
        ("mer_roast_craft", "Obsidian Espresso Roasters", MerchantCategory.RESTAURANTS, "Single-origin pour-overs and cold brew subscriptions", "https://obsidianroasters.synthetic-demo.net", 0.99),
        ("mer_blue_harbor", "Harbor Light Seafood Grill", MerchantCategory.RESTAURANTS, "Casual dockside dining and takeaway", "https://harborlight.synthetic-demo.net", 0.95),
        # Entertainment & Streaming
        ("mer_stream_pulse", "StreamPulse Prime", MerchantCategory.ENTERTAINMENT, "4K movies, original documentaries and series", "https://streampulse.synthetic-demo.net", 0.99),
        ("mer_sonic_cloud", "SonicWave Music HD", MerchantCategory.ENTERTAINMENT, "Lossless spatial audio streaming service", "https://sonicwave.synthetic-demo.net", 0.99),
        ("mer_game_nexus", "PixelForge Game Pass", MerchantCategory.ENTERTAINMENT, "Cross-platform cloud gaming network", "https://pixelforge.synthetic-demo.net", 0.96),
        # Transportation
        ("mer_city_commute", "SwiftRide Mobility", MerchantCategory.TRANSPORTATION, "Urban on-demand rides and carshares", "https://swiftride.synthetic-demo.net", 0.96),
        ("mer_metro_transit", "Metropolitan Transit District", MerchantCategory.TRANSPORTATION, "Subway, regional rail and transit pass", "https://metrotransit.synthetic-demo.net", 0.99),
        ("mer_charge_net", "VoltPath EV Fast Chargers", MerchantCategory.TRANSPORTATION, "Public electric vehicle ultra-fast charging", "https://voltpath.synthetic-demo.net", 0.97),
        # Digital Services & Cloud
        ("mer_strata_cloud", "StrataVault Cloud Storage", MerchantCategory.DIGITAL_SERVICES, "2TB encrypted backup and sync storage", "https://stratavault.synthetic-demo.net", 0.99),
        ("mer_sentinel_vpn", "Aegis Privacy VPN", MerchantCategory.DIGITAL_SERVICES, "Zero-log encrypted private network service", "https://aegisprivacy.synthetic-demo.net", 0.98),
        ("mer_docu_signet", "SealVault Digital Notary", MerchantCategory.DIGITAL_SERVICES, "Cloud signature and contract verification", "https://sealvault.synthetic-demo.net", 0.98),
        # Education & Learning
        ("mer_code_academy", "KernelCraft Developer Academy", MerchantCategory.EDUCATION, "Interactive deep-dive algorithms and systems", "https://kernelcraft.synthetic-demo.net", 0.97),
        ("mer_lingua_flow", "LinguaPoly Language Studio", MerchantCategory.EDUCATION, "Speech immersion and AI language practice", "https://linguapoly.synthetic-demo.net", 0.96),
        # Fitness & Wellness
        ("mer_apex_fitness", "Apex Athletic Club", MerchantCategory.FITNESS, "Full-service gym, pool and sauna facility", "https://apexathletic.synthetic-demo.net", 0.98),
        ("mer_zen_studio", "Prana Flow Yoga Collective", MerchantCategory.FITNESS, "Reformer pilates, hot yoga and mindfulness", "https://pranaflow.synthetic-demo.net", 0.95),
        ("mer_fit_pulse", "PulseFit Virtual Coaching", MerchantCategory.FITNESS, "Smart watch workout plans and telemetry", "https://pulsefit.synthetic-demo.net", 0.94),
        # Travel & Hospitality
        ("mer_aerowings", "SkyVanguard Airlines", MerchantCategory.TRAVEL, "Domestic and international commercial flights", "https://skyvanguard.synthetic-demo.net", 0.97),
        ("mer_haven_suites", "Haven Loft Boutique Hotels", MerchantCategory.TRAVEL, "Urban workspace apartments and hotel rooms", "https://havenlofts.synthetic-demo.net", 0.96),
        # Home Improvement
        ("mer_craft_timber", "Timber & Stone Hardware", MerchantCategory.HOME_IMPROVEMENT, "Ergonomic standing desk components and home tools", "https://timberstone.synthetic-demo.net", 0.97),
        ("mer_lumina_home", "Lumina Smart Lighting", MerchantCategory.HOME_IMPROVEMENT, "Automated ambient lighting and circadian systems", "https://luminahome.synthetic-demo.net", 0.96),
        # Software & Dev
        ("mer_git_forge", "GitForge Pro Dev Cloud", MerchantCategory.SOFTWARE, "CI/CD pipelines, container registries and code review", "https://gitforge.synthetic-demo.net", 0.99),
        ("mer_ai_synth", "Cognition Engine Pro", MerchantCategory.SOFTWARE, "Developer neural synthesis API subscription", "https://cognitionengine.synthetic-demo.net", 0.98),
        ("mer_linear_task", "PlanCraft Work Management", MerchantCategory.SOFTWARE, "Agile sprint tracking and product roadmap tool", "https://plancraft.synthetic-demo.net", 0.99),
        # Utilities & Telecom
        ("mer_spark_power", "GreenGrid Renewable Power", MerchantCategory.UTILITIES, "Residential clean electricity and water billing", "https://greengrid.synthetic-demo.net", 0.99),
        ("mer_fiber_link", "OpticSpeed Fiber Telecom", MerchantCategory.UTILITIES, "1 Gbps symmetrical residential fiber internet", "https://opticspeed.synthetic-demo.net", 0.98),
    ]

    merchants: List[SyntheticMerchant] = []
    for mid, name, cat, desc, url, score in raw_data:
        merchants.append(
            SyntheticMerchant(
                merchant_id=mid,
                name=name,
                category=cat,
                sub_category=desc,
                website=url,
                country="US",
                currency="USD",
                supports_paypal=True,
                trusted_score=score,
                tags=[cat.value, "synthetic_verified"]
            )
        )
    return merchants
