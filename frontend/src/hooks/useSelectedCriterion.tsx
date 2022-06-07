import React, {
  createContext,
  useState,
  useEffect,
  useMemo,
  useContext,
} from 'react';
import { useCurrentPoll } from 'src/hooks';

interface SelectedCriterionContextValue {
  selectedCriterion: string;
  setSelectedCriterion: (criterion: string) => void;
}

const SelectedCriterionContext = createContext<SelectedCriterionContextValue>({
  selectedCriterion: '',
  setSelectedCriterion: () => undefined,
});

export const SelectedCriterionProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { name: pollName, options } = useCurrentPoll();

  const mainCriterionName = options?.mainCriterionName || '';
  const [selectedCriterion, setSelectedCriterion] =
    useState<string>(mainCriterionName);

  // Reset the selected criterion when the poll changes
  useEffect(() => {
    setSelectedCriterion(mainCriterionName);
  }, [pollName, mainCriterionName]);

  const contextValue = useMemo(
    () => ({
      selectedCriterion,
      setSelectedCriterion,
    }),
    [selectedCriterion]
  );

  return (
    <SelectedCriterionContext.Provider value={contextValue}>
      {children}
    </SelectedCriterionContext.Provider>
  );
};

const useSelectedCriterion = () => useContext(SelectedCriterionContext);

export default useSelectedCriterion;
