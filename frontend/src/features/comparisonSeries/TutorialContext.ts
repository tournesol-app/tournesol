import { createContext } from 'react';

const initialState = {
  isActive: false,
};

export const TutorialContext = createContext(initialState);
