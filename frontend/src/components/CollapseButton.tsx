import React from 'react';
import { Button, Badge, useTheme } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface CollapseButtonProps {
  children?: React.ReactNode;
  expanded: boolean;
  showBadge?: boolean;
  onClick?: (event: React.ChangeEvent<EventTarget>) => void;
}

const DefaultText = () => {
  const { t } = useTranslation();
  return (
    <span style={{ textTransform: 'uppercase' }}>
      {t('components.filtersButton')}
    </span>
  );
};

const CollapseButton = ({
  children = <DefaultText />,
  expanded,
  showBadge = false,
  onClick,
}: CollapseButtonProps) => {
  const theme = useTheme();
  return (
    <Badge color="secondary" variant="dot" invisible={!showBadge}>
      <Button
        color="secondary"
        size="large"
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={onClick}
        sx={{
          padding: '0 8px',
          marginBottom: '8px',
          marginLeft: '-8px', // keep the text aligned to the left
          color: expanded
            ? theme.palette.secondary.main
            : theme.palette.action.active,
        }}
      >
        {children}
      </Button>
    </Badge>
  );
};

export default CollapseButton;
