import React from 'react';
import { makeStyles } from '@material-ui/core';
import TopBar, { topBarHeight } from './components/topbar/TopBar';
import SideBar from './components/sidebar/SideBar';

interface Props {
  children?: React.ReactNode;
}

const useStyles = makeStyles({
  sideBarContainer: {
    display: 'flex',
    flexDirection: 'row',
    height: `calc(100% - ${topBarHeight})`,
  },
  main: {
    flexGrow: 1,
    overflow: 'hidden',
    backgroundColor: '#ffffff',
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
