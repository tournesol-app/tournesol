import React from 'react';
import { Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';

const useStyles = makeStyles({
  filterTitle: {
    borderBottom: '1px solid #E7E5DB',
    marginBottom: '0.3em',
  },
});

interface Props {
  title: string;
  children: React.ReactNode;
}

const TitledSection = ({ title, children }: Props) => {
  const classes = useStyles();
  return (
    <>
      <Typography variant="h6" className={classes.filterTitle}>
        {title}
      </Typography>
      {children}
    </>
  );
};

export default TitledSection;
