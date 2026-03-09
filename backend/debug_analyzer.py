from contributor_analyzer import ContributorAnalyzer
import json

# Mock commits matching CommitAnalyzer.extract_summary output
mock_commits = [
    {
        "sha": "sha1",
        "message": "initial commit",
        "author": "Alice",
        "date": "2023-01-01T10:00:00Z",
        "files": [{"filename": "auth/login.py"}],
        "files_changed": ["auth/login.py"],
        "additions": 100,
        "deletions": 10,
        "is_merge": False
    },
    {
        "sha": "sha2",
        "message": "add api",
        "author": "Bob",
        "date": "2023-01-05T12:00:00Z",
        "files": [{"filename": "api/routes.py"}],
        "files_changed": ["api/routes.py"],
        "additions": 50,
        "deletions": 5,
        "is_merge": False
    }
]

print("Running ContributorAnalyzer...")
try:
    results = ContributorAnalyzer.analyze(mock_commits)
    print("Results:")
    print(json.dumps(results, indent=2))
except Exception as e:
    import traceback
    print("Error during analysis:")
    traceback.print_exc()
