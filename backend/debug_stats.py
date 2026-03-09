from statistics_engine import StatisticsEngine

mock_commits = [
    {"author": "Alice", "date": "2023-01-01", "additions": 100, "deletions": 10, "files_changed": ["a.py", "b.py"], "type": "feature", "message": "feat: init"},
    {"author": "Bob", "date": "2023-01-05", "additions": 50, "deletions": 5, "files_changed": ["c.py"], "type": "bugfix", "message": "fix: bug"},
    {"author": "Alice", "date": "2023-01-10", "additions": 600, "deletions": 50, "files_changed": ["d.py", "e.py", "f.py"], "type": "refactor", "message": "refactor: core"},
    {"author": "Alice", "date": "2023-02-01", "additions": 20, "deletions": 2, "files_changed": ["test.py"], "type": "testing", "message": "test: add tests"}
]

print("Testing Impact Score...")
score = StatisticsEngine.compute_impact_score(mock_commits[0])
print(f"Impact: {score}")

print("Testing Bus Factor...")
bf = StatisticsEngine.calculate_bus_factor(mock_commits)
print(f"Bus Factor: {bf}")

print("Testing Maturity Score...")
ms = StatisticsEngine.calculate_maturity_score(mock_commits)
print(f"Maturity: {ms}")

print("Testing Collaboration Score...")
cs = StatisticsEngine.calculate_collaboration_score(mock_commits)
print(f"Collaboration: {cs}")

print("Testing Adaptive Arch Changes...")
arch = StatisticsEngine.detect_architecture_changes(mock_commits)
print(f"Arch changes: {len(arch)}")

print("All tests passed!")
