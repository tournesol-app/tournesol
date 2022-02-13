import React from 'react';
import clsx from 'clsx';
import { Button, Theme, Badge } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { makeStyles } from '@mui/styles';
import { useTranslation } from 'react-i18next';

const useStyles = makeStyles((theme: Theme) => ({
  collapseButton: {
    padding: '8px',
    marginLeft: '-8px', // keep the text aligned to the left
  },
  collapseButtonDefault: {
    color: theme.palette.action.active,
  },
  collapseButtonExpanded: {
    color: theme.palette.secondary.main,
  },
}));

interface CollapseButtonProps {
  children?: React.ReactNode;
  expanded: boolean;
  showBadge: boolean;
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
  showBadge,
  onClick,
}: CollapseButtonProps) => {
  const classes = useStyles();
  return (
    <Badge
      color="secondary"
      variant="dot"
      invisible={!showBadge}
      style={{ padding: '0px 8px' }}
    >
      <Button
        color="secondary"
        size="large"
        startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
        aria-expanded={expanded}
        aria-label="show more"
        onClick={onClick}
        className={clsx(classes.collapseButton, {
          [classes.collapseButtonDefault]: !expanded,
          [classes.collapseButtonExpanded]: expanded,
        })}
      >
        {children}
      </Button>
    </Badge>
  );
};

export default CollapseButton;
