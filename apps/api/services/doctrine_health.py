"""Doctrine health scanning and thinness detection."""

import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta


class DoctrineHealthService:
    """Scans markdown files in core/, context/, and skills/ directories."""
    
    # Word count minimums per file or file type
    MINIMUMS = {
        "core/VOICE.md": 1500,
        "core/STYLE_GUIDE.md": 800,
        "core/CLAIMS_POLICY.md": 600,
        "core/BRAND_VOICE.md": 800,
        "core/CONTENT_STRATEGY.md": 800,
        "core/CONTEXT.md": 500,
        "core/DEVELOPER_FLUENCY.md": 600,
        "core/DISTRIBUTION_STRATEGY.md": 800,
        "core/EDITORIAL_PRINCIPLES.md": 600,
        "core/GOVERNANCE.md": 400,
        "context/02_narrative/messaging-framework.md": 1500,
        "context/02_narrative/competitive-pov.md": 1000,
        "context/02_narrative/campaign-messaging.md": 800,
        "context/02_narrative/technical-messaging-case-study.md": 600,
        "context/03_strategy/content-strategy.md": 1500,
        "context/03_strategy/ar-strategy.md": 800,
        "context/03_strategy/content-strategy-framework.md": 800,
        "context/03_strategy/strategy-blueprint.md": 600,
        "context/03_strategy/post-gtm-blueprint.md": 600,
        "context/04_execution/post-launch-framework.md": 600,
        "context/04_execution/campaign-blueprint.md": 600,
        "context/04_execution/campaign-brief.md": 500,
        "context/04_execution/gtm-operating-system.md": 800,
        "context/05_patterns/developer-ads.md": 600,
        "context/05_patterns/landing-pages.md": 600,
        "context/05_patterns/workflows.md": 600,
        "context/06_influence/analyst-relations-playbook.md": 800,
        "context/07_research/intelligence-scoring-prompt.md": 500,
        "context/07_research/market-research-playbook.md": 800,
    }
    
    # Default minimums for files not explicitly listed
    DEFAULT_MINIMUMS = {
        "core": 800,
        "context": 800,
        "skills": 200,
    }
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.cache = {}
        self.cache_time = None
    
    def get_health_report(self, force_refresh: bool = False) -> Dict:
        """
        Get health report for all doctrine files.
        Caches for 5 minutes.
        
        Returns: {
            "total_files": N,
            "placeholder_count": X,
            "thin_count": Y,
            "files": [{"path": "...", "word_count": N, "recommended": M, "thinness_pct": P, "badge": "..."}],
            "timestamp": "...",
            "cached": bool
        }
        """
        now = datetime.utcnow()
        
        # Use cache if available and not forced refresh
        if self.cache and self.cache_time and not force_refresh:
            if (now - self.cache_time).total_seconds() < 300:  # 5 minute cache
                result = self.cache.copy()
                result["cached"] = True
                return result
        
        # Scan all files
        files = []
        placeholder_count = 0
        thin_count = 0
        
        # Scan core/
        core_path = self.repo_root / "core"
        if core_path.exists():
            for md_file in core_path.glob("*.md"):
                file_info = self._analyze_file(md_file)
                files.append(file_info)
                if file_info["badge"] == "placeholder":
                    placeholder_count += 1
                elif file_info["badge"] == "thin":
                    thin_count += 1
        
        # Scan context/
        context_path = self.repo_root / "context"
        if context_path.exists():
            for md_file in context_path.rglob("*.md"):
                # Skip README
                if md_file.name == "README.md":
                    continue
                file_info = self._analyze_file(md_file)
                files.append(file_info)
                if file_info["badge"] == "placeholder":
                    placeholder_count += 1
                elif file_info["badge"] == "thin":
                    thin_count += 1
        
        # Sort by thinness (placeholders first)
        files.sort(key=lambda f: (f["thinness_pct"], f["path"]))
        
        result = {
            "total_files": len(files),
            "placeholder_count": placeholder_count,
            "thin_count": thin_count,
            "files": files,
            "timestamp": now.isoformat(),
            "cached": False
        }
        
        # Cache result
        self.cache = result.copy()
        self.cache_time = now
        
        return result
    
    def _analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count words (simple split on whitespace)
            word_count = len(content.split())
            
            # Get recommended minimum
            relative_path = str(file_path.relative_to(self.repo_root))
            recommended = self.MINIMUMS.get(relative_path)
            
            if not recommended:
                # Use default based on directory
                if "core" in relative_path:
                    recommended = self.DEFAULT_MINIMUMS["core"]
                elif "context" in relative_path:
                    recommended = self.DEFAULT_MINIMUMS["context"]
                elif "skills" in relative_path:
                    recommended = self.DEFAULT_MINIMUMS["skills"]
                else:
                    recommended = 800
            
            # Calculate thinness percentage
            thinness_pct = (word_count / recommended * 100) if recommended > 0 else 0
            
            # Determine badge
            if thinness_pct < 25:
                badge = "placeholder"
            elif thinness_pct < 75:
                badge = "thin"
            else:
                badge = "complete"
            
            return {
                "path": relative_path,
                "word_count": word_count,
                "recommended": recommended,
                "thinness_pct": round(thinness_pct, 1),
                "badge": badge
            }
        
        except Exception as e:
            return {
                "path": str(file_path.relative_to(self.repo_root)),
                "word_count": 0,
                "recommended": 800,
                "thinness_pct": 0,
                "badge": "error",
                "error": str(e)
            }
    
    def get_highest_leverage_thin_file(self) -> Dict:
        """
        Get the highest-leverage thin or placeholder file.
        Heuristic: file referenced by the most skills/playbooks.
        Currently simplified: just returns the most placeholder file.
        """
        report = self.get_health_report()
        
        # Find first placeholder, else first thin
        for f in report["files"]:
            if f["badge"] == "placeholder":
                return f
        
        for f in report["files"]:
            if f["badge"] == "thin":
                return f
        
        return None
