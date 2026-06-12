/**
 * Signal to the Tournesol frontend that the browser extension is installed.
 *
 * The frontend reads this attribute to adapt its UI (see `useIsExtensionInstalled`).
 * Keep the attribute name in sync with the frontend.
 */

document.documentElement.setAttribute(
  'data-tournesol-extension-installed',
  'true'
);
