import { useEffect, useState } from 'react';

export const useDocumentTitle = (pageTitle: string) => {
  const [previousTitle] = useState(document.title);

  useEffect(() => {
    document.title = pageTitle;
  }, [pageTitle]);

  useEffect(() => {
    return () => {
      document.title = previousTitle;
    };
  }, [previousTitle]);
};
