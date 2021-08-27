import React from 'react';
import { makeStyles } from '@material-ui/core';
import TopBar from './components/topbar/TopBar';
import SideBar from './components/sidebar/SideBar';

interface Props {
  children?: React.ReactNode;
}

const useStyles = makeStyles({
  sideBarContainer: {
    display: 'flex',
    flexDirection: 'row',
  },
  main: {
    flexGrow: 1,
    padding: '24px',
  },
});

const Frame = ({ children }: Props) => {
  const classes = useStyles();

  return (
    <>
      <TopBar />
      <div className={classes.sideBarContainer}>
        <SideBar />
        <main className={classes.main}>{children}</main>
      </div>
    </>
  );
};

export default Frame;
