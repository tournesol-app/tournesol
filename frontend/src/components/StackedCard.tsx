import React, { useState } from 'react';
import {
  Button,
  Divider,
  List,
  Card,
  CardHeader,
  CardContent,
  CardActions,
  Collapse,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';

type Props = {
  title: React.ReactElement;
  items: React.ReactElement[];
  actions: React.ReactElement;
};

const StackedCard = ({ title, items, actions }: Props) => {
  const [showAll, setShowAll] = useState(false);

  return (
    <Card>
      <CardHeader
        sx={{ color: '#000', backgroundColor: '#eee', p: 1 }}
        title={title}
      />
      <CardContent sx={{ p: 2, py: 0 }}>
        <List sx={{ py: 0 }}>
          {items.slice(0, 3).map((item, i) => (
            <React.Fragment key={i}>
              {item}
              <Divider variant="inset" component="li" />
            </React.Fragment>
          ))}
          {!showAll && (
            <Button
              fullWidth
              onClick={() => setShowAll(!showAll)}
              startIcon={showAll ? <ExpandLess /> : <ExpandMore />}
              size="medium"
              color="secondary"
              sx={{
                marginBottom: '8px',
              }}
            >
              {showAll ? 'Show Less' : 'Show All'}
            </Button>
          )}
          <Collapse in={showAll} timeout="auto" sx={{ width: '100%' }}>
            {items.slice(3).map((item, i) => (
              <React.Fragment key={i}>
                {item}
                <Divider variant="inset" component="li" />
              </React.Fragment>
            ))}
          </Collapse>
        </List>
      </CardContent>
      <CardActions sx={{ flexDirection: 'column' }}>{actions}</CardActions>
    </Card>
  );
};

export default StackedCard;
