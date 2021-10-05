import React, { useState } from 'react';
import Snackbar from '@material-ui/core/Snackbar';

const Alert = ({ children }: { children: React.ReactNode }) => {
  const [isOpen, setIsOpen] = useState(true);

  const onClose = () => {
    setIsOpen(false);
  };

  return (
    <Snackbar
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'center',
      }}
      open={isOpen}
      autoHideDuration={3000}
      message={children}
      onClose={onClose}
    />
  );
};

export default Alert;
