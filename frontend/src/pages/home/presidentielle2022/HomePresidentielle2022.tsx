import React from 'react';

import ContributeSection from 'src/pages/home/presidentielle2022/ContributeSection';
import TitleSection from 'src/pages/home/TitleSection';
import PollListSection from 'src/pages/home/PollListSection';
import AlternatingBackgroundColorSectionList from 'src/pages/home/AlternatingBackgroundColorSectionList';

const HomePresidentielle2022Page = () => {
  return (
    <AlternatingBackgroundColorSectionList
      secondaryBackground="rgba(0, 0, 0, 0.08)"
      secondaryColor="#000000"
    >
      <TitleSection />
      <ContributeSection />
      <PollListSection />
      {/* 
        <UsageStatsSection /> 
        TODO: Stats are specific to videos. This component and the api 
        endpoint may be adapted to work for all Polls.
      */}
    </AlternatingBackgroundColorSectionList>
  );
};

export default HomePresidentielle2022Page;
