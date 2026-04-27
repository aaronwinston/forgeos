'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { useState, useEffect } from 'react';
import TurndownService from 'turndown';
import { marked } from 'marked';
import {
  Bold,
  Italic,
  Heading1,
  Heading2,
  Heading3,
  List,
  Code2,
  Quote,
  Undo2,
  Redo2,
} from 'lucide-react';

interface TipTapEditorProps {
  initialMarkdown: string;
  onChange: (markdown: string) => void;
}

const turndownService = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
});

export default function TipTapEditor({
  initialMarkdown,
  onChange,
}: TipTapEditorProps) {
  const [isReady, setIsReady] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'Start writing your draft...',
      }),
    ],
    content: '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const markdown = turndownService.turndown(html);
      onChange(markdown);
    },
  });

  useEffect(() => {
    if (editor && initialMarkdown && !isReady) {
      parseMarkdownAndSetContent(initialMarkdown);
      setIsReady(true);
    }
  }, [editor, initialMarkdown, isReady]);

  const parseMarkdownAndSetContent = async (markdown: string) => {
    try {
      const html = await marked(markdown);
      if (editor) {
        editor.commands.setContent(html as string);
      }
    } catch (error) {
      console.error('Error parsing markdown:', error);
      // Fallback: set raw markdown as plain text
      if (editor) {
        editor.commands.setContent(
          `<pre>${markdown.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`
        );
      }
    }
  };

  const applyBold = () => editor?.chain().focus().toggleBold().run();
  const applyItalic = () => editor?.chain().focus().toggleItalic().run();
  const applyHeading1 = () =>
    editor?.chain().focus().toggleHeading({ level: 1 }).run();
  const applyHeading2 = () =>
    editor?.chain().focus().toggleHeading({ level: 2 }).run();
  const applyHeading3 = () =>
    editor?.chain().focus().toggleHeading({ level: 3 }).run();
  const applyBulletList = () =>
    editor?.chain().focus().toggleBulletList().run();
  const applyCodeBlock = () =>
    editor?.chain().focus().toggleCodeBlock().run();
  const applyBlockquote = () =>
    editor?.chain().focus().toggleBlockquote().run();
  const handleUndo = () => editor?.chain().focus().undo().run();
  const handleRedo = () => editor?.chain().focus().redo().run();

  const buttonClass =
    'p-2 hover:bg-gray-200 rounded transition-colors flex items-center justify-center';

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Toolbar */}
      <div className="border-b border-gray-200 p-2 bg-gray-50 flex flex-wrap gap-1">
        <button
          onClick={applyBold}
          className={buttonClass}
          title="Bold (Cmd+B)"
          disabled={!editor}
        >
          <Bold size={18} />
        </button>
        <button
          onClick={applyItalic}
          className={buttonClass}
          title="Italic (Cmd+I)"
          disabled={!editor}
        >
          <Italic size={18} />
        </button>

        <div className="w-px bg-gray-300 mx-1" />

        <button
          onClick={applyHeading1}
          className={buttonClass}
          title="Heading 1"
          disabled={!editor}
        >
          <span className="font-bold text-lg">H1</span>
        </button>
        <button
          onClick={applyHeading2}
          className={buttonClass}
          title="Heading 2"
          disabled={!editor}
        >
          <span className="font-bold">H2</span>
        </button>
        <button
          onClick={applyHeading3}
          className={buttonClass}
          title="Heading 3"
          disabled={!editor}
        >
          <span className="font-bold text-sm">H3</span>
        </button>

        <div className="w-px bg-gray-300 mx-1" />

        <button
          onClick={applyBulletList}
          className={buttonClass}
          title="Bullet List"
          disabled={!editor}
        >
          <List size={18} />
        </button>
        <button
          onClick={applyBlockquote}
          className={buttonClass}
          title="Blockquote"
          disabled={!editor}
        >
          <Quote size={18} />
        </button>
        <button
          onClick={applyCodeBlock}
          className={buttonClass}
          title="Code Block (Cmd+`)"
          disabled={!editor}
        >
          <Code2 size={18} />
        </button>

        <div className="w-px bg-gray-300 mx-1" />

        <button
          onClick={handleUndo}
          className={buttonClass}
          title="Undo (Cmd+Z)"
          disabled={!editor}
        >
          <Undo2 size={18} />
        </button>
        <button
          onClick={handleRedo}
          className={buttonClass}
          title="Redo (Cmd+Shift+Z)"
          disabled={!editor}
        >
          <Redo2 size={18} />
        </button>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-auto">
        <EditorContent
          editor={editor}
          className="prose prose-sm max-w-none p-4 focus:outline-none"
        />
      </div>
    </div>
  );
}
