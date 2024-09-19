import { storage } from 'src/app/localStorage';

// Name of the key used in the browser's local storage.
const COLLAPSED_NS = 'entityContextsCollapsed';

const initCollapsed = () => '{}';

export const setCollapsedState = (uid: string, state: boolean) => {
  let collapsed = storage?.getItem(COLLAPSED_NS);
  if (collapsed == null) {
    collapsed = initCollapsed();
  }

  const collapsedJSON = JSON.parse(collapsed);
  collapsedJSON[uid] = state;
  storage?.setItem(COLLAPSED_NS, JSON.stringify(collapsedJSON));
};

export const getCollapsedState = (uid: string): boolean | null => {
  const collapsed = storage?.getItem(COLLAPSED_NS) ?? initCollapsed();
  if (!collapsed) {
    return null;
  }
  const pendingJSON = JSON.parse(collapsed);
  const state = pendingJSON[uid];
  return state ?? null;
};
