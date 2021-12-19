import React from 'react';
import clsx from 'clsx';
import { Button, Theme } from '@material-ui/core';
import { ExpandMore, ExpandLess } from '@material-ui/icons';
import { makeStyles } from '@material-ui/styles';

const useStyles = makeStyles((theme: Theme) => ({
  filtersButton: {
    padding: '8px',
    marginLeft: '-8px', // keep the text aligned to the left
  },
  filtersButtonDefault: {
    color: theme.palette.action.active,
  },
  filtersButtonExpanded: {
    color: theme.palette.secondary.main,
  },
}));

interface FiltersButtonProps {
  children?: React.ReactNode;
  expanded: boolean;
  onClick?: (event: React.ChangeEvent<EventTarget>) => void;
}

const FiltersButton = ({
  children = 'Filters',
  expanded,
  onClick,
}: FiltersButtonProps) => {
  const classes = useStyles();
  return (
    <Button
      size="large"
      startIcon={!expanded ? <ExpandMore /> : <ExpandLess />}
      aria-expanded={expanded}
      aria-label="show more"
      onClick={onClick}
      className={clsx(classes.filtersButton, {
        [classes.filtersButtonDefault]: !expanded,
        [classes.filtersButtonExpanded]: expanded,
      })}
    >
      {children}
    </Button>
  );
};

export default FiltersButton;
