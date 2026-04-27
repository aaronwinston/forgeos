'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { useState, useEffect, useCallback } from 'react';
import TurndownService from 'turndown';
import { marked } from 'marked';
import {
  Bold,
  Italic,
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
  const [charCount, setCharCount] = useState(0);
  const [editorRef, setEditorRef] = useState<ReturnType<typeof useEditor> | null>(
    null
  );

  const parseMarkdownAndSetContent = useCallback(
    async (markdown: string) => {
      if (!editorRef) return;

      try {
        const html = await marked(markdown);
        editorRef.commands.setContent(html as string);
        setCharCount(markdown.length);
      } catch (error) {
        console.error('Error parsing markdown:', error);
        // Fallback: set raw markdown as plain text
        editorRef.commands.setContent(
          `<pre>${markdown.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`
        );
      }
    },
    [editorRef]
  );

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Placeholder.configure({
        placeholder: 'Start writing your draft...',
        emptyEditorClass: 'is-editor-empty',
      }),
    ],
    content: '',
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const markdown = turndownService.turndown(html);
      onChange(markdown);
      setCharCount(editor.getText().length);
    },
  });

  useEffect(() => {
    setEditorRef(editor);
  }, [editor]);

  useEffect(() => {
    if (editorRef && initialMarkdown && !isReady) {
      parseMarkdownAndSetContent(initialMarkdown);
      setIsReady(true);
    }
  }, [editorRef, initialMarkdown, isReady, parseMarkdownAndSetContent]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!editor) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Bold: Cmd+B or Ctrl+B
      if ((e.metaKey || e.ctrlKey) && e.key === 'b') {
        e.preventDefault();
        editor.chain().focus().toggleBold().run();
      }
      // Italic: Cmd+I or Ctrl+I
      if ((e.metaKey || e.ctrlKey) && e.key === 'i') {
        e.preventDefault();
        editor.chain().focus().toggleItalic().run();
      }
      // Code: Cmd+` or Ctrl+`
      if ((e.metaKey || e.ctrlKey) && e.key === '`') {
        e.preventDefault();
        editor.chain().focus().toggleCode().run();
      }
    };

    editor.view.dom.addEventListener('keydown', handleKeyDown);
    return () => editor.view.dom.removeEventListener('keydown', handleKeyDown);
  }, [editor]);

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
    'p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors flex items-center justify-center text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100';

  const toolbarClass =
    'border-b border-gray-200 dark:border-gray-700 p-2 bg-gray-50 dark:bg-gray-900 flex flex-wrap gap-1';

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-950">
      {/* Toolbar */}
      <div className={toolbarClass}>
        {/* Formatting: Bold, Italic */}
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

        <div className="w-px bg-gray-300 dark:bg-gray-600 mx-1" />

        {/* Headings: H1, H2, H3 */}
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

        <div className="w-px bg-gray-300 dark:bg-gray-600 mx-1" />

        {/* Lists and Blocks */}
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

        <div className="w-px bg-gray-300 dark:bg-gray-600 mx-1" />

        {/* Undo/Redo */}
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

        {/* Character count indicator */}
        <div className="ml-auto pl-2 border-l border-gray-300 dark:border-gray-600 flex items-center">
          <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
            {charCount} characters
          </span>
        </div>
      </div>

      {/* Editor Content Area */}
      <div className="flex-1 overflow-auto">
        <EditorContent
          editor={editor}
          className="prose dark:prose-invert prose-sm max-w-none p-4 focus:outline-none text-gray-900 dark:text-gray-100"
        />
      </div>
    </div>
  );
}
