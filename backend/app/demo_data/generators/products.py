from decimal import Decimal
from typing import List
from ..models.product import SyntheticProduct, ProductCategory

def generate_products() -> List[SyntheticProduct]:
    products: List[SyntheticProduct] = []

    # Helper templates across categories
    categories_data = [
        # Electronics & Hardware (25 products)
        (
            ProductCategory.ELECTRONICS,
            "mer_volt_circuits",
            [
                ("UltraView 27-inch 4K HDR Studio Monitor", Decimal("399.99"), Decimal("15.00"), 3, 30, 24, {"Resolution": "3840x2160", "Refresh Rate": "144Hz", "Panel": "IPS", "Color": "99% DCI-P3"}),
                ("ProView 34-inch Curved Ultrawide Display", Decimal("649.00"), Decimal("25.00"), 4, 30, 36, {"Resolution": "3440x1440", "Curvature": "1800R", "Refresh": "165Hz", "Thunderbolt": "90W PD"}),
                ("PixelFlex 15.6-inch Portable OLED Screen", Decimal("229.50"), Decimal("0.00"), 2, 30, 12, {"Display": "OLED FHD", "Weight": "650g", "Ports": "Dual USB-C, Mini-HDMI"}),
                ("VoltHub 12-in-1 Thunderbolt 4 Docking Hub", Decimal("179.00"), Decimal("0.00"), 2, 30, 24, {"Power Delivery": "100W", "Displays": "Triple 4K@60Hz", "Ethernet": "2.5 Gbps"}),
                ("VoltDesk 65W GaN Dual USB-C Fast Charger", Decimal("38.50"), Decimal("4.99"), 2, 14, 12, {"Ports": "2x USB-C, 1x USB-A", "Tech": "GaN III", "Foldable": "Yes"}),
                ("VoltCore 140W Universal Power Bank 27000mAh", Decimal("89.95"), Decimal("0.00"), 2, 30, 18, {"Capacity": "99.9Wh Flight-Safe", "Output": "140W USB-C PD 3.1"}),
                ("VoltStream 4K60 Pro Capture Card", Decimal("129.99"), Decimal("5.00"), 3, 30, 12, {"Pass-through": "Zero Lag 4K@120Hz HDR", "Interface": "USB 3.2 Gen 2"}),
                ("VoltKey Wireless Dual-Mode Mechanical Keyboard", Decimal("119.00"), Decimal("0.00"), 3, 30, 12, {"Switches": "Hot-swappable tactile", "Battery": "4000mAh (200 hrs)", "RGB": "Per-key"}),
                ("VoltGlide Ergo Precision Wireless Mouse", Decimal("74.50"), Decimal("0.00"), 2, 30, 12, {"DPI": "26000", "Sensor": "Optical", "Connectivity": "Bluetooth + 2.4G"}),
                ("VoltPad Extended Wool-Felt Desk Mat (90x40cm)", Decimal("29.99"), Decimal("4.50"), 3, 30, 6, {"Material": "Merino Wool & Natural Cork", "Thickness": "4mm"}),
                ("VoltStand Heavy Duty Gas Spring Monitor Arm", Decimal("62.00"), Decimal("8.00"), 3, 30, 24, {"Weight Capacity": "9kg", "VESA": "75x75, 100x100", "Tilt": "+90/-45 deg"}),
                ("VoltCam 4K Studio AI Webcam with HDR", Decimal("149.00"), Decimal("0.00"), 2, 30, 12, {"Field of View": "90 deg", "Focus": "Dual-pixel autofocus", "Mics": "Noise-cancelling dual array"}),
                ("VoltLink Braided 240W Thunderbolt 4 Cable 2m", Decimal("24.99"), Decimal("3.00"), 2, 14, 12, {"Speed": "40Gbps", "Power": "240W EPR", "Durability": "25000 bends"}),
                ("VoltSafe Smart Biometric Desktop Safe", Decimal("199.00"), Decimal("15.00"), 4, 30, 24, {"Lock": "Fingerprint + PIN", "Backup": "Physical keys", "Steel": "Solid 14-gauge"}),
                ("VoltCool MagSafe Wireless Car Vent Mount", Decimal("34.99"), Decimal("0.00"), 2, 30, 12, {"Charging": "15W Qi2 Certified", "Mount": "Steel hook clamping"}),
            ]
        ),
        (
            ProductCategory.ELECTRONICS,
            "mer_micro_gear",
            [
                ("MicroLink 8-Port Gigabit Smart Switch", Decimal("45.00"), Decimal("5.00"), 3, 30, 12, {"Ports": "8x 10/100/1000 Mbps", "Housing": "Metal", "PoE": "No"}),
                ("MicroPlug Smart Home Wi-Fi Power Outlet 4-Pack", Decimal("32.99"), Decimal("0.00"), 2, 30, 12, {"Protocol": "Matter & Apple HomeKit", "Monitoring": "Real-time energy tracking"}),
                ("MicroSensor Zigbee Temperature & Humidity Sensor", Decimal("18.50"), Decimal("3.50"), 2, 30, 12, {"Battery": "CR2450 (2 yrs)", "Precision": "+/- 0.2C"}),
                ("MicroDrive 2TB Rugged External NVMe SSD", Decimal("169.99"), Decimal("0.00"), 2, 30, 36, {"Speed": "2000 MB/s", "Drop Resistance": "3 meters", "IP Rating": "IP67"}),
                ("MicroFlash 256GB Dual Type-C/A Flash Drive", Decimal("26.90"), Decimal("2.50"), 2, 30, 12, {"Read Speed": "400 MB/s", "Casing": "Zinc alloy"}),
                ("MicroClean Electric Compressed Air Duster", Decimal("39.99"), Decimal("0.00"), 2, 30, 12, {"RPM": "110000", "Battery": "7500mAh", "Nozzles": "5 interchangeable"}),
                ("MicroScreen Clean Spray & Microfiber Kit", Decimal("14.99"), Decimal("2.00"), 2, 14, 6, {"Formula": "Alcohol-free, streak-free", "Size": "250ml"}),
                ("MicroCable 6-in-1 Universal Travel Cable Set", Decimal("22.50"), Decimal("3.00"), 2, 30, 12, {"Adapters": "Lightning, Micro-USB, Type-C", "Case": "Aluminum compact"}),
                ("MicroLamp Minimalist USB-C Monitor Light Bar", Decimal("48.00"), Decimal("0.00"), 2, 30, 12, {"Color Temp": "2700K - 6500K", "Control": "Touch sensitive", "Glare": "Zero screen reflection"}),
                ("MicroStand Aluminum MagSafe iPhone Desk Stand", Decimal("25.00"), Decimal("3.50"), 2, 30, 12, {"Angle": "360 deg rotatable", "Finish": "Anodized space grey"}),
            ]
        ),
        # Audio & Sound (15 products)
        (
            ProductCategory.AUDIO,
            "mer_hyper_audio",
            [
                ("AcousticPro ANC Wireless Studio Headphones", Decimal("279.00"), Decimal("0.00"), 2, 30, 24, {"Driver": "40mm custom graphene", "ANC": "Hybrid Active -42dB", "Battery": "50 hours", "Codecs": "LDAC, AAC"}),
                ("PulseTWS True Wireless Earbuds with Spatial Audio", Decimal("149.99"), Decimal("0.00"), 2, 30, 12, {"Waterproof": "IPX5", "ANC": "Smart Transparency", "Case Battery": "32 hours total"}),
                ("SoundStage Desktop Reference Studio Monitors (Pair)", Decimal("249.50"), Decimal("18.00"), 4, 30, 24, {"Power": "100W Class-D", "Inputs": "Optical, Balanced TRS, Bluetooth 5.3"}),
                ("HyperVoice Broadcast Cardioid USB-C Microphone", Decimal("119.00"), Decimal("0.00"), 2, 30, 24, {"Sample Rate": "24-bit/192kHz", "Pattern": "Cardioid, Omnidirectional", "Monitoring": "Zero-latency 3.5mm"}),
                ("VocalShield Desktop Pop Filter & Shock Mount", Decimal("34.99"), Decimal("4.00"), 3, 30, 12, {"Material": "Dual-layer metal mesh", "Thread": "Standard 5/8 and 3/8 inch"}),
                ("SoundBar Compact 2.0 Computer Soundbar", Decimal("69.00"), Decimal("0.00"), 3, 30, 12, {"Drivers": "Dual neodymium full-range", "Inputs": "USB Audio, AUX, Bluetooth"}),
                ("HyperAmp Hi-Res USB DAC & Headphone Amplifier", Decimal("89.00"), Decimal("0.00"), 2, 30, 18, {"Chipset": "ESS Sabre ES9038Q2M", "Output Power": "600mW @ 32 ohms", "SNR": "120dB"}),
                ("AcousticFoam Pro Studio Sound Treatment Panels (12-Pack)", Decimal("49.90"), Decimal("7.50"), 3, 30, 12, {"Dimensions": "30x30x5cm", "Density": "30kg/m3", "Fire Retardant": "Class A"}),
                ("HyperBoom Portable Waterproof Rugged Bluetooth Speaker", Decimal("79.99"), Decimal("0.00"), 2, 30, 12, {"Battery": "24 hours", "Waterproof": "IP67 floatable", "Stereo Pairing": "Yes"}),
                ("AudioCable Gold-Plated Balanced XLR Cable 3m", Decimal("19.99"), Decimal("3.00"), 2, 14, 12, {"Conductors": "Oxygen-free copper (OFC)", "Shielding": "95% braided"}),
                ("SoundDampening Isolation Studio Monitor Pads (Pair)", Decimal("24.50"), Decimal("3.50"), 2, 30, 12, {"Material": "High-density acoustic foam", "Angle": "5 adjustable inclinations"}),
                ("HyperMini Clip-On Wireless Lavalier Mic System", Decimal("89.99"), Decimal("0.00"), 2, 30, 12, {"Range": "100 meters line-of-sight", "Battery": "8 hrs per transmitter", "Noise Cancel": "DSP based"}),
                ("SleepSound Mask with Flat Ultra-Thin Bluetooth Speakers", Decimal("35.00"), Decimal("0.00"), 2, 30, 6, {"Fabric": "Memory foam & breathable silk", "Timer": "Auto-off sleep timer"}),
                ("HyperBass Active 8-inch Compact Subwoofer", Decimal("189.00"), Decimal("16.00"), 4, 30, 24, {"Power": "150W RMS", "Frequency Response": "35Hz - 150Hz", "Crossover": "Adjustable"}),
                ("AudioClean Stylus & Record Cleaning Kit", Decimal("22.00"), Decimal("3.00"), 2, 14, 6, {"Brush": "Carbon fiber antistatic", "Fluid": "Quick-drying non-toxic"}),
            ]
        ),
        # Office & Workspace (20 products)
        (
            ProductCategory.OFFICE,
            "mer_craft_timber",
            [
                ("TimberDesk Pro Solid Oak Dual-Motor Standing Desk", Decimal("580.00"), Decimal("35.00"), 5, 45, 60, {"Desktop": "Solid European Oak 140x70cm", "Motors": "Dual whisper-quiet", "Memory": "4 presets", "Weight Limit": "120kg"}),
                ("ErgoSit Mesh Ergonomic Lumbar Task Chair", Decimal("320.00"), Decimal("20.00"), 4, 30, 36, {"Lumbar": "Dynamic 3D support", "Armrests": "4D adjustable", "Mesh": "High-tensile breathable elastomeric"}),
                ("TimberStool Active Ergonomic Wobble Balance Stool", Decimal("110.00"), Decimal("10.00"), 3, 30, 24, {"Base": "Weighted convex non-slip rubber", "Height Range": "55cm - 80cm pneumatic"}),
                ("CableCraft Under-Desk Wire Management Channel", Decimal("32.50"), Decimal("0.00"), 2, 30, 12, {"Material": "Powder-coated steel", "Length": "80cm", "Install": "No drill clamp-on"}),
                ("TimberRiser Solid Walnut Desktop Monitor Stand", Decimal("68.00"), Decimal("5.00"), 3, 30, 24, {"Material": "American Walnut with cork feet", "Length": "105cm (dual monitor)"}),
                ("FootRest Adjustable Angle Heated Footrest", Decimal("45.00"), Decimal("4.50"), 3, 30, 12, {"Tilt": "0 to 30 degrees", "Massage Rollers": "Built-in central texture"}),
                ("DeskPad Leatherette Waterproof Blotter (80x40cm)", Decimal("24.99"), Decimal("0.00"), 2, 30, 6, {"Material": "Vegan PU Leather", "Reversible": "Dual color black/charcoal"}),
                ("TimberTray Magnetic Desk Drawer Add-on", Decimal("39.00"), Decimal("3.50"), 3, 30, 12, {"Slide": "Ball-bearing whisper glide", "Dimensions": "35x25x5cm"}),
                ("BalanceBoard Anti-Fatigue Standing Desk Rocker", Decimal("65.00"), Decimal("7.00"), 3, 30, 24, {"Surface": "Textured ergonomic PU foam", "Base": "Natural Birch plywood"}),
                ("PrivacyScreen Magnetic Acrylic Desk Divider", Decimal("55.00"), Decimal("6.00"), 3, 30, 12, {"Sound Absorption": "NRC 0.85 acoustic felt", "Mount": "Universal clamp"}),
                ("HeadphoneHanger Under-Desk Swivel Aluminum Hook", Decimal("16.00"), Decimal("2.50"), 2, 14, 12, {"Rotation": "360 degrees", "Cable Clip": "Integrated loop"}),
                ("TimberCupboard 3-Drawer Mobile Office Cabinet", Decimal("145.00"), Decimal("18.00"), 5, 30, 24, {"Lock": "Interlocking single-key lock", "Wheels": "Heavy-duty casters"}),
                ("AirPurifier Desk HEPA Filter Air Purifier", Decimal("59.90"), Decimal("0.00"), 3, 30, 18, {"CADR": "120 m3/h", "Noise": "Quiet 24dB sleep mode", "Filter": "True HEPA H13"}),
                ("DeskFan USB Oscillating Bladeless Desktop Fan", Decimal("32.00"), Decimal("3.00"), 2, 30, 12, {"Speeds": "4 levels", "Noise": "Below 30dB", "Timer": "1-4 hours"}),
                ("PaperShredder Micro-Cut P-4 Document Security Shredder", Decimal("78.00"), Decimal("8.00"), 3, 30, 24, {"Capacity": "10 sheets per pass", "Bin": "18 Liters pull-out", "Safety": "Auto-reverse sensor"}),
                ("Whiteboard Portable Tempered Glass Desktop Whiteboard", Decimal("36.00"), Decimal("4.00"), 2, 30, 12, {"Storage": "Internal organizer for markers", "Surface": "Non-staining tempered glass"}),
                ("ErgoMousePad Gel Wrist Rest Cushion", Decimal("15.99"), Decimal("2.00"), 2, 14, 6, {"Filling": "Cooling memory gel", "Base": "Non-skid polyurethane"}),
                ("DocumentHolder Adjustable Eye-Level Reading Stand", Decimal("22.50"), Decimal("3.00"), 2, 30, 12, {"Clips": "Spring-loaded page holders", "Angles": "7 viewing angles"}),
                ("PenPot Weighted Cast Brass Minimalist Pen Stand", Decimal("28.00"), Decimal("3.50"), 2, 30, 60, {"Weight": "350g solid brass", "Finish": "Matte brushed lacquer"}),
                ("CableTies Reusable Hook-and-Loop Cable Organizers 50-Pack", Decimal("11.99"), Decimal("0.00"), 2, 30, 6, {"Length": "15cm and 20cm assortment", "Material": "Durable nylon"}),
            ]
        ),
        # Fitness & Wellness (15 products)
        (
            ProductCategory.FITNESS,
            "mer_apex_fitness",
            [
                ("ApexGrip Adjustable Dumbbell Set (5 - 52.5 lbs Pair)", Decimal("349.00"), Decimal("40.00"), 5, 30, 24, {"Adjustment": "Dial selection 2.5 lb increments", "Plates": "Durable molding steel"}),
                ("KettleBell Cast Iron 16kg Competition Kettlebell", Decimal("58.00"), Decimal("12.00"), 4, 30, 12, {"Handle": "Smooth textured ergonomic grip", "Weight": "16kg (35.2 lbs)"}),
                ("ApexMat Non-Slip Extra-Thick 6mm Natural Rubber Yoga Mat", Decimal("54.00"), Decimal("0.00"), 2, 30, 12, {"Material": "Biodegradable tree rubber", "Dimensions": "183x68cm", "Grip": "Wet & dry grip"}),
                ("MassageGun Deep Tissue Percussion Muscle Massager", Decimal("99.00"), Decimal("0.00"), 2, 30, 24, {"Stall Force": "45 lbs", "Speeds": "5 gear settings", "Heads": "6 interchangeable heads"}),
                ("ResistanceBands Heavy-Duty Stackable Latex Tube Bands Set", Decimal("29.99"), Decimal("0.00"), 2, 30, 12, {"Resistance": "Up to 150 lbs total", "Accessories": "Door anchor, ankle straps, handles"}),
                ("JumpRope Precision Ball-Bearing Speed Jump Rope", Decimal("18.50"), Decimal("2.50"), 2, 30, 12, {"Cable": "Coated steel wire", "Bearings": "360-degree dual bearing"}),
                ("FoamRoller High-Density Grid Trigger Point Muscle Roller", Decimal("24.00"), Decimal("3.00"), 2, 30, 12, {"Length": "45cm", "Core": "Rigid hollow PVC pipe"}),
                ("PullUpBar Multi-Grip Doorway Pull-Up & Chin-Up Bar", Decimal("38.00"), Decimal("5.00"), 3, 30, 12, {"Door Width": "fits 60-85cm", "Max User Weight": "136kg / 300 lbs"}),
                ("AbWheel Ultra-Wide Kinetic Spring Abdominal Roller", Decimal("26.90"), Decimal("3.00"), 2, 30, 12, {"Wheel": "Extra-wide curved tread", "Assistance": "Carbon steel kinetic engine"}),
                ("WorkoutGloves Breathable Padded Palm Weightlifting Gloves", Decimal("19.99"), Decimal("2.00"), 2, 30, 6, {"Protection": "Silicone honeycomb grip", "Wrist Wrap": "Integrated velcro wrap"}),
                ("SmartScale Bluetooth Body Composition Scale", Decimal("42.00"), Decimal("0.00"), 2, 30, 18, {"Metrics": "14 body metrics (BMI, visceral fat, muscle)", "Sync": "Apple Health & Google Fit"}),
                ("HydrationFlask 32oz Insulated Stainless Steel Sports Bottle", Decimal("27.50"), Decimal("0.00"), 2, 30, 36, {"Insulation": "TempShield double-wall (24h cold)", "Lid": "Straw sport lid"}),
                ("GymBag Waterproof Duffel with Separate Shoe Compartment", Decimal("46.00"), Decimal("4.00"), 3, 30, 12, {"Capacity": "40 Liters", "Fabric": "900D water-repellent nylon"}),
                ("AgilityLadder 6-Meter Speed Training Agility Ladder with Cones", Decimal("21.00"), Decimal("3.00"), 2, 30, 12, {"Rungs": "12 adjustable nylon rungs", "Stakes": "4 metal ground anchors"}),
                ("AnkleWeights Adjustable 5 lb Pair Weighted Leg Straps", Decimal("23.50"), Decimal("3.50"), 2, 30, 12, {"Pockets": "Removable iron sand pockets", "Closure": "Reinforced D-ring strap"}),
            ]
        ),
        # Productivity, Home & Lighting (15 products)
        (
            ProductCategory.HOME,
            "mer_lumina_home",
            [
                ("LuminaBar ScreenBar Pro Smart Circadian Lighting", Decimal("79.99"), Decimal("0.00"), 2, 30, 24, {"CRI": ">95 color accuracy", "Sensor": "Auto-dimming ambient light sensor"}),
                ("LuminaFloor Minimalist Linear Corner LED Floor Lamp", Decimal("95.00"), Decimal("8.00"), 3, 30, 24, {"Height": "145cm", "Colors": "16 million RGB + warm/cool white", "App": "Wi-Fi smart control"}),
                ("LuminaStrip 5m Addressable Gradient Smart LED Lightstrip", Decimal("39.99"), Decimal("0.00"), 2, 30, 18, {"Control": "Matter, Alexa, Google Home", "Effects": "Dynamic sound sync"}),
                ("LuminaBulb Smart E26 Tunable Filament Vintage Bulb (4-Pack)", Decimal("32.50"), Decimal("0.00"), 2, 30, 12, {"Brightness": "800 Lumens", "Color": "2200K - 5000K warm candle to daylight"}),
                ("TimeCube Hexagon Magnetic Pomodoro Productivity Timer", Decimal("21.99"), Decimal("2.50"), 2, 30, 12, {"Presets": "5, 10, 25, 30, 45, 60 min", "Display": "OLED gravity flip screen"}),
                ("EmberMug Smart Temperature-Controlled Ceramic Coffee Mug", Decimal("129.00"), Decimal("0.00"), 2, 30, 18, {"Battery": "80 mins (all-day on coaster)", "Temp Range": "50C - 62.5C (120F - 145F)"}),
                ("AromaDiffuser Ultrasonic Wood Grain Essential Oil Diffuser", Decimal("28.00"), Decimal("3.00"), 2, 30, 12, {"Capacity": "400ml", "Run Time": "12 hours continuous", "Light": "7 color mood lights"}),
                ("DeskClock E-Ink Minimalist Calendar & Clock Widget", Decimal("64.00"), Decimal("0.00"), 3, 30, 12, {"Display": "4.2-inch crisp E-Paper", "Battery": "6 months rechargeable"}),
                ("UnderDeskHeater Ceramic Low-Wattage Safe Foot Warmer", Decimal("44.50"), Decimal("4.00"), 3, 30, 12, {"Safety": "Tip-over & overheat auto shutoff", "Power": "250W energy saver"}),
                ("CableOrganizerBamboo Desktop Charging Station & Cord Dock", Decimal("34.00"), Decimal("3.50"), 2, 30, 12, {"Material": "100% Sustainable Bamboo", "Slots": "5 device divider racks"}),
                ("LuminaNight Smart Motion Sensor Hallway Night Lights (3-Pack)", Decimal("24.00"), Decimal("0.00"), 2, 30, 12, {"Sensor": "PIR infrared detection 3m", "Battery": "USB-C rechargeable 90 days"}),
                ("CoffeeDripper Ceramic V60 Pour-Over Coffee Brewer", Decimal("23.00"), Decimal("3.00"), 2, 14, 12, {"Material": "Arita-ware Japanese Ceramic", "Capacity": "1-4 cups (02 size)"}),
                ("CoffeeGrinder Manual Conical Burr Stainless Steel Hand Grinder", Decimal("59.00"), Decimal("0.00"), 2, 30, 24, {"Burrs": "38mm CNC 420 stainless steel", "Clicks": "36 grind adjustments"}),
                ("VacuumContainer Airtight UV-Proof Coffee Bean Container", Decimal("29.90"), Decimal("3.00"), 2, 30, 12, {"Pump": "Integrated vacuum pump lid", "Capacity": "1.2 Liters"}),
                ("DeskPlant Geometric Concrete Succulent Planters (Trio)", Decimal("26.50"), Decimal("4.00"), 3, 14, 6, {"Material": "Handmade architectural concrete", "Drainage": "Built-in tray hole"}),
            ]
        ),
        # Software & Digital Tools (15 products)
        (
            ProductCategory.SOFTWARE,
            "mer_git_forge",
            [
                ("DevSuite Pro Lifetime Developer License", Decimal("199.00"), Decimal("0.00"), 1, 14, 12, {"License": "Perpetual offline license", "Updates": "1 year included", "Platforms": "macOS, Linux, Windows"}),
                ("CloudCompute 500 Credits Developer Pack", Decimal("99.00"), Decimal("0.00"), 1, 7, 0, {"Type": "Prepaid GPU inference credits", "Expiry": "Never expires"}),
                ("SecureVault Password & Key Management Team Tier (Annual)", Decimal("120.00"), Decimal("0.00"), 1, 30, 0, {"Users": "Up to 5 team members", "Storage": "10GB encrypted vault", "Auditing": "SOC2 certified"}),
                ("DesignCraft UI Pro Component Library & Figma Kit", Decimal("89.00"), Decimal("0.00"), 1, 14, 0, {"Components": "1200+ React & Tailwind widgets", "Figma": "Complete design tokens"}),
                ("GitForge Enterprise Server Self-Hosted Single Node", Decimal("480.00"), Decimal("0.00"), 1, 30, 12, {"Capacity": "25 developers", "Support": "Priority email support", "Security": "SAML SSO"}),
                ("CodeLint Static Analysis & Vulnerability Scanner (Annual)", Decimal("150.00"), Decimal("0.00"), 1, 30, 0, {"Languages": "Python, TypeScript, Go, Rust", "Rule Packs": "OWASP Top 10"}),
                ("APIInspector Mocking & Contract Testing Studio", Decimal("65.00"), Decimal("0.00"), 1, 14, 0, {"Protocols": "REST, GraphQL, gRPC", "Environments": "Unlimited team workspaces"}),
                ("TypeDocs Automated Documentation & OpenAPI Publisher", Decimal("75.00"), Decimal("0.00"), 1, 14, 0, {"Export": "Static HTML, Markdown, PDF", "Custom Domain": "SSL included"}),
                ("DatabaseStudio Visual Schema Modeler & Migration Tool", Decimal("85.00"), Decimal("0.00"), 1, 14, 0, {"Databases": "PostgreSQL, MySQL, SQLite", "Diffing": "Live schema comparison"}),
                ("RegExMaster Visual Pattern Debugger & Benchmark Tool", Decimal("29.00"), Decimal("0.00"), 1, 14, 0, {"Engines": "PCRE, JS, Python re", "Performance": "Microsecond profiler"}),
                ("FontFamily Monospace Pro Programming Font Bundle", Decimal("49.00"), Decimal("0.00"), 1, 14, 0, {"Weights": "8 weights + italics", "Ligations": "Over 80 coding ligatures"}),
                ("TerminalPower Zsh/Fish Workflow Accelerator Plugin Suite", Decimal("35.00"), Decimal("0.00"), 1, 14, 0, {"Features": "Fuzzy history, AI autocompletion, git aliases"}),
                ("AudioPlugin Pro EQ & Spectral Analyzer VST3/AU", Decimal("79.00"), Decimal("0.00"), 1, 14, 0, {"DAWs": "Ableton, Logic, Reaper", "Bands": "12 dynamic parametric bands"}),
                ("VideoEncoder Pro Hardware-Accelerated Batch Compressor", Decimal("49.99"), Decimal("0.00"), 1, 14, 0, {"Codecs": "AV1, HEVC, ProRes", "Speed": "NVENC & QuickSync optimized"}),
                ("DiagramForge Architectural System Architecture Modeler", Decimal("59.00"), Decimal("0.00"), 1, 14, 0, {"Diagrams": "C4 Model, Sequence, Cloud Architecture", "Export": "SVG, PNG, Mermaid"}),
            ]
        ),
    ]

    p_idx = 1
    for cat, default_merchant, item_list in categories_data:
        for name, price, ship, del_days, ret_days, war_mo, specs in item_list:
            pid = f"prd_{p_idx:03d}_{name.lower().replace(' ', '_')[:16]}"
            products.append(
                SyntheticProduct(
                    product_id=pid,
                    merchant_id=default_merchant,
                    product_name=name,
                    description=f"Synthetic demo product: {name}. Precision engineered for reliable daily workflows.",
                    category=cat,
                    price=price,
                    currency="USD",
                    availability=True,
                    stock_count=45 + (p_idx % 30),
                    shipping_cost=ship,
                    estimated_delivery_days=del_days,
                    return_policy_days=ret_days,
                    warranty_months=war_mo,
                    specifications=specs,
                    rating=round(4.4 + ((p_idx % 6) * 0.1), 1),
                    review_count=35 + (p_idx * 7)
                )
            )
            p_idx += 1

    return products
