import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { Link, LinkOwnProps } from '@mui/material';

interface ExternalLinkProps {
  children: React.ReactNode;
  href?: string;
  color?: string;
}

interface InternalLinkProps {
  children: React.ReactNode;
  to: string;
  target?: string;
  ariaLabel?: string;
  color?: string;
  underline?: LinkOwnProps['underline'];
  fontWeight?: number;
  className?: string;
}

export const ExternalLink = ({
  children,
  href,
  color = 'revert',
}: ExternalLinkProps) => {
  return (
    <Link
      href={href}
      target="_blank"
      rel="noreferrer"
      sx={{
        color: color,
        textDecoration: 'revert',
      }}
    >
      {children}
    </Link>
  );
};

export const InternalLink = ({
  children,
  to,
  target,
  ariaLabel,
  color = 'secondary',
  underline = 'hover',
  fontWeight,
  className,
}: InternalLinkProps) => {
  return (
    <Link
      component={RouterLink}
      to={to}
      target={target}
      className={className}
      aria-label={ariaLabel}
      color={color}
      underline={underline}
      fontWeight={fontWeight}
    >
      {children}
    </Link>
  );
};
