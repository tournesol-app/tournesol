import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Alert,
  AlertTitle,
  Box,
  Collapse,
  Link,
  Theme,
  Typography,
  useMediaQuery,
} from '@mui/material';

interface TipProps {
  tip: { title: string; messages: string[] };
  // Allows to identify a unique tip in the DOM.
  tipId: string;
}

const Tip = ({ tip, tipId }: TipProps) => {
  const { t } = useTranslation();
  const [collapsed, setCollapsed] = useState(false);
  const isSmallScreen = useMediaQuery((theme: Theme) =>
    theme.breakpoints.down('sm')
  );
  const defaultVisibleParagrahs = isSmallScreen ? 0 : 1;

  const handleCollapse = () => {
    setCollapsed(!collapsed);
  };

  return (
    <Alert
      severity="info"
      icon={false}
      sx={{
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

      {defaultVisibleParagrahs > 0 && (
        <>
          {tip.messages
            .slice(0, defaultVisibleParagrahs)
            .map((message, index) => (
              <Typography key={`tip_${index}`} paragraph mb={1}>
                {message}
              </Typography>
            ))}
        </>
      )}

      <Collapse in={collapsed} timeout="auto">
        {tip.messages.slice(defaultVisibleParagrahs).map((message, index) => {
          return (
            <Typography key={`tip_${index}`} paragraph mb={1}>
              {message}
            </Typography>
          );
        })}
      </Collapse>
      {tip.messages.length > defaultVisibleParagrahs && (
        <Box display="flex" justifyContent="flex-end">
          <Link
            component="button"
            color="secondary"
            onClick={handleCollapse}
            sx={{ textDecoration: 'none' }}
          >
            {collapsed ? t('tip.less') : t('tip.showMore')}
          </Link>
        </Box>
      )}
    </Alert>
  );
};

export default Tip;
