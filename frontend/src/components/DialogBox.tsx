import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Dialog, DialogTitle } from '@mui/material';
import { ButtonOwnProps } from '@mui/material/Button/Button';

interface DialogProps {
  title: string;
  content: React.ReactNode;
  open: boolean;
  onClose: () => void;
  additionalActionButton?: React.ReactNode;
  mainActionColor?: ButtonOwnProps['color'];
  mainActionCallback?: () => void;
}

/**
 * A dialog box that displays the provided content which can be any arbitrary
 * React component.
 */
const DialogBox = ({
  open,
  onClose,
  title,
  content,
  additionalActionButton,
  mainActionColor = 'primary',
  mainActionCallback,
}: DialogProps) => {
  const { t } = useTranslation();

  const handleClose = () => {
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle
        sx={{
          color: '#fff',
          fontFamily: 'Poppins-Bold',
          backgroundColor: 'secondary.main',
        }}
      >
        {title}
      </DialogTitle>
      <Box py={2} px={3}>
        <Box>{content}</Box>
        <Box display="flex" justifyContent="flex-end" gap={1}>
          {additionalActionButton}
          <Button
            variant="contained"
            color={mainActionColor}
            onClick={mainActionCallback ?? handleClose}
          >
            {t('dialogBox.continue')}
          </Button>
        </Box>
      </Box>
    </Dialog>
  );
};

export default DialogBox;
