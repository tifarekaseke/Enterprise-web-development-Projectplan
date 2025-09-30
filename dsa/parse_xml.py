import xml.etree.ElementTree as ET
import re
import json
import os
from datetime import datetime

def parse_momo_xml(xml_path):
    """Parse MoMo SMS XML and extract transaction data"""
    try:
        # Check if file exists
        if not os.path.exists(xml_path):
            print(f"ERROR: File not found: {xml_path}")
            print(f"Absolute path: {os.path.abspath(xml_path)}")
            print(f"Current directory: {os.getcwd()}")
            return []
        
        print(f"Parsing XML from: {xml_path}")
        
        # Parse XML
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        print(f"Root element: {root.tag}")
        print(f"Total SMS count: {root.get('count', 'unknown')}")
        
        transactions = []
        sms_elements = root.findall('sms')
        print(f"Found {len(sms_elements)} SMS elements")
        
        for idx, sms in enumerate(sms_elements, start=1):
            body = sms.get('body', '')
            date = sms.get('date', '')
            
            transaction = {
                "id": idx,
                "type": extract_transaction_type(body),
                "amount": extract_amount(body),
                "currency": "RWF",
                "sender": extract_sender(body),
                "receiver": extract_receiver(body),
                "timestamp": convert_timestamp(date),
                "transaction_id": extract_transaction_id(body),
                "raw_text": body
            }
            
            transactions.append(transaction)
        
        print(f"Successfully parsed {len(transactions)} transactions")
        return transactions
    
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse XML: {e}")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_transaction_type(body):
    """Determine if it's a received payment or sent payment"""
    body_lower = body.lower()
    if 'received' in body_lower:
        return 'received'
    elif 'payment' in body_lower or 'paid' in body_lower:
        return 'sent'
    return 'unknown'

def extract_amount(body):
    """Extract the transaction amount from the body"""
    # Look for patterns like "2000 RWF", "1,000 RWF", "24,900 RWF"
    patterns = [
        r'received\s+([\d,]+(?:\.\d+)?)\s*RWF',  # "received 2000 RWF"
        r'payment of\s+([\d,]+(?:\.\d+)?)\s*RWF',  # "payment of 1,000 RWF"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            return float(amount_str)
    
    return 0.0

def extract_sender(body):
    """Extract sender name from received transactions"""
    # Pattern: "received X RWF from Name (*********013)"
    match = re.search(r'from\s+([^(]+)\s*\(', body, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_receiver(body):
    """Extract receiver name from sent transactions"""
    # Pattern: "payment of X RWF to Name 12345"
    match = re.search(r'to\s+([A-Za-z\s]+)\s+\d', body, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_transaction_id(body):
    """Extract transaction ID from body"""
    # Pattern: "TxId: 73214484437" or "Financial Transaction Id: 76662021700"
    patterns = [
        r'TxId:\s*(\d+)',
        r'Financial Transaction Id:\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, body, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def convert_timestamp(date_ms):
    """Convert millisecond timestamp to readable format"""
    if not date_ms:
        return None
    
    try:
        timestamp = int(date_ms) / 1000  # Convert milliseconds to seconds
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None


# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("MoMo XML Parser")
    print("=" * 50)
    
    # Get XML path
    xml_path = os.environ.get("MOMO_XML", "data/raw/modified_sms_v2.xml")
    
    # Parse the XML
    data = parse_momo_xml(xml_path)
    
    # Check if parsing was successful
    if not data:
        print("\nERROR: No transactions were parsed!")
        print("Please check:")
        print("1. The XML file exists at the specified path")
        print("2. The XML file is properly formatted")
        print("3. The XML contains <sms> elements")
        exit(1)
    
    # Create output directory
    os.makedirs("examples", exist_ok=True)
    
    # Write to JSON
    output_file = "examples/sample_transactions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Successfully wrote {len(data)} transactions to {output_file}")
    
    # Print first transaction as example
    if data:
        print("\n" + "=" * 50)
        print("Example - First Transaction:")
        print("=" * 50)
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
        
        # Print statistics
        received_count = sum(1 for t in data if t['type'] == 'received')
        sent_count = sum(1 for t in data if t['type'] == 'sent')
        total_received = sum(t['amount'] for t in data if t['type'] == 'received')
        total_sent = sum(t['amount'] for t in data if t['type'] == 'sent')
        
        print("\n" + "=" * 50)
        print("Transaction Statistics:")
        print("=" * 50)
        print(f"Total transactions: {len(data)}")
        print(f"Received: {received_count} ({total_received:,.0f} RWF)")
        print(f"Sent: {sent_count} ({total_sent:,.0f} RWF)")
        print(f"Net: {total_received - total_sent:,.0f} RWF")