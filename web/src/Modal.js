import React, { useEffect } from 'react';
import './modal.css';

export default function Modal({ title, children, onClose }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  return (
    <div className="modal-backdrop">
      <div className="modal-window">
        <h3 className="modal-title">{title}</h3>
        <div className="modal-content">{children}</div>
        <button className="modal-close" onClick={onClose}>OK</button>
      </div>
    </div>
  );
}
