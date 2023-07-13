import React, { useState } from 'react';

import {
  Alert,
  AlertTitle,
  Collapse,
  IconButton,
  Typography,
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';

interface TipSingleProps {
  tip: { title: string; messages: string[] };
}

const Tip = ({ tip }: TipSingleProps) => {
  const [showTips, setCollapsed] = useState(false);

  const handleCollapse = () => {
    setCollapsed(!showTips);
  };

  return (
    <Alert
      severity="info"
      icon={false}
      action={
        <IconButton
          onClick={handleCollapse}
          size="medium"
          color="secondary"
          sx={{ marginBottom: '8px' }}
        >
          {showTips ? <ExpandLess /> : <ExpandMore />}
        </IconButton>
      }
    >
      <AlertTitle>
        <strong>{tip.title}</strong>
      </AlertTitle>
      <Typography paragraph mb={1}>
        {tip.messages[0]}
      </Typography>
      <Collapse in={showTips} timeout="auto" sx={{ maxWidth: '880px' }}>
        {tip.messages.slice(1).map((message, index) => {
          return (
            <Typography key={index} paragraph mb={1}>
              {message}
            </Typography>
          );
        })}
      </Collapse>
    </Alert>
  );
};

export default Tip;
