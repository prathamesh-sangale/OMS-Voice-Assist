import json
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
            issues.append(f"{new_path}: Field missing in re-serialized data")
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
            issues.append(f"{path}.{k}: Added field in re-serialized data")
            
    return issues

def main():
    print("Starting Data Integrity Audit...")
    
    file_path = "app/data/crystal-oms-demo.json"
    with open(file_path, "r", encoding="utf-8") as f:
        original_json = json.load(f)
        
    repo = JSONOMSRepository(file_path=file_path)
    
    # Serialize back using the repo's internal mechanism
    serialized_data = {**repo._metadata}
    serialized_data["oms_orders"] = [order.model_dump(mode="json", exclude_unset=True) for order in repo._orders]
    serialized_data["oms_order_tasks"] = [task.model_dump(mode="json", exclude_unset=True) for task in repo._tasks]
    
    print(f"Original orders count: {len(original_json.get('oms_orders', []))}")
    print(f"Serialized orders count: {len(serialized_data.get('oms_orders', []))}")
    
    issues = compare_dicts(original_json, serialized_data)
    
    if issues:
        print(f"\\nAUDIT FAILED! Found {len(issues)} issues:")
        for issue in issues[:30]:
            print(issue)
        if len(issues) > 30:
            print(f"...and {len(issues) - 30} more.")
        exit(1)
    else:
        print("\\nAUDIT PASSED! All data preserved.")
        exit(0)

if __name__ == "__main__":
    main()
