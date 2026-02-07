import React, { useState } from 'react';
import "./tiptap.css";
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import {
  FaBold, FaItalic, FaUnderline, FaHeading,
  FaListUl, FaQuoteLeft, FaCode,
  FaLink, FaImage, FaUndo, FaRedo, FaSave, FaTimes
} from 'react-icons/fa';

function TipTap({ initialContent = '', onSave, onClose }) {
  const [showLinkInput, setShowLinkInput] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] }, // кастом уровней заголовков
      }),
      Image.configure({ inline: true, allowBase64: true }),
      Link.configure({ openOnClick: false }), // кастом Link
    ],
    content: initialContent,
  });

  const addLink = () => {
    if (linkUrl && editor) {
      editor.chain().focus().setLink({ href: linkUrl }).run();
      setLinkUrl('');
      setShowLinkInput(false);
    }
  };

  const addImage = () => {
    const url = window.prompt('URL изображения:');
    if (url && editor) {
      editor.chain().focus().setImage({ src: url }).run();
    }
  };

  if (!editor) return null;

  return (
    <div className="tiptap-container">
      <div className="tiptap-toolbar">
        <button onClick={() => editor.chain().focus().toggleBold().run()}
                className={editor.isActive('bold') ? 'is-active' : ''} title="Жирный">
          <FaBold />
        </button>

        <button onClick={() => editor.chain().focus().toggleItalic().run()}
                className={editor.isActive('italic') ? 'is-active' : ''} title="Курсив">
          <FaItalic />
        </button>

        <button onClick={() => editor.chain().focus().toggleUnderline().run()}
                className={editor.isActive('underline') ? 'is-active' : ''} title="Подчеркнутый">
          <FaUnderline />
        </button>

        <button onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                className={editor.isActive('heading', { level: 1 }) ? 'is-active' : ''} title="Заголовок 1">
          <FaHeading />1
        </button>

        <button onClick={() => editor.chain().focus().toggleBulletList().run()}
                className={editor.isActive('bulletList') ? 'is-active' : ''} title="Список">
          <FaListUl />
        </button>

        <button onClick={() => setShowLinkInput(!showLinkInput)} title="Добавить ссылку">
          <FaLink />
        </button>

        <button onClick={addImage} title="Добавить изображение">
          <FaImage />
        </button>

        <button onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Отменить">
          <FaUndo />
        </button>

        <button onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Повторить">
          <FaRedo />
        </button>
      </div>

      {showLinkInput && (
        <div className="input-popup">
          <input
            type="text"
            placeholder="URL ссылки"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addLink()}
            autoFocus
          />
          <button onClick={addLink}>Добавить</button>
          <button onClick={() => setShowLinkInput(false)}>Отмена</button>
        </div>
      )}

      <div className="tiptap-editor">
        <EditorContent editor={editor} />
      </div>

      <div className="tiptap-actions">
        <button onClick={() => onSave(editor.getHTML())} className="save-btn">
          <FaSave /> Сохранить
        </button>
        <button onClick={onClose} className="cancel-btn">
          <FaTimes /> Отмена
        </button>
      </div>
    </div>
  );
}

export default TipTap;
