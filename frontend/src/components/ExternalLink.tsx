import React from 'react';

import { Link } from '@mui/material';

interface ExternalLinkProps {
  children: React.ReactNode;
  href: string;
}

const ExternalLink = ({ children, href }: ExternalLinkProps) => {
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
      {children}
    </Link>
  );
};

export default ExternalLink;
