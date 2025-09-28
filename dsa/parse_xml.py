# dsa/parse_xml.py
from xml.etree import ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os

def parse_momo_xml(xml_path: str) -> List[Dict[str, Any]]:
    """
    Parse modified_sms_v2.xml into a list of dicts.
    Expected XML shape (example, adapt tags if needed):
      <records>
        <sms id="123">
          <type>PAY</type>
          <amount>2000</amount>
          <currency>RWF</currency>
          <sender>+2507...</sender>
          <receiver>+2507...</receiver>
          <timestamp>2025-09-01 12:30:00</timestamp>
          <raw>original sms text here</raw>
        </sms>
        ...
      </records>
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    out: List[Dict[str, Any]] = []
    for sms in root.findall(".//sms"):
        def _text(tag: str) -> Optional[str]:
            el = sms.find(tag)
            return el.text.strip() if el is not None and el.text else None

        # Create a normalized transaction dict
        rec = {
            "id": sms.get("id") or None,  # keep string id if present; API will coerce to int
            "type": _text("type"),
            "amount": float(_text("amount") or 0),
            "currency": _text("currency") or "RWF",
            "sender": _text("sender"),
            "receiver": _text("receiver"),
            "timestamp": _text("timestamp"),
            "raw_text": _text("raw") or "",
        }
        # try to standardize timestamp (optional)
        try:
            dt = datetime.fromisoformat(rec["timestamp"])
            rec["timestamp"] = dt.isoformat()
        except Exception:
            pass  # leave as-is
        out.append(rec)

    # Ensure every record has an integer id (generate if missing)
    next_id = 1
    for r in out:
        if r["id"] is None:
            r["id"] = next_id
            next_id += 1
        else:
            try:
                r["id"] = int(r["id"])
                next_id = max(next_id, r["id"] + 1)
            except ValueError:
                r["id"] = next_id
                next_id += 1
    return out

if __name__ == "__main__":
    xml_path = os.environ.get("MOMO_XML", "modified_sms_v2.xml")
    data = parse_momo_xml(xml_path)
    os.makedirs("examples", exist_ok=True)
    with open("examples/sample_transactions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(data)} transactions to examples/sample_transactions.json")
