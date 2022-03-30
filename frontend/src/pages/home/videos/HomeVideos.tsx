import React from 'react';

import UsageStatsSection from 'src/features/statistics/UsageStatsSection';
import ExtensionSection from 'src/pages/home/videos/ExtensionSection';
import ContributeSection from 'src/pages/home/videos/ContributeSection';
import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import AlternatingBackgroundColorSectionList from 'src/pages/home/AlternatingBackgroundColorSectionList';

const HomeVideosPage = () => {
  return (
    <AlternatingBackgroundColorSectionList>
      <TitleSection />
      <ExtensionSection />
      <ContributeSection />
      <PollListSection />
      <UsageStatsSection />
    </AlternatingBackgroundColorSectionList>
  );
};

export default HomeVideosPage;
