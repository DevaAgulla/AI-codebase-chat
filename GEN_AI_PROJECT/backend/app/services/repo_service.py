"""Service for cloning and analyzing GitHub repositories."""
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import gitignore_parser
from app.config import settings


class RepoService:
    """Service for handling GitHub repository operations."""
    
    def __init__(self):
        self.max_file_size_bytes = settings.max_file_size_kb * 1024
        self.max_files = settings.max_files
        self.max_total_chars = settings.max_total_chars
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return True
    
    def _should_ignore_file(self, file_path: Path, gitignore_rules) -> bool:
        """Check if file should be ignored based on .gitignore."""
        if gitignore_rules:
            return gitignore_rules(file_path)
        return False
    
    def _get_gitignore_rules(self, repo_path: Path) -> Optional[callable]:
        """Load .gitignore rules if present."""
        gitignore_path = repo_path / '.gitignore'
        if gitignore_path.exists():
            try:
                return gitignore_parser.parse_gitignore(gitignore_path)
            except Exception:
                return None
        return None
    
    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code/config file worth analyzing."""
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.sass', '.json', '.yaml', '.yml',
            '.toml', '.xml', '.sql', '.sh', '.bash', '.zsh', '.ps1',
            '.md', '.txt', '.env', '.config', '.conf', '.ini'
        }
        
        # Check extension
        if file_path.suffix.lower() in code_extensions:
            return True
        
        # Check common config files without extension
        config_files = {
            'dockerfile', 'makefile', '.gitignore', '.env.example',
            'package.json', 'requirements.txt', 'pom.xml', 'build.gradle',
            'cargo.toml', 'go.mod', 'composer.json', 'gemfile'
        }
        
        return file_path.name.lower() in config_files
    
    def _build_tree_structure(self, repo_path: Path, gitignore_rules) -> str:
        """Build a text representation of the folder structure."""
        lines = []
        
        def build_tree(path: Path, prefix: str = "", is_last: bool = True):
            """Recursively build tree structure."""
            if path.name.startswith('.') and path.name != '.gitignore':
                return
            
            if path.is_dir():
                # Skip common ignored directories
                if path.name in ['node_modules', '__pycache__', '.git', '.venv', 'venv', 'dist', 'build', '.next']:
                    return
                
                marker = "└── " if is_last else "├── "
                lines.append(f"{prefix}{marker}{path.name}/")
                
                try:
                    children = sorted([p for p in path.iterdir() if not self._should_ignore_file(p, gitignore_rules)])
                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        extension = "    " if is_last else "│   "
                        build_tree(child, prefix + extension, is_last_child)
                except PermissionError:
                    pass
            else:
                if self._is_code_file(path):
                    marker = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{marker}{path.name}")
        
        build_tree(repo_path)
        return "\n".join(lines)
    
    def clone_repo(self, repo_url: str, branch: Optional[str] = None) -> Path:
        """Clone a GitHub repository to a temporary directory."""
        # Validate GitHub URL
        if not repo_url.startswith(('https://github.com/', 'http://github.com/', 'git@github.com:')):
            raise ValueError("Invalid GitHub URL. Must be a GitHub repository URL.")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="codebase_explainer_")
        repo_path = Path(temp_dir)
        
        try:
            # Build git clone command
            cmd = ['git', 'clone', '--depth', '1']
            
            if branch:
                cmd.extend(['-b', branch])
            
            # Add token if available for private repos
            if settings.github_token:
                # Modify URL to include token
                if 'https://' in repo_url:
                    repo_url = repo_url.replace('https://', f'https://{settings.github_token}@')
            
            cmd.append(repo_url)
            cmd.append(str(repo_path))
            
            # Execute clone with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.clone_timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if '404' in error_msg or 'not found' in error_msg.lower():
                    raise ValueError(f"Repository not found: {repo_url}")
                elif 'permission' in error_msg.lower() or 'authentication' in error_msg.lower():
                    raise ValueError("Repository is private or authentication failed. Set GITHUB_TOKEN for private repos.")
                else:
                    raise ValueError(f"Failed to clone repository: {error_msg}")
            
            # Git clone behavior: if target exists, clones into it; otherwise creates subdirectory
            # Check if .git exists in repo_path (cloned directly)
            if (repo_path / '.git').exists():
                return repo_path
            
            # Otherwise, find the subdirectory git created
            subdirs = [d for d in repo_path.iterdir() if d.is_dir() and d.name != '.git']
            if subdirs:
                return subdirs[0]
            
            # Fallback to repo_path
            return repo_path
            
        except subprocess.TimeoutExpired:
            raise ValueError(f"Repository clone timed out after {settings.clone_timeout} seconds")
        except Exception as e:
            # Cleanup on error
            import shutil
            if repo_path.exists():
                shutil.rmtree(repo_path, ignore_errors=True)
            raise
    
    def analyze_repo(self, repo_url: str, branch: Optional[str] = None) -> Dict:
        """Clone and analyze a repository, returning structure and file contents."""
        repo_path = self.clone_repo(repo_url, branch)
        gitignore_rules = self._get_gitignore_rules(repo_path)
        
        try:
            # Build folder structure tree
            tree_structure = self._build_tree_structure(repo_path, gitignore_rules)
            
            # Collect files with content
            files_data = []
            total_chars = 0
            file_count = 0
            
            def collect_files(path: Path):
                nonlocal total_chars, file_count
                
                if file_count >= self.max_files or total_chars >= self.max_total_chars:
                    return
                
                if path.is_file():
                    if not self._is_code_file(path):
                        return
                    
                    if self._should_ignore_file(path, gitignore_rules):
                        return
                    
                    if self._is_binary_file(path):
                        return
                    
                    try:
                        file_size = path.stat().st_size
                        if file_size > self.max_file_size_bytes:
                            # Include path but truncate content
                            files_data.append({
                                'path': str(path.relative_to(repo_path)),
                                'content': f"[File too large: {file_size} bytes, truncated]",
                                'truncated': True
                            })
                            return
                        
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            content_chars = len(content)
                            
                            if total_chars + content_chars > self.max_total_chars:
                                # Truncate to fit
                                remaining = self.max_total_chars - total_chars
                                content = content[:remaining] + "\n[Truncated due to token limit]"
                            
                            files_data.append({
                                'path': str(path.relative_to(repo_path)),
                                'content': content,
                                'truncated': False
                            })
                            
                            total_chars += len(content)
                            file_count += 1
                            
                    except Exception:
                        # Skip files that can't be read
                        pass
                
                elif path.is_dir():
                    # Skip ignored directories
                    if path.name in ['node_modules', '__pycache__', '.git', '.venv', 'venv', 'dist', 'build', '.next']:
                        return
                    
                    try:
                        for child in path.iterdir():
                            if file_count >= self.max_files or total_chars >= self.max_total_chars:
                                break
                            collect_files(child)
                    except PermissionError:
                        pass
            
            # Start collecting from repo root
            for item in repo_path.iterdir():
                if file_count >= self.max_files or total_chars >= self.max_total_chars:
                    break
                collect_files(item)
            
            return {
                'tree_structure': tree_structure,
                'files': files_data,
                'total_files': file_count,
                'total_chars': total_chars,
                'repo_path': str(repo_path)
            }
            
        except Exception as e:
            # Cleanup on error
            import shutil
            if repo_path.exists():
                shutil.rmtree(repo_path.parent, ignore_errors=True)
            raise
