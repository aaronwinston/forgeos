'use client';

import { useMemo } from 'react';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';
import SkillPlaybookChip from './SkillPlaybookChip';

interface MarkdownMessageProps {
  content: string;
}

interface CodeArgs {
  text: string;
  lang?: string;
}

interface LinkArgs {
  href: string;
  text: string;
}

export default function MarkdownMessage({ content }: MarkdownMessageProps) {
  const html = useMemo(() => {
    // Configure marked with highlight.js for code blocks
    marked.setOptions({
      breaks: true,
      gfm: true,
    });

    // Create a custom renderer for code blocks with syntax highlighting
    const renderer = new marked.Renderer();
    
    renderer.code = function (args: CodeArgs) {
      const { text, lang } = args;
      let highlightedCode = text;
      
      if (lang && hljs.getLanguage(lang)) {
        try {
          highlightedCode = hljs.highlight(text, { language: lang }).value;
        } catch {
          highlightedCode = text;
        }
      } else {
        highlightedCode = hljs.highlightAuto(text).value;
      }

      return `<pre><code class="hljs language-${lang || 'plaintext'}">${highlightedCode}</code></pre>`;
    };

    renderer.link = function(args: LinkArgs) {
      const { href, text } = args;
      return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-700 underline">${text}</a>`;
    };

    marked.setOptions({ renderer });

    return marked(content);
  }, [content]);

  // Extract and replace skill/playbook references
  const processedHtml = useMemo(() => {
    const result = html;
    
    // The HTML is used as-is; references are handled in ChipReferences component
    return result;
  }, [html]);

  return (
    <div className="prose prose-sm max-w-none dark:prose-invert text-sm">
      {/* Parse HTML and render with proper styling */}
      <div
        className="space-y-2 text-gray-900"
        dangerouslySetInnerHTML={{ __html: processedHtml }}
      />
      
      {/* Inline skill/playbook chip rendering */}
      {(content.includes('[skill:') || content.includes('[playbook:')) && (
        <ChipReferences content={content} />
      )}
    </div>
  );
}

function ChipReferences({ content }: { content: string }) {
  const skillMatches = Array.from(content.matchAll(/\[skill:\s*([^\]]+)\]/g));
  const playbookMatches = Array.from(content.matchAll(/\[playbook:\s*([^\]]+)\]/g));

  if (skillMatches.length === 0 && playbookMatches.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
      {skillMatches.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {skillMatches.map(([, name], idx) => (
            <SkillPlaybookChip key={`skill-${idx}`} type="skill" name={name.trim()} />
          ))}
        </div>
      )}
      {playbookMatches.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {playbookMatches.map(([, name], idx) => (
            <SkillPlaybookChip key={`playbook-${idx}`} type="playbook" name={name.trim()} />
          ))}
        </div>
      )}
    </div>
  );
}
