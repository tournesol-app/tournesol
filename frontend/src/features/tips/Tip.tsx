import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  AlertTitle,
  Collapse,
  Grid,
  Link,
  MobileStepper,
  Typography,
} from '@mui/material';

interface TipProps {
  tip: { title: string; messages: string[] };
  // Allows to identify a unique tip in the DOM.
  tipId: string;
  stepPos?: number;
  stepMax?: number;
}

const Tip = ({ tip, tipId, stepPos, stepMax }: TipProps) => {
  const { t } = useTranslation();

  const [collapsed, setCollapsed] = useState(false);

  const handleCollapse = () => {
    setCollapsed(!collapsed);
  };

  return (
    <Alert
      severity="info"
      icon={false}
      sx={{
        minHeight: '131.617px',
        width: '100%',
        '.MuiAlert-message': {
          width: '100%',
        },
      }}
      data-testid={`tip-id-${tipId}`}
    >
      <AlertTitle>
        <strong>{tip.title}</strong>
      </AlertTitle>
      <Typography paragraph mb={1}>
        {tip.messages[0]}
      </Typography>
      <Collapse in={collapsed} timeout="auto">
        {tip.messages.slice(1).map((message, index) => {
          return (
            <Typography key={`tip_${index}`} paragraph mb={1}>
              {message}
            </Typography>
          );
        })}
      </Collapse>
      <Grid container display="flex" justifyContent="space-between">
        <Grid item xs={4}></Grid>
        <Grid item xs={4}>
          {stepMax !== undefined && stepPos === undefined && (
            <MobileStepper
              variant="dots"
              steps={stepMax}
              position="static"
              sx={{ background: 'none' }}
              activeStep={stepPos}
              backButton={undefined}
              nextButton={undefined}
            />
          )}
        </Grid>
        <Grid item justifyItems="flex-end">
          {tip.messages.length > 1 && (
            <Link
              component="button"
              color="secondary"
              onClick={handleCollapse}
              sx={{ textDecoration: 'none' }}
            >
              {collapsed ? t('tip.less') : t('tip.showMore')}
            </Link>
          )}
        </Grid>
      </Grid>
    </Alert>
  );
};

export default Tip;
