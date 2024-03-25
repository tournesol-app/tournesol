import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { Link, LinkOwnProps } from '@mui/material';

interface ExternalLinkProps {
  children: React.ReactNode;
  href?: string;
}

interface InternalLinkProps {
  children: React.ReactNode;
  href: string;
  target?: string;
  ariaLabel?: string;
  color?: string;
  underline?: LinkOwnProps['underline'];
  fontWeight?: number;
  className?: string;
}

export const ExternalLink = ({ children, href }: ExternalLinkProps) => {
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

export const InternalLink = ({
  children,
  href,
  target,
  ariaLabel,
  color = 'secondary',
  underline = 'hover',
  fontWeight,
  className,
}: InternalLinkProps) => {
  return (
    <Link
      className={className}
      component={RouterLink}
      to={href}
      target={target}
      aria-label={ariaLabel}
      color={color}
      underline={underline}
      fontWeight={fontWeight}
    >
      {children}
    </Link>
  );
};
