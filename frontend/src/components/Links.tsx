import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { Link, LinkOwnProps, SxProps } from '@mui/material';

interface ExternalLinkProps {
  children: React.ReactNode;
  href?: string;
  target?: string;
  sx?: SxProps;
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

/**
 * A link to an external website.
 *
 * Avoid using the prop `target="_blank"` as much as possible. It changes the
 * browser' default behaviour, and forces the opening of a new tab or window
 * regardless of the users' preferences.
 *
 * `target="_blank"` can be useful when:
 *   - a user is leaving a page with unsaved changes
 *   - a media is playing on the page, and we don't want to interrupt it
 *   - etc.
 */
export const ExternalLink = ({
  children,
  href,
  target,
  sx,
}: ExternalLinkProps) => {
  return (
    <Link
      href={href}
      target={target}
      rel="noreferrer"
      sx={{
        color: 'revert',
        textDecoration: 'revert',
        ...sx,
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
