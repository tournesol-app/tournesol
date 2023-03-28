import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Button, Dialog, DialogTitle, Typography } from '@mui/material';

interface DialogProps {
  dialog: { title: string; messages: Array<string> };
  open: boolean;
  onClose: () => void;
  additionalActionButton?: React.ReactNode;
}

/**
 * A dialog box that displays one or more messages.
 */
const DialogBox = ({
  open,
  onClose,
  dialog,
  additionalActionButton,
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
        {dialog.title}
      </DialogTitle>
      <Box py={2} px={3}>
        <Box>
          {dialog.messages.map((message, index) => {
            return (
              <Typography key={index} paragraph>
                {message}
              </Typography>
            );
          })}
        </Box>
        <Box display="flex" justifyContent="flex-end" gap={1}>
          {additionalActionButton}
          <Button variant="contained" onClick={handleClose}>
            {t('dialogBox.continue')}
          </Button>
        </Box>
      </Box>
    </Dialog>
  );
};

export default DialogBox;
