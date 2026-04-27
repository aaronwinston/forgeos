"""Weekly briefing feedback aggregation and scoring prompt calibration."""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from models import BriefingFeedback
from anthropic import Anthropic
import re


class BriefingAggregationService:
    def __init__(self, session: Session):
        self.session = session
        self.client = Anthropic()
    
    def aggregate_feedback(self, days_back: int = 7) -> dict:
        """
        Aggregate feedback from the last N days and generate a calibration summary.
        Returns: {"summary": "...", "thumbs_up": N, "thumbs_down": M}
        """
        cutoff = datetime.utcnow() - timedelta(days=days_back)
        
        # Query feedback from last N days
        feedback_records = self.session.exec(
            select(BriefingFeedback)
            .where(BriefingFeedback.created_at >= cutoff)
            .order_by(BriefingFeedback.created_at.desc())
        ).all()
        
        if not feedback_records:
            return {
                "summary": None,
                "thumbs_up": 0,
                "thumbs_down": 0,
                "reason": "no_feedback_yet"
            }
        
        # Count feedback types
        thumbs_up = sum(1 for f in feedback_records if f.feedback_type == "thumbs_up")
        thumbs_down = sum(1 for f in feedback_records if f.feedback_type == "thumbs_down")
        
        # If insufficient feedback, skip generation
        if thumbs_up + thumbs_down < 5:
            return {
                "summary": None,
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "reason": "insufficient_feedback"
            }
        
        # Generate summary via Claude
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on this briefing feedback pattern (out of {thumbs_up + thumbs_down} total items):
                    
- {thumbs_up} items rated helpful (👍)
- {thumbs_down} items rated not helpful (👎)

Generate a 1-2 sentence summary of what Aaron's preferences suggest. 
Focus on patterns: topics, source types, relevance signals, etc.
Be specific and actionable for a scoring prompt.

Return ONLY the summary text, no preamble."""
                }
            ]
        )
        
        summary = message.content[0].text.strip() if message.content else None
        
        return {
            "summary": summary,
            "thumbs_up": thumbs_up,
            "thumbs_down": thumbs_down,
            "ratio": thumbs_up / (thumbs_up + thumbs_down) if (thumbs_up + thumbs_down) > 0 else 0
        }
    
    def update_scoring_prompt(self, calibration_summary: str) -> bool:
        """
        Update the intelligence-scoring-prompt.md file with the calibration addendum.
        Prepends the summary before the "## Scoring rubric" section.
        
        Returns: True if successful, False otherwise
        """
        try:
            prompt_path = "context/07_research/intelligence-scoring-prompt.md"
            
            # Read current prompt
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except FileNotFoundError:
                print(f"[ERROR] Scoring prompt not found at {prompt_path}")
                return False
            
            # Find insertion point (before "## Scoring rubric")
            rubric_marker = "## Scoring rubric"
            if rubric_marker not in content:
                print(f"[ERROR] '{rubric_marker}' section not found in prompt")
                return False
            
            # Create calibration section
            now = datetime.utcnow().strftime("%Y-%m-%d")
            calibration_section = f"""## Weekly Calibration (Updated {now})

{calibration_summary}

Adjust scoring upward for items matching these signals.

"""
            
            # Remove old calibration section if exists
            old_calibration_pattern = r"## Weekly Calibration.*?\n\n(?=##)"
            content = re.sub(old_calibration_pattern, "", content, flags=re.DOTALL)
            
            # Insert new calibration section
            content = content.replace(rubric_marker, calibration_section + rubric_marker)
            
            # Write back
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] Updated scoring prompt with calibration: {calibration_summary[:80]}...")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to update scoring prompt: {e}")
            return False


def run_weekly_aggregation(session: Session) -> dict:
    """
    Main entry point for weekly aggregation job.
    Aggregates feedback and updates prompt.
    Safe to call multiple times; idempotent.
    """
    service = BriefingAggregationService(session)
    
    # Aggregate last 7 days
    result = service.aggregate_feedback(days_back=7)
    
    if result.get("summary"):
        # Update prompt with new calibration
        success = service.update_scoring_prompt(result["summary"])
        if success:
            result["status"] = "success"
            result["prompt_updated"] = True
        else:
            result["status"] = "error"
            result["prompt_updated"] = False
    else:
        result["status"] = "skipped"
        result["prompt_updated"] = False
    
    return result
