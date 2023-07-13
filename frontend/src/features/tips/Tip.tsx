import React, { useState } from 'react';

import {
  Alert,
  AlertTitle,
  Button,
  Collapse,
  Grid,
  Typography,
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface TipSingleProps {
  tip: { title: string; messages: string[] };
}

const Tip = ({ tip }: TipSingleProps) => {
  const { t } = useTranslation();

  const [showTips, setCollapsed] = useState(false);

  const handleCollapse = () => {
    setCollapsed(!showTips);
  };

  return (
    <Alert severity="info">
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item>
          <AlertTitle>
            <strong>{tip.title}</strong>
          </AlertTitle>
        </Grid>
        <Grid item>
          <Button
            fullWidth
            onClick={handleCollapse}
            startIcon={showTips ? <ExpandLess /> : <ExpandMore />}
            size="medium"
            color="secondary"
            sx={{
              marginBottom: '8px',
              color: showTips ? 'red' : '',
            }}
          >
            {showTips
              ? t('videos.dialogs.tutorial.hideTips')
              : t('videos.dialogs.tutorial.showTips')}
          </Button>
        </Grid>
      </Grid>
      <Typography paragraph>{tip.messages[0]}</Typography>
      <Collapse in={showTips} timeout="auto" sx={{ maxWidth: '880px' }}>
        {tip.messages.slice(1).map((message, index) => {
          return (
            <Typography key={index} paragraph>
              {message}
            </Typography>
          );
        })}
      </Collapse>
    </Alert>
  );
};

export default Tip;
