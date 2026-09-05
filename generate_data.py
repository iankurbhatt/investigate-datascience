import os
import csv
import random
import shutil
from datetime import datetime, timedelta

def generate_fintech_datasets():
    random.seed(42)
    
    # Target directories
    data_dirs = ['data', os.path.join('investigate_pandas', 'data')]
    for d in data_dirs:
        os.makedirs(d, exist_ok=True)
        
    print("Generating comprehensive Fintech datasets...")

    # -------------------------------------------------------------
    # 1. Base Setup & Pools
    # -------------------------------------------------------------
    regions = ['North', 'East', 'South', 'West']
    card_types = ['Visa', 'MasterCard', 'Amex', 'Discover']
    statuses = ['Completed', 'Failed', 'Pending', 'Reversed']
    devices = ['Mobile', 'Desktop', 'ATM', 'POS']
    
    # 1500 core customers, 500 core merchants
    customer_ids = [f"C{random.randint(10000, 99999)}" for _ in range(1500)]
    merchant_ids = [f"M{random.randint(1000, 9999)}" for _ in range(500)]
    
    # Dedup while preserving order
    unique_cust_pool = list(dict.fromkeys(customer_ids))
    unique_merch_pool = list(dict.fromkeys(merchant_ids))
    
    # -------------------------------------------------------------
    # 2. Generate raw_transactions.csv (15,000 rows)
    # -------------------------------------------------------------
    start_date = datetime(2025, 1, 1)
    tx_rows = []
    num_duplicates = 100
    num_unique_tx = 15000 - num_duplicates
    
    tx_dict = {} # tx_id -> {cust_id, merch_id, amount, date, status}
    
    for i in range(num_unique_tx):
        tx_id = f"TX{100000 + i}"
        cust_id = random.choice(unique_cust_pool)
        merch_id = random.choice(unique_merch_pool)
        
        # Missing values (approx 5% chance)
        if random.random() < 0.05:
            amount_val = "NaN"
            numeric_amount = None
        else:
            numeric_amount = round(random.uniform(5.0, 2000.0), 2)
            amount_val = numeric_amount
            
        card = random.choice(card_types)
        status = random.choice(statuses)
        device = random.choice(devices)
        age = random.randint(0, 120)
        
        days_offset = random.randint(0, 500)
        date_val = start_date + timedelta(days=days_offset)
        
        # Realistic date string format variations
        fmt_choice = random.choice(['YYYY-MM-DD', 'DD/MM/YYYY', 'MM-DD-YYYY', 'DD-MMM-YYYY', 'ISO-TS'])
        if fmt_choice == 'YYYY-MM-DD':
            date_str = date_val.strftime('%Y-%m-%d')
        elif fmt_choice == 'DD/MM/YYYY':
            date_str = date_val.strftime('%d/%m/%Y')
        elif fmt_choice == 'MM-DD-YYYY':
            date_str = date_val.strftime('%m-%d-%Y')
        elif fmt_choice == 'DD-MMM-YYYY':
            date_str = date_val.strftime('%d-%b-%Y')
        else:
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            date_val_with_time = date_val.replace(hour=hour, minute=minute, second=second)
            date_str = date_val_with_time.strftime('%Y-%m-%d %H:%M:%S')
            
        region = random.choice(regions)
        if random.random() < 0.02:
            region = region.lower()
        elif random.random() < 0.02:
            region = f" {region} "
            
        is_fraud = 0
        if isinstance(numeric_amount, float):
            if numeric_amount > 1800.0 and random.random() < 0.8:
                is_fraud = 1
            elif status == 'Failed' and numeric_amount > 1500.0 and random.random() < 0.5:
                is_fraud = 1
        if random.random() < 0.01:
            is_fraud = 1
            
        tx_row = [tx_id, cust_id, merch_id, amount_val, card, status, device, age, date_str, region, is_fraud]
        tx_rows.append(tx_row)
        
        tx_dict[tx_id] = {
            'customer_id': cust_id,
            'merchant_id': merch_id,
            'amount': numeric_amount if numeric_amount is not None else 100.0,
            'date_val': date_val,
            'status': status,
            'card_type': card,
            'is_fraud': is_fraud
        }
        
    duplicate_rows = random.choices(tx_rows, k=num_duplicates)
    tx_rows.extend(duplicate_rows)
    random.shuffle(tx_rows)
    
    # -------------------------------------------------------------
    # 3. Generate customers.csv (5,000 rows)
    # -------------------------------------------------------------
    # Pool includes all active customers + additional registered users
    extra_customers = [f"C{random.randint(10000, 99999)}" for _ in range(3550)]
    all_customer_pool = list(dict.fromkeys(unique_cust_pool + extra_customers))[:5000]
    
    first_names = [
        'James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda',
        'David', 'Elizabeth', 'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
        'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
        'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
        'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
        'Aarav', 'Priya', 'Liam', 'Emma', 'Mateo', 'Sofia', 'Wei', 'Yuki', 'Amara', 'Carlos'
    ]
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
        'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
        'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
        'Patel', 'Sharma', 'Tanaka', 'Muller', 'Dubois', 'Silva', 'Rossi', 'Kim', 'Chen'
    ]
    email_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'icloud.com', 'proton.me', 'fintechmail.io']
    countries = ['US', 'US', 'US', 'CA', 'GB', 'DE', 'FR', 'AU', 'SG', 'IN']
    us_states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI', 'NJ', 'VA', 'WA', 'AZ', 'MA']
    kyc_statuses = ['Verified', 'Verified', 'Verified', 'Pending', 'Under Review', 'Rejected']
    risk_tiers = ['Low', 'Low', 'Medium', 'Medium', 'High', 'Critical']
    tiers = ['Standard', 'Silver', 'Gold', 'Platinum', 'VIP']
    
    customer_rows = []
    for c_id in all_customer_pool:
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        domain = random.choice(email_domains)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}@{domain}"
        country = random.choice(countries)
        state = random.choice(us_states) if country == 'US' else 'N/A'
        kyc = random.choice(kyc_statuses)
        risk = random.choice(risk_tiers)
        
        # Credit score: 300 to 850, ~3% missing (unbanked)
        if random.random() < 0.03:
            credit_score = ""
        else:
            credit_score = random.randint(350, 850)
            
        income = random.randint(22000, 320000)
        account_balance = round(random.uniform(50.0, 75000.0), 2)
        
        created_days_ago = random.randint(30, 2000)
        created_date = (datetime(2025, 1, 1) - timedelta(days=created_days_ago)).strftime('%Y-%m-%d')
        tier = random.choice(tiers)
        has_crypto = 1 if random.random() < 0.28 else 0
        is_pep = 1 if random.random() < 0.015 else 0
        
        customer_rows.append([
            c_id, fn, ln, email, country, state, kyc, risk,
            credit_score, income, account_balance, created_date, tier, has_crypto, is_pep
        ])

    # -------------------------------------------------------------
    # 4. Generate merchants.csv (2,000 rows)
    # -------------------------------------------------------------
    extra_merchants = [f"M{random.randint(1000, 9999)}" for _ in range(1600)]
    all_merchant_pool = list(dict.fromkeys(unique_merch_pool + extra_merchants))[:2000]
    
    categories = [
        ('E-Commerce & Marketplaces', 5311, 0.024, 'Moderate'),
        ('Food & Dining', 5812, 0.019, 'Low'),
        ('Travel & Airlines', 4511, 0.028, 'High'),
        ('Grocery & Supermarket', 5411, 0.015, 'Low'),
        ('Crypto & Digital Assets', 6051, 0.038, 'Extreme'),
        ('Gaming & Virtual Goods', 7995, 0.032, 'High'),
        ('Electronics & Computers', 5732, 0.022, 'Moderate'),
        ('Healthcare & Wellness', 8099, 0.018, 'Low'),
        ('Financial Services & SaaS', 5999, 0.025, 'Moderate')
    ]
    
    merchant_prefixes = [
        'Apex', 'Quantum', 'Nova', 'Cyber', 'Starlight', 'Hyper', 'Swift', 'Prime',
        'Vanguard', 'Alpha', 'Nexus', 'Vertex', 'Zenith', 'Summit', 'Global', 'Beacon',
        'Titan', 'Pulse', 'Aero', 'Horizon', 'BlueSky', 'SilverLine', 'Velocity', 'Pioneer'
    ]
    merchant_suffixes = [
        'Pay', 'Mart', 'Direct', 'Hub', 'Express', 'Holdings', 'Store', 'Ventures',
        'Cloud', 'Retail', 'Logistics', 'Tech', 'Solutions', 'Air', 'Foods', 'Cafe'
    ]
    
    merchant_rows = []
    for m_id in all_merchant_pool:
        cat_info = random.choice(categories)
        cat_name, mcc, base_fee, default_risk = cat_info
        
        name = f"{random.choice(merchant_prefixes)} {random.choice(merchant_suffixes)}"
        fee_pct = round(base_fee + random.uniform(-0.003, 0.005), 4)
        m_country = random.choice(countries)
        risk = default_risk if random.random() < 0.85 else random.choice(['Low', 'Moderate', 'High', 'Extreme'])
        
        onboard_days = random.randint(100, 1800)
        onboard_date = (datetime(2025, 1, 1) - timedelta(days=onboard_days)).strftime('%Y-%m-%d')
        settlement_days = random.choice([1, 1, 2, 2, 3, 7])
        chargeback_monitored = 1 if risk in ['High', 'Extreme'] and random.random() < 0.35 else 0
        monthly_volume_est = round(random.uniform(10000.0, 2500000.0), 2)
        
        merchant_rows.append([
            m_id, name, cat_name, mcc, m_country, fee_pct,
            risk, onboard_date, settlement_days, chargeback_monitored, monthly_volume_est
        ])

    # -------------------------------------------------------------
    # 5. Generate disputes.csv (10,000 rows)
    # -------------------------------------------------------------
    # Disputes linked to raw_transactions + some external dispute records
    dispute_reasons = [
        'Fraudulent Transaction',
        'Item Not Received',
        'Product Defective / Unacceptable',
        'Duplicate Processing',
        'Subscription Cancelled',
        'Credit Not Processed',
        'Friendly Fraud / Unrecognized'
    ]
    dispute_statuses = [
        'Won - Merchant',
        'Won - Customer',
        'Under Review',
        'Arbitration',
        'Chargeback Reversed',
        'Pending Evidence'
    ]
    liabilities = ['Merchant', 'Cardholder', 'Issuing Bank', 'Payment Processor']
    chargeback_fees = [15.00, 20.00, 25.00, 35.00, 50.00]
    
    dispute_rows = []
    tx_ids_list = list(tx_dict.keys())
    
    # 10,000 dispute records
    for d_idx in range(10000):
        dsp_id = f"DSP{200000 + d_idx}"
        
        # 70% of disputes link directly to existing raw_transactions, 30% are external historical
        if d_idx < 7000 and random.random() < 0.9:
            sampled_tx_id = random.choice(tx_ids_list)
            meta = tx_dict[sampled_tx_id]
            linked_tx_id = sampled_tx_id
            c_id = meta['customer_id']
            m_id = meta['merchant_id']
            tx_amt = meta['amount']
            tx_dt = meta['date_val']
            # If transaction had is_fraud=1, higher chance of Fraudulent Transaction reason
            if meta['is_fraud'] == 1 and random.random() < 0.75:
                reason = 'Fraudulent Transaction'
            else:
                reason = random.choice(dispute_reasons)
        else:
            linked_tx_id = f"TX{random.randint(200000, 299999)}"
            c_id = random.choice(all_customer_pool)
            m_id = random.choice(all_merchant_pool)
            tx_amt = round(random.uniform(20.0, 1500.0), 2)
            tx_dt = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 450))
            reason = random.choice(dispute_reasons)
            
        # Dispute filed between 2 to 45 days after transaction
        dispute_date_val = tx_dt + timedelta(days=random.randint(2, 45))
        dispute_date_str = dispute_date_val.strftime('%Y-%m-%d')
        
        # Disputed amount: partial (e.g. 50%) or full amount
        if random.random() < 0.15:
            disputed_amt = round(tx_amt * random.uniform(0.3, 0.9), 2)
        else:
            disputed_amt = round(tx_amt, 2)
            
        status = random.choice(dispute_statuses)
        evidence = 1 if status in ['Won - Merchant', 'Won - Customer', 'Arbitration'] or random.random() < 0.6 else 0
        cb_fee = random.choice(chargeback_fees)
        
        if status in ['Won - Merchant', 'Won - Customer', 'Arbitration', 'Chargeback Reversed']:
            res_days = random.randint(7, 60)
            res_date_str = (dispute_date_val + timedelta(days=res_days)).strftime('%Y-%m-%d')
            if status == 'Won - Merchant':
                liability = 'Cardholder' if random.random() < 0.8 else 'Issuing Bank'
            elif status == 'Won - Customer':
                liability = 'Merchant' if random.random() < 0.85 else 'Payment Processor'
            else:
                liability = random.choice(liabilities)
        else:
            res_date_str = "" # Still pending / open
            liability = "Pending"
            
        dispute_rows.append([
            dsp_id, linked_tx_id, c_id, m_id, dispute_date_str, reason,
            disputed_amt, status, evidence, cb_fee, res_date_str, liability
        ])

    # -------------------------------------------------------------
    # 6. Generate kyc_audit_records.psv (4,500 rows)
    # -------------------------------------------------------------
    doc_types = ['PASSPORT', 'DRIVERS_LICENSE', 'NATIONAL_ID', 'RESIDENCE_PERMIT']
    vendors = ['Jumio', 'Onfido', 'Veriff', 'Trulioo', 'IDnow']
    flags_pool = ['CLEAR', 'CLEAR', 'CLEAR', 'ADDRESS_MISMATCH_WARN', 'PEP_HIT;SANCTION_CLEAR', 'TAMPERED_DOC_SUSPECTED', 'HIGH_RISK_GEO;SUSPICIOUS_IP', 'EXPIRED_DOC']
    
    kyc_psv_lines = [
        "# REGULATORY KYC AUDIT EXPORT",
        "# FORMAT: PSV (PIPE DELIMITED)",
        "# SOURCE: COMPLIANCE_MAIN_DB",
        "verification_id|customer_id|document_type|id_number_masked|verification_vendor|confidence_score|facial_match_pct|screening_flags|verified_timestamp"
    ]
    for idx, c_id in enumerate(all_customer_pool[:4500]):
        v_id = f"KYC-{10000 + idx}"
        doc = random.choice(doc_types)
        mask_num = f"{doc[:4]}-****-{random.randint(100, 999)}"
        vendor = random.choice(vendors)
        conf = round(random.uniform(0.35, 0.99), 2)
        face_match = round(random.uniform(30.0, 99.9), 1)
        flags = random.choice(flags_pool)
        v_date = (datetime(2025, 1, 1) - timedelta(days=random.randint(10, 1200))).strftime('%Y-%m-%d %H:%M:%S')
        kyc_psv_lines.append(f"{v_id}|{c_id}|{doc}|{mask_num}|{vendor}|{conf}|{face_match}|{flags}|{v_date}")

    # -------------------------------------------------------------
    # 7. Generate device_telemetry.jsonl (8,000 lines)
    # -------------------------------------------------------------
    os_choices = [
        ('iOS', ['16.5', '16.7', '17.0', '17.2', '17.4']),
        ('Android', ['11.0', '12.0', '13.0', '14.0']),
        ('Windows', ['10.0', '11.0']),
        ('MacOS', ['13.5', '14.1', '14.2']),
        ('Linux', ['5.15', '6.2', '6.5'])
    ]
    app_vers = ['5.0.0', '5.0.8', '5.1.0', '5.1.2', 'Web-Portal']
    networks = ['5G', '4G', 'WiFi', 'Ethernet', '3G', 'Tor-Proxy']
    
    jsonl_lines = []
    import json
    for i in range(8000):
        c_id = random.choice(all_customer_pool)
        chosen_os, vers_list = random.choice(os_choices)
        entry = {
            "session_id": f"SES-{100000 + i}",
            "customer_id": c_id,
            "device_os": chosen_os,
            "os_version": random.choice(vers_list),
            "battery_level": None if chosen_os in ['Windows', 'Linux', 'MacOS'] else round(random.uniform(0.05, 1.0), 2),
            "is_rooted_jailbroken": True if (chosen_os in ['Android', 'iOS', 'Linux'] and random.random() < 0.04) else False,
            "app_version": random.choice(app_vers),
            "network_type": random.choice(networks),
            "latency_ms": random.randint(15, 600)
        }
        jsonl_lines.append(json.dumps(entry))

    # -------------------------------------------------------------
    # 8. Generate api_event_logs.json (3,000 events)
    # -------------------------------------------------------------
    event_types = ['LOGIN_ATTEMPT', 'PASSWORD_RESET', 'CARD_PIN_CHANGE', 'BENEFICIARY_ADDED', 'LIMIT_INCREASE_REQUEST', 'WALLET_SYNC', 'UNRECOGNIZED_DEVICE', 'API_KEY_GENERATED', 'FAILED_PASSWORD_STREAK']
    api_events = []
    for i in range(3000):
        c_id = random.choice(all_customer_pool)
        ev_type = random.choice(event_types)
        risk_score = round(random.uniform(0.02, 0.99), 2)
        mfa_prompt = True if risk_score > 0.40 else False
        mfa_pass = True if (mfa_prompt and risk_score < 0.80) else False
        
        event_obj = {
            "event_id": f"EVT-{10000 + i}",
            "customer_id": c_id,
            "event_type": ev_type,
            "timestamp": (datetime(2026, 1, 1) + timedelta(minutes=random.randint(1, 80000))).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "client_info": {
                "ip_address": f"{random.randint(24, 220)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "user_agent": f"FintechClient/{random.choice(['iOS', 'Android', 'Web'])}",
                "location": {
                    "country": random.choice(countries),
                    "city": random.choice(['New York', 'London', 'Frankfurt', 'Mumbai', 'Tokyo', 'Toronto', 'Sydney', 'Paris', 'Sao Paulo']),
                    "is_vpn": True if random.random() < 0.15 else False
                }
            },
            "security_flags": {
                "mfa_prompted": mfa_prompt,
                "mfa_passed": mfa_pass,
                "risk_score": risk_score
            }
        }
        api_events.append(event_obj)
        
    api_json_payload = {
        "api_version": "v2.4",
        "extracted_at": "2026-03-01T12:00:00Z",
        "status": "success",
        "pagination": {
            "total_records": len(api_events),
            "page": 1,
            "has_more": False
        },
        "data": api_events
    }

    # -------------------------------------------------------------
    # 9. Generate fx_rates_daily.tsv (2,000 rows)
    # -------------------------------------------------------------
    fx_pairs = [
        ('USD', 'EUR', 0.9200, 0.0004),
        ('USD', 'GBP', 0.7850, 0.0005),
        ('USD', 'INR', 83.1000, 0.0500),
        ('USD', 'JPY', 144.5000, 0.1500),
        ('USD', 'CAD', 1.3500, 0.0008),
        ('USD', 'AUD', 1.5200, 0.0010),
        ('USD', 'CHF', 0.8800, 0.0005),
        ('USD', 'SGD', 1.3400, 0.0006)
    ]
    fx_tsv_lines = ["rate_date\tbase_currency\tquote_currency\tspot_rate\tbid_rate\task_rate\tcentral_bank_fixing"]
    fx_start = datetime(2025, 1, 1)
    for day in range(250):
        current_d = (fx_start + timedelta(days=day)).strftime('%Y-%m-%d')
        for base, quote, mid_base, spread in fx_pairs:
            fluct = random.uniform(-0.03, 0.03) * mid_base
            spot = round(mid_base + fluct, 4)
            bid = round(spot - spread, 4)
            ask = round(spot + spread, 4)
            fixing = round((bid + ask) / 2, 4)
            fx_tsv_lines.append(f"{current_d}\t{base}\t{quote}\t{spot}\t{bid}\t{ask}\t{fixing}")

    # -------------------------------------------------------------
    # 10. Generate credit_bureau_scores.xml (4,000 rows)
    # -------------------------------------------------------------
    xml_reports = ['<?xml version="1.0" encoding="UTF-8"?>\n<credit_bureau_pulls export_date="2026-03-01">']
    bureaus = ['Experian', 'Equifax', 'TransUnion']
    for idx, c_id in enumerate(all_customer_pool[:4000]):
        p_id = f"PULL-{10000 + idx}"
        b_name = random.choice(bureaus)
        fico = random.randint(350, 850)
        delinq = random.randint(0, 5) if fico < 650 else 0
        util = round(random.uniform(2.0, 98.0) if fico < 680 else random.uniform(1.0, 35.0), 1)
        inq = random.randint(0, 8) if fico < 620 else random.randint(0, 2)
        bk = 1 if fico < 500 and random.random() < 0.25 else 0
        c_age = round(random.uniform(1.0, 25.0), 1)
        
        xml_reports.append(f"  <report>\n    <pull_id>{p_id}</pull_id>\n    <customer_id>{c_id}</customer_id>\n    <bureau_name>{b_name}</bureau_name>\n    <fico_score_8>{fico}</fico_score_8>\n    <delinquency_count_24m>{delinq}</delinquency_count_24m>\n    <revolving_utilization_pct>{util}</revolving_utilization_pct>\n    <hard_inquiries_12m>{inq}</hard_inquiries_12m>\n    <bankruptcy_flag>{bk}</bankruptcy_flag>\n    <credit_age_years>{c_age}</credit_age_years>\n  </report>")
    xml_reports.append('</credit_bureau_pulls>')

    # -------------------------------------------------------------
    # 11. Generate ach_clearing_settlement.dat (5,000 rows fixed-width)
    # -------------------------------------------------------------
    fwf_lines = [f"{'TXN_BATCH_ID':<19}{'CUST_ID':<11}{'TRANS_TYPE':<12}{'SETTLEMENT_USD':<15}{'ROUTING_NUM':<12}{'ACC_STATUS'}"]
    ach_types = ['DEBIT', 'CREDIT']
    ach_statuses = ['SETTLED', 'SETTLED', 'SETTLED', 'SETTLED', 'RETURNED_NSF', 'RETURNED_ACT_CLOSED', 'SUSPENDED_AML']
    for i in range(5000):
        batch_id = f"ACH-20260301-{1000 + i}"
        c_id = random.choice(all_customer_pool)
        t_type = random.choice(ach_types)
        amount_val = f"{random.uniform(10.0, 25000.0):011.2f}"
        routing = f"{random.randint(10000000, 99999999):09d}"
        status_val = random.choice(ach_statuses)
        fwf_lines.append(f"{batch_id:<19}{c_id:<11}{t_type:<12}{amount_val:<15}{routing:<12}{status_val}")

    # -------------------------------------------------------------
    # 12. Write all files to both target folders
    # -------------------------------------------------------------
    for target_dir in data_dirs:
        # 1. raw_transactions.csv
        raw_tx_path = os.path.join(target_dir, 'raw_transactions.csv')
        with open(raw_tx_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'transaction_id', 'customer_id', 'merchant_id', 'transaction_amount',
                'card_type', 'transaction_status', 'device_type', 'account_age_months',
                'transaction_date', 'region', 'is_fraud'
            ])
            writer.writerows(tx_rows)
            
        # 2. customers.csv
        cust_path = os.path.join(target_dir, 'customers.csv')
        with open(cust_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'customer_id', 'first_name', 'last_name', 'email', 'country_code',
                'state_province', 'kyc_status', 'risk_tier', 'credit_score',
                'annual_income', 'account_balance', 'account_created_at',
                'account_tier', 'has_crypto_wallet', 'is_pep'
            ])
            writer.writerows(customer_rows)
            
        # 3. merchants.csv
        merch_path = os.path.join(target_dir, 'merchants.csv')
        with open(merch_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'merchant_id', 'merchant_name', 'category', 'mcc_code', 'country_code',
                'interchange_fee_pct', 'risk_rating', 'onboarding_date',
                'payout_settlement_days', 'is_chargeback_monitored', 'monthly_volume_est'
            ])
            writer.writerows(merchant_rows)
            
        # 4. disputes.csv
        disp_path = os.path.join(target_dir, 'disputes.csv')
        with open(disp_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'dispute_id', 'transaction_id', 'customer_id', 'merchant_id',
                'dispute_date', 'dispute_reason', 'disputed_amount', 'dispute_status',
                'evidence_submitted', 'chargeback_fee_usd', 'resolution_date', 'liability_assigned'
            ])
            writer.writerows(dispute_rows)

        # 5. kyc_audit_records.psv
        with open(os.path.join(target_dir, 'kyc_audit_records.psv'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(kyc_psv_lines) + '\n')

        # 6. device_telemetry.jsonl
        with open(os.path.join(target_dir, 'device_telemetry.jsonl'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(jsonl_lines) + '\n')

        # 7. api_event_logs.json
        with open(os.path.join(target_dir, 'api_event_logs.json'), 'w', encoding='utf-8') as f:
            json.dump(api_json_payload, f, indent=2)

        # 8. fx_rates_daily.tsv
        with open(os.path.join(target_dir, 'fx_rates_daily.tsv'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(fx_tsv_lines) + '\n')

        # 9. credit_bureau_scores.xml
        with open(os.path.join(target_dir, 'credit_bureau_scores.xml'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_reports) + '\n')

        # 10. ach_clearing_settlement.dat
        with open(os.path.join(target_dir, 'ach_clearing_settlement.dat'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(fwf_lines) + '\n')
            
        print(f"-> Successfully generated in '{target_dir}':")
        print(f"   - raw_transactions.csv     : {len(tx_rows):,} rows")
        print(f"   - customers.csv            : {len(customer_rows):,} rows")
        print(f"   - merchants.csv            : {len(merchant_rows):,} rows")
        print(f"   - disputes.csv             : {len(dispute_rows):,} rows")
        print(f"   - kyc_audit_records.psv    : {len(kyc_psv_lines)-4:,} rows")
        print(f"   - device_telemetry.jsonl   : {len(jsonl_lines):,} rows")
        print(f"   - api_event_logs.json      : {len(api_events):,} records")
        print(f"   - fx_rates_daily.tsv       : {len(fx_tsv_lines)-1:,} rows")
        print(f"   - credit_bureau_scores.xml : {len(xml_reports)-2:,} reports")
        print(f"   - ach_clearing_settlement.dat: {len(fwf_lines)-1:,} rows")

if __name__ == '__main__':
    generate_fintech_datasets()

