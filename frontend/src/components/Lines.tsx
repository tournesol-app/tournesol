import React from 'react';

const Lines = ({ messages }: { messages?: string[] }) => {
  if (!messages || messages.length === 0) {
    return null;
  }
  return (
    <>
      {messages.map((message, idx) => (
        <span key={idx}>
          {message}
          <br />
        </span>
      ))}
    </>
  );
};

export default Lines;
