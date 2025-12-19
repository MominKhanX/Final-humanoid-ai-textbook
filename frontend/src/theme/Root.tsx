import React from 'react';
import ChatWidget from '@site/src/components/ChatWidget';

// Wrapper to add global components to all pages
export default function Root({children}) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
