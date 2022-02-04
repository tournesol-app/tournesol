import React from 'react';
import { DrawerProps, Drawer } from '@mui/material';

const SelectorDrawer = (props: DrawerProps) => {
  return <Drawer {...props} anchor="bottom" />;
};

export default SelectorDrawer;
