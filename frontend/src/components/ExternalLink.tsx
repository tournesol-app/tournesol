import React from 'react';

import { Link } from '@mui/material';

const ExternalLink = ({ text, href }: { text: string; href: string }) => {
  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener"
      sx={{
        color: 'revert',
        textDecoration: 'revert',
      }}
    >
      {text}
    </Link>
  );
};

export default ExternalLink;
