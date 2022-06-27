import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import SelectorListBox, {
  EntitiesTab,
} from 'src/features/entity_selector/EntityTabsBox';
import { PollsService, UsersService } from 'src/services/openapi';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { useLoginState } from 'src/hooks/useLoginState';

interface Props {
  contextUid: string;
  uploader?: string;
}

const ContextualRecommendations = ({ contextUid, uploader }: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();

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
          });
          const results = response.results ?? [];
          return results.filter((entity) => entity.uid !== contextUid);
        },
      });
    tabs.push({
      name: 'comparedWith',
      label: t('contextualRecommendations.comparedWith'),
      fetch: async () => {
        const response = await UsersService.usersMeComparisonsListFiltered({
          pollName,
          uid: contextUid,
          limit: 20,
        });
        const results = response.results ?? [];
        return results.map(({ entity_a, entity_b }) =>
          entity_a.uid === contextUid ? entity_b : entity_a
        );
      },
      disabled: !isLoggedIn,
    });
    return tabs;
  }, [t, pollName, uploader, contextUid, isLoggedIn]);

  return <SelectorListBox tabs={tabs} width="auto" maxHeight="none" withLink />;
};

export default ContextualRecommendations;
