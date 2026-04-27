"""File expansion flow for doctrine files."""

from anthropic import Anthropic
from pathlib import Path
from typing import Optional


class FileExpansionService:
    """AI-assisted file expansion using Claude."""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.client = Anthropic()
    
    def read_file(self, file_path: str) -> tuple[str, bool]:
        """Read a markdown file. Returns (content, success)."""
        try:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                return f"[ERROR] File not found: {file_path}", False
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content, True
        except Exception as e:
            return f"[ERROR] Failed to read file: {e}", False
    
    def write_file(self, file_path: str, content: str) -> tuple[str, bool]:
        """Write content to a markdown file. Returns (message, success)."""
        try:
            full_path = self.repo_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"File updated: {file_path}", True
        except Exception as e:
            return f"[ERROR] Failed to write file: {e}", False
    
    def get_context_for_file(self, file_path: str) -> str:
        """Get surrounding context and related files for a doctrine file."""
        try:
            # Read related context files
            context_parts = []
            
            # If this is in context/, read the orchestrator
            if "context" in file_path:
                orch_path = "context/00_orchestration/forgeos-context-orchestrator.md"
                content, success = self.read_file(orch_path)
                if success:
                    context_parts.append(f"## Context Orchestrator\n\n{content[:2000]}...")
            
            # If this is in core/, read VOICE and STYLE_GUIDE
            if "core" in file_path:
                voice_path = "core/VOICE.md"
                voice_content, success = self.read_file(voice_path)
                if success:
                    context_parts.append(f"## Voice Guide\n\n{voice_content[:1500]}...")
            
            return "\n\n---\n\n".join(context_parts) if context_parts else ""
        except Exception as e:
            return f"[Could not load context: {e}]"
    
    def generate_expansion_prompt(self, file_path: str, file_content: str, context: str) -> str:
        """Generate the system prompt for file expansion."""
        file_type = self._identify_file_type(file_path)
        
        return f"""You are helping Aaron expand a doctrine file from a placeholder to production quality.

File being expanded: {file_path}
Current word count: {len(file_content.split())} words

File type: {file_type}

Surrounding context:
{context}

Your task:
1. Ask Aaron 5–8 targeted questions to understand what should go in this file
2. Ask questions about the specific content, themes, principles, or examples
3. Be conversational; ask one or two questions at a time, not all at once
4. After gathering sufficient information (usually 2-3 exchanges), generate a draft of at least 1500 words
5. The draft should maintain Aaron's voice and align with the surrounding doctrine

Important:
- Don't make up positioning or claims Aaron hasn't told you about
- If Aaron doesn't know what should go in a file, help him think through it
- Ask clarifying questions if something is vague
- When ready to generate the draft, ask "Should I write the draft now?" and wait for confirmation
- The final draft should be production-ready markdown

Start by asking your first question about what should go in this file."""
    
    def _identify_file_type(self, file_path: str) -> str:
        """Identify the type of file being expanded."""
        if "VOICE" in file_path:
            return "Voice & Brand Tone"
        elif "STYLE_GUIDE" in file_path:
            return "Style Guide"
        elif "messaging" in file_path:
            return "Messaging Framework"
        elif "strategy" in file_path:
            return "Strategy Document"
        elif "playbook" in file_path:
            return "Playbook"
        else:
            return "Doctrine File"
    
    def generate_draft(self, file_path: str, file_content: str, conversation_history: list) -> str:
        """Generate a draft expansion based on conversation."""
        system_prompt = f"""You are completing a file expansion task. Based on Aaron's responses, generate a production-ready draft for:

File: {file_path}

Current content (if any):
{file_content}

Conversation history shows Aaron's preferences and requirements. Now generate a draft that:
1. Is at least 1500 words
2. Directly addresses Aaron's stated needs and preferences
3. Maintains consistency with the rest of the doctrine
4. Uses clear, professional language
5. Includes examples where helpful

Return ONLY the markdown content, no preamble. The draft should be ready to save directly to the file."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=system_prompt,
            messages=conversation_history
        )
        
        return message.content[0].text if message.content else ""
