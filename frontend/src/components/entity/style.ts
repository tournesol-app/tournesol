import { SxProps } from '@mui/material';

export const entityCardMainSx: SxProps = {
  bgcolor: '#FFFFFF',
  border: '1px solid #DCD8CB',
  boxShadow: '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
  borderRadius: '4px',
  alignContent: 'flex-start',
  overflow: 'hidden',
  /*
    Set flex property to 1 to allow the card to expand as a flex item
    when placed side-by-side with another card, ensuring they remain
    equal in size.
  */
  flex: 1,
};
