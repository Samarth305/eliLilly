import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from commit_analyzer import CommitAnalyzer

test_cases = [
    {"message": "feat: add login system", "expected": "feature"},
    {"message": "fix: handle null pointer", "expected": "bugfix"},
    {"message": "refactor: simplify auth logic", "expected": "refactor"},
    {"message": "perf: cache db queries", "expected": "performance"},
    {"message": "test: add unit tests", "expected": "testing"},
    {"message": "docs: update README", "expected": "documentation"},
    {"message": "chore: format code", "expected": "chore"},
    {"message": "security: sanitize input", "expected": "security"},
    {"message": "init project", "expected": "feature"},
    {"message": "upgrade deps", "expected": "dependency"},
    {"message": "k8s: add deployment config", "expected": "infrastructure"},
    {"message": "cleanup unused variables", "expected": "refactor"},
    {"message": "feat(auth): enable oauth2", "expected": "feature"},
    {"message": "fix(api): error in endpoint", "expected": "bugfix"},
    {"message": "removing dead code", "expected": "removal"},
]

def run_tests():
    passed = 0
    failed = 0
    for case in test_cases:
        result = CommitAnalyzer.classify_commit({"message": case["message"], "files": [], "additions": 0, "deletions": 0})
        if result["category"] == case["expected"]:
            print(f"✅ PASS: '{case['message']}' -> {result['category']}")
            passed += 1
        else:
            print(f"❌ FAIL: '{case['message']}' -> Expected {case['expected']}, got {result['category']} (Confidence: {result['confidence']})")
            failed += 1
    
    print(f"\nSummary: {passed} passed, {failed} failed")

if __name__ == "__main__":
    run_tests()
