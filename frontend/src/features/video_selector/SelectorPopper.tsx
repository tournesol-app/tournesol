import React from 'react';
import { Popper, PopperProps } from '@mui/material';

const SelectorPopper = (props: PopperProps) => {
  //   const [isOpen, setIsOpen] = React.useState(true);
  //   return (
  //     <Drawer hideBackdrop ref={ref} anchor="bottom" open={open}>
  //       {children}
  // </Drawer>
  //   );
  if (!props.open) {
    return null;
  }
  return (
    <Popper
      {...props}
      style={{ width: 'fit-content' }}
      placement="bottom-start"
      modifiers={[
        {
          name: 'offset',
          options: {
            offset: [0, 4],
          },
        },
      ]}
    />
  );
};

export default SelectorPopper;
