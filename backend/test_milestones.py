import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from milestone_detector import MilestoneDetector
from datetime import datetime, timedelta

def create_mock_commit(date, msg="commit", additions=10, deletions=5, type="feature", files=None, files_changed=None):
    return {
        "sha": "sha123",
        "message": msg,
        "date": date + "Z" if not date.endswith("Z") else date,
        "author": "Alice",
        "additions": additions,
        "deletions": deletions,
        "type": type,
        "files": files or [{"filename": "src/main.py", "status": "modified"}],
        "files_changed": files_changed or ["src/main.py"]
    }

def run_tests():
    print("🚀 Running Milestone Detection Tests...\n")
    
    # Base baseline for stats (10 small commits)
    base_date = datetime(2023, 1, 1)
    commits = [create_mock_commit((base_date + timedelta(days=i)).isoformat()) for i in range(10)]
    
    # 1. Test Architecture Shift (Huge commit affecting many files and dirs)
    arch_commit = create_mock_commit(
        (base_date + timedelta(days=11)).isoformat(),
        additions=5000, deletions=3000,
        files_changed=["src/api/v1.py", "src/db/models.py", "src/ui/main.js", "infra/k8s.yaml", "docs/api.md", "tests/test_api.py", "scripts/deploy.sh", "config/settings.json", "styles/main.css", "utils/helper.py"]
    )
    commits.append(arch_commit)
    
    # 2. Test Module Introduction (5 new files in a new folder)
    for i in range(5):
        commits.append(create_mock_commit(
            (base_date + timedelta(days=20+i)).isoformat(),
            files=[{"filename": f"new_module/file_{i}.py", "status": "added"}]
        ))
        
    # 3. Test Testing Adoption (3 test commits in a month)
    test_month_start = datetime(2023, 3, 1)
    for i in range(3):
        commits.append(create_mock_commit(
            (test_month_start + timedelta(days=i)).isoformat(),
            type="testing"
        ))
        
    # 4. Test Development Burst (Extra commits in a week)
    burst_week_start = datetime(2023, 4, 1)
    for i in range(20): # Burst of 20 commits
        commits.append(create_mock_commit(
            (burst_week_start + timedelta(days=i%7)).isoformat()
        ))
        
    # 5. Test Dependency Migration (3 dep commits in a week)
    dep_week_start = datetime(2023, 5, 1)
    for i in range(3):
        commits.append(create_mock_commit(
            (dep_week_start + timedelta(days=i)).isoformat(),
            type="dependency"
        ))
        
    # 6. Test Change Points (Phase Shift & Slowdown)
    # Week 1-4: Baseline (5 commits/week)
    for w in range(4):
        date = datetime(2023, 6, 1) + timedelta(weeks=w)
        for i in range(5):
            commits.append(create_mock_commit((date + timedelta(days=i)).isoformat()))
            
    # Week 5: Phase Shift (20 commits)
    shift_date = datetime(2023, 6, 1) + timedelta(weeks=4)
    for i in range(20):
        commits.append(create_mock_commit((shift_date + timedelta(days=i % 7)).isoformat()))
        
    # Week 6: Slowdown (2 commits)
    slow_date = datetime(2023, 6, 1) + timedelta(weeks=5)
    for i in range(2):
        commits.append(create_mock_commit((slow_date + timedelta(days=i)).isoformat()))

    milestones = MilestoneDetector.generate_milestones(commits, [])
    
    types_found = [m["type"] for m in milestones]
    print(f"Detected Milestone Types: {types_found}\n")
    
    expected_types = [
        "project_creation", 
        "architecture_shift", 
        "module_introduction", 
        "testing_adoption", 
        "development_burst", 
        "dependency_migration",
        "development_phase_shift",
        "development_slowdown"
    ]
    
    all_passed = True
    for t in expected_types:
        if t in types_found:
            print(f"✅ Found: {t}")
        else:
            print(f"❌ Missing: {t}")
            all_passed = False
            
    if all_passed:
        print("\n✨ ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED.")

if __name__ == "__main__":
    run_tests()
