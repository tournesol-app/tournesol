import React from 'react';
import { IconButton } from '@mui/material';
import { Link } from 'react-router-dom';

/**
 * A button with an icon that redirects to a link when clicked.
 */
const InternalLinkButton = ({
  children,
  to,
}: {
  children: React.ReactNode;
  to: string;
}) => {
  return (
    <Link to={to}>
      <IconButton>{children}</IconButton>
    </Link>
  );
};

export default InternalLinkButton;
