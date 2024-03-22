import { SxProps } from '@mui/material';

export const entityCardMainSx: SxProps = {
  bgcolor: '#FFFFFF',
  border: '1px solid #DCD8CB',
  boxShadow: '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
  borderRadius: '4px',
  alignContent: 'flex-start',
  overflow: 'hidden',
  /*
    Allow the card to grow on the comparison page
    to match the height of the second entity card
  */
  flexGrow: 1,
};
