import React, { useState } from 'react';

import {
  Alert,
  AlertTitle,
  Box,
  Collapse,
  Link,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';

interface TipSingleProps {
  tip: { title: string; messages: string[] };
}

const Tip = ({ tip }: TipSingleProps) => {
  const { t } = useTranslation();

  const [collapsed, setCollapsed] = useState(false);

  const handleCollapse = () => {
    setCollapsed(!collapsed);
  };

  return (
    <Alert
      severity="info"
      icon={false}
      action={<></>}
      sx={{
        minHeight: '131.617px',
      }}
    >
      <AlertTitle>
        <strong>{tip.title}</strong>
      </AlertTitle>
      <Typography paragraph mb={1}>
        {tip.messages[0]}
      </Typography>
      <Collapse in={collapsed} timeout="auto" sx={{ maxWidth: '880px' }}>
        {tip.messages.slice(1).map((message, index) => {
          return (
            <Typography key={`tip_${index}`} paragraph mb={1}>
              {message}
            </Typography>
          );
        })}
      </Collapse>
      <Box display="flex" justifyContent="flex-end">
        <Link component="button" color="secondary" onClick={handleCollapse}>
          {collapsed
            ? t('videos.dialogs.tutorial.hideTips')
            : t('videos.dialogs.tutorial.showTips')}
        </Link>
      </Box>
    </Alert>
  );
};

export default Tip;
