import React, { useEffect, useState } from 'react';
import {
  Typography,
  Box,
  Divider,
  List,
  ListItem,
  CircularProgress,
} from '@material-ui/core';

import { ContentHeader, ContentBox } from 'src/components';

const DOMAINS_PAGE_SIZE = 1000;

const PrivacyPolicyPage = () => {
  return (
    <div
      style={{
        marginTop: 24,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          maxWidth: '100%',
          width: 640,
          color: '#4A473E',
          padding: 24,
        }}
      >
        <Typography variant="h3">Privacy Policy</Typography>

        <Typography variant="h4">What personal data Tournesol collects and why</Typography>

        <Typography variant="h5">Ratings</Typography>
        
        <Typography paragraph>
        Our mission is to elicit, infer and aggregate contributors’ judgments on the quality of
        online videos. To do so, Tournesol collects the data provided by the contributors when
        they compare pairs of content.
        </Typography>
        
        <Typography variant="h5">Search</Typography>
        
        <Typography paragraph>
        Even if the contributor is not logged in, Tournesol collects the parameters of their
        search queries in order to better understand most users’ needs. We believe that such
        data can also have a scientific and ethical value to help make recommendation systems
        more robustly beneficial to humanity.
        </Typography>

      </div>
    </div>
  );
};

export default PrivacyPolicyPage;