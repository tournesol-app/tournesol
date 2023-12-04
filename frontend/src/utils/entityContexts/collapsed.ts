// Name of the key used in the browser's local storage.
const COLLAPSED_NS = 'entityContextsCollapsed';

const initCollapsed = () => '{}';

const collapsedIsEmpty = (collapsed: string) => {
  return collapsed == null || collapsed === initCollapsed();
};

export const setCollapsedState = (uid: string, state: boolean) => {
  let collapsed = localStorage.getItem(COLLAPSED_NS);

  if (collapsed == null) {
    collapsed = initCollapsed();
  }

  const collapsedJSON = JSON.parse(collapsed);
  collapsedJSON[uid] = state;

  localStorage.setItem(COLLAPSED_NS, JSON.stringify(collapsedJSON));
};

export const getCollapsedState = (uid: string): boolean | null => {
  const collapsed = localStorage.getItem(COLLAPSED_NS) ?? initCollapsed();

  if (collapsedIsEmpty(collapsed)) {
    return null;
  }

  const pendingJSON = JSON.parse(collapsed);
  const state = pendingJSON[uid];
  return state ?? null;
};
