import React from 'react';
import { Box, Button, Dialog, DialogTitle, Typography } from '@mui/material';

interface DialogProps {
  dialog: { title: string; messages: Array<string> };
  open: boolean;
  onClose: () => void;
}

const DialogBox = ({ open, onClose, dialog }: DialogProps) => {
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
        <Box display="flex" justifyContent="flex-end">
          <Button variant="contained" onClick={handleClose}>
            Continuer
          </Button>
        </Box>
      </Box>
    </Dialog>
  );
};

export default DialogBox;
