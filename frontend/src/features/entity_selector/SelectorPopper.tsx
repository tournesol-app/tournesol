import React from 'react';
import { Dialog, Popper, PopperProps, Button, Box } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface Props extends PopperProps {
  onClose: () => void;
  modal?: boolean;
}

const SelectorPopper = ({
  modal = false,
  open,
  onClose,
  children,
  ...rest
}: Props) => {
  const { t } = useTranslation();

  if (modal) {
    return (
      <Dialog open={open} onClose={onClose} fullScreen>
        <Box>
          <Button
            size="large"
            color="inherit"
            onClick={onClose}
            startIcon={<ArrowBack />}
          >
            {t('entitySelector.backButton')}
          </Button>
        </Box>
        {children}
      </Dialog>
    );
  }
  return (
    <Popper
      open={open}
      {...rest}
      style={{ width: 'fit-content' }}
      placement="bottom-start"
      modifiers={[
        {
          name: 'offset',
          options: {
            offset: [0, 4],
          },
        },
      ]}
    >
      {children}
    </Popper>
  );
};

export default SelectorPopper;
