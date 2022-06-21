import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import SelectorListBox, {
  EntitiesTab,
} from 'src/features/entity_selector/EntityTabsBox';
import { PollsService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';

interface Props {
  contextUid: string;
  uploader?: string;
}

const ContextualRecommendations = ({ contextUid, uploader }: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const handleEntitySelect = () => undefined;

  const tabs: EntitiesTab[] = useMemo(() => {
    const tabs = [];
    if (uploader)
      tabs.push({
        name: 'channel',
        label: t('contextualRecommendations.channel'),
        fetch: async () => {
          const response = await PollsService.pollsRecommendationsList({
            name: pollName,
            limit: 20,
            metadata: {
              uploader,
            },
            unsafe: true,
          });
          const results = response.results ?? [];
          return results.filter((entity) => entity.uid !== contextUid);
        },
      });
    return tabs;
  }, [t, pollName, uploader, contextUid]);

  return (
    <SelectorListBox
      tabs={tabs}
      onSelectEntity={handleEntitySelect}
      width="auto"
      maxHeight="none"
    />
  );
};

export default ContextualRecommendations;
