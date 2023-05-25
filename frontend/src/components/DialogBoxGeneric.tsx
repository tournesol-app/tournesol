import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Button, Dialog, DialogTitle } from '@mui/material';

interface DialogBoxGenericProps {
  dialog: { title: string; content: React.ReactNode };
  open: boolean;
  onClose: () => void;
  additionalActionButton?: React.ReactNode;
}

const DialogBoxGeneric = ({
  open,
  onClose,
  dialog,
  additionalActionButton,
}: DialogBoxGenericProps) => {
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
        <Box>{dialog.content}</Box>
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

export default DialogBoxGeneric;
