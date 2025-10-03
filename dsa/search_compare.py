# dsa/search_compare.py
import time, random, json # stdlib only

def linear_find(records, target_id): 
    for rec in records: 
        if rec["id"] == target_id:
            return rec 
    return None

def dict_find(index, target_id): # index is a dict mapping id -> record
    return index.get(target_id) # O(1) expected-time lookup 

if __name__ == "__main__":
    # Load what parse_xml produced (or fabricate ~20 if file missing)
    try:
        with open("examples/json_schemas.json", "r", encoding="utf-8") as f:
            data = json.load(f) 
    except FileNotFoundError: # fabricate some data to test the search performance
        data = [{"id": i+1, "type":"PAY","amount":100+i,"currency":"RWF","sender":"A","receiver":"B","timestamp":"2025-09-01T00:00:00","raw_text":""} for i in range(25)] # 25 sample records

    index = {int(r["id"]): r for r in data} 
    ids = [int(r["id"]) for r in data] 
    random_ids = [random.choice(ids) for _ in range(1000)] # 1000 random ids to lookup 

    t0 = time.perf_counter() 
    for tid in random_ids: 
        _ = linear_find(data, tid)
    t1 = time.perf_counter() 

    for tid in random_ids:
        _ = dict_find(index, tid)
    t2 = time.perf_counter() 

    print(f"Linear search took: {(t1 - t0)*1000:.3f} ms for {len(random_ids)} lookups")
    print(f"Dict lookup took:   {(t2 - t1)*1000:.3f} ms for {len(random_ids)} lookups")
    print("Dict is faster on average because it uses hash table O(1) expected-time lookups,\n"
          "while linear scan is O(n) and scales poorly as records grow.")
    