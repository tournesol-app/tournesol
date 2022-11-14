import React, { useEffect, useState } from 'react';
import clsx from 'clsx';
import makeStyles from '@mui/styles/makeStyles';
import { Box } from '@mui/material';
import TopBar, { topBarHeight } from './components/topbar/TopBar';
import Footer from './components/footer/Footer';
import SideBar from './components/sidebar/SideBar';
import StorageError from './components/StorageError';

const isEmbedded = Boolean(new URLSearchParams(location.search).get('embed'));

const useStyles = makeStyles({
  sideBarContainer: {
    position: 'relative',
    display: 'flex',
    flexDirection: 'row',
    height: `calc(100% - ${topBarHeight}px)`,
  },
  main: {
    flexGrow: 1,
    overflow: 'auto',
    height: '100%',
  },
});

const EmbeddedTopBar = () => (
  <Box
    sx={{
      height: '4px',
      bgcolor: (theme) => theme.palette.primary.main,
    }}
  />
);

/**
 * When Tournesol is in an iframe, and third-party state is blocked, the authentication
 * will not work as expected.
 * This function attempts to detect this situation to warn the user
 * and advise to add tournesol domain as an exception.
 */
const hasLocalStorageAccess = async () => {
  // `document.hasStorageAccess` will tell us whether the current context has access
  // to "first-party" storage (including localStorage shared with previous sessions).
  // Especially necessary on Firefox which implements "state partitioning" for
  // third-party iframes when "Strict mode" is enabled.
  // See https://hacks.mozilla.org/2021/02/introducing-state-partitioning/
  //
  // However, `document.hasStorageAccess` is currently not implemented in Chrome.
  // null/undefined values need to be ignored.
  const hasStorageAccess = await document.hasStorageAccess?.();
  if (hasStorageAccess != null) {
    return hasStorageAccess;
  }
  try {
    localStorage;
    return true;
  } catch (err) {
    return false;
  }
};

interface Props {
  children?: React.ReactNode;
}

const Frame = ({ children }: Props) => {
  const classes = useStyles();
  const [hasStorageError, setHasStorageError] = useState(false);

  useEffect(() => {
    const checkStorage = async () => {
      if (!(await hasLocalStorageAccess())) {
        setHasStorageError(true);
      }
    };
    if (isEmbedded) {
      checkStorage();
    }
  }, []);

  return (
    <>
      {isEmbedded ? <EmbeddedTopBar /> : <TopBar />}
      <div className={clsx({ [classes.sideBarContainer]: !isEmbedded })}>
        {!isEmbedded && <SideBar />}
        <main className={classes.main}>
          {hasStorageError ? <StorageError /> : children}
          <Footer />
        </main>
      </div>
    </>
  );
};

export default Frame;
