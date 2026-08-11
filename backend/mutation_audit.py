import json
import os
import copy
from app.oms.repositories.json_repository import JSONOMSRepository

def compare_dicts(d1, d2, path="root"):
    issues = []
    if not isinstance(d1, dict) or not isinstance(d2, dict):
        if d1 != d2:
            issues.append(f"{path}: Value mismatch {d1} != {d2}")
        return issues
        
    for k in d1:
        new_path = f"{path}.{k}"
        if k not in d2:
            issues.append(f"{new_path}: Field missing in mutated data")
        else:
            if isinstance(d1[k], dict):
                issues.extend(compare_dicts(d1[k], d2[k], new_path))
            elif isinstance(d1[k], list):
                if len(d1[k]) != len(d2[k]):
                    issues.append(f"{new_path}: Array length mismatch {len(d1[k])} != {len(d2[k])}")
                else:
                    for i in range(len(d1[k])):
                        if isinstance(d1[k][i], dict) and isinstance(d2[k][i], dict):
                            issues.extend(compare_dicts(d1[k][i], d2[k][i], f"{new_path}[{i}]"))
                        else:
                            if d1[k][i] != d2[k][i]:
                                issues.append(f"{new_path}[{i}]: Array value mismatch {d1[k][i]} != {d2[k][i]}")
            else:
                if d1[k] != d2[k]:
                    issues.append(f"{new_path}: Value mismatch {d1[k]} != {d2[k]}")
                    
    for k in d2:
        if k not in d1:
            issues.append(f"{path}.{k}: Added field in mutated data")
            
    return issues

def main():
    print("Starting Mutation Audit...")
    file_path = "app/data/crystal-oms-demo.json"
    
    with open(file_path, "r", encoding="utf-8") as f:
        original_json = json.load(f)
        
    # Create repo and perform mutation
    repo = JSONOMSRepository(file_path=file_path)
    
    # Grab the first order id
    first_order_id = repo._orders[0].id
    original_status = repo._orders[0].status
    new_status = "mutated_status_123"
    
    print(f"Mutating order {first_order_id} status from {original_status} to {new_status}")
    
    # Mutate and save
    repo.update_order_status(first_order_id, new_status)
    
    # Reload from disk
    with open(file_path, "r", encoding="utf-8") as f:
        mutated_json = json.load(f)
        
    # We expect EXACTLY one issue: the status field we changed.
    # To check this cleanly, we can temporarily change the original_json in memory to match the expected mutation,
    # then compare. If there are NO issues, the mutation was perfectly isolated!
    
    original_json["oms_orders"][0]["status"] = new_status
    
    issues = compare_dicts(original_json, mutated_json)
    
    # Restore original file state since this is a test
    repo.update_order_status(first_order_id, original_status)
    
    if issues:
        print(f"\\nMUTATION AUDIT FAILED! Found {len(issues)} unexpected differences:")
        for issue in issues[:30]:
            print(issue)
        exit(1)
    else:
        print("\\nMUTATION AUDIT PASSED! All unrelated fields were preserved perfectly.")
        exit(0)

if __name__ == "__main__":
    main()
