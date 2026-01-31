import os
import re

def fix_merge_conflicts(file_path):
    """Remove Git merge conflict markers and keep the HEAD version"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has conflicts
        if '<<<<<<< HEAD' not in content:
            return False
        
        # Pattern to match conflict blocks
        # Keeps everything between <<<<<<< HEAD and =======
        # Removes everything between ======= and >>>>>>>
        pattern = r'<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n.*?\r?\n>>>>>>> [^\r\n]+\r?\n'
        
        # Replace conflicts with HEAD version
        fixed_content = re.sub(pattern, r'\1\n', content, flags=re.DOTALL)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_and_fix_conflicts(directory):
    """Recursively find and fix all files with merge conflicts"""
    fixed_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        if 'venv1' in dirs:
            dirs.remove('venv1')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            
        for file in files:
            # Only process text files
            if file.endswith(('.html', '.css', '.js', '.py', '.md', '.txt')):
                file_path = os.path.join(root, file)
                if fix_merge_conflicts(file_path):
                    fixed_files.append(file_path)
                    print(f"Fixed: {file_path}")
    
    return fixed_files

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Scanning directory: {base_dir}")
    print("=" * 60)
    
    fixed = find_and_fix_conflicts(base_dir)
    
    print("=" * 60)
    print(f"\nTotal files fixed: {len(fixed)}")
    for f in fixed:
        print(f"  - {os.path.relpath(f, base_dir)}")
