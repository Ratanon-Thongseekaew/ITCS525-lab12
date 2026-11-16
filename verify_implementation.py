# Run tests to verify the implementation

import subprocess
import sys

def run_tests():
    print("Running tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")  
        print(result.stderr)
    print(f"Return code: {result.returncode}")
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)