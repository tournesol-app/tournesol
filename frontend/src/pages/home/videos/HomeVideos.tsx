import React from 'react';

import { Grid2 } from '@mui/material';

import WebsiteBanners from 'src/features/banners/WebsiteBanners';
import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import ComparisonSection from 'src/pages/home/videos/sections/ComparisonSection';
import FundingSection from 'src/pages/home/videos/sections/FundingSection';
import RecommendationsSection from 'src/pages/home/videos/sections/RecommendationsSection';
import ResearchSection from 'src/pages/home/videos/sections/research/ResearchSection';
import UseOurExtension from 'src/pages/home/videos/sections/UseOurExtension';
import InstallMobileApp from 'src/pages/home/videos/sections/InstallMobileApp';

const HomeVideosPage = () => {
  const homeSectionSx = {
    width: '100%',
    px: { xs: 2, md: 6 },
  };

  return (
    <>
      <WebsiteBanners />
      <Grid2
        container
        sx={{
          width: '100%',
          flexDirection: 'column',
          alignItems: 'center',
          '& > .MuiGrid2-root > *': {
            maxWidth: '1200px',
            mx: 'auto',
          },
        }}
      >
        <Grid2
          sx={{
            bgcolor: 'background.emphatic',
            ...homeSectionSx,
            color: 'white',
          }}
        >
          <RecommendationsSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <InstallMobileApp />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <UseOurExtension />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <ComparisonSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <FundingSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <ResearchSection />
        </Grid2>
        <Grid2 sx={homeSectionSx}>
          <UsageStatsSection />
        </Grid2>
      </Grid2>
    </>
  );
};
export default HomeVideosPage;
