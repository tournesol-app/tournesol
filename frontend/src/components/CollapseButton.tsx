import React from 'react';
import { Button, Badge, useTheme } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

interface CollapseButtonProps {
  children?: React.ReactNode;
  expanded: boolean;
  showBadge?: boolean;
  onClick?: (event: React.ChangeEvent<EventTarget>) => void;
  variant?: 'default' | 'mainOptions';
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
  variant = 'default',
}: CollapseButtonProps) => {
  const theme = useTheme();
  return (
    <Badge color="secondary" variant="dot" invisible={!showBadge}>
      <Button
        size="large"
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={onClick}
        sx={{
          padding: '0 8px',
          fontSize: variant === 'mainOptions' ? '1.1rem' : undefined,
          color:
            expanded || variant == 'mainOptions'
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
