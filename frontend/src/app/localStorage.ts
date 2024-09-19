function getLocalStorage() {
  try {
    const key = '__checking_local_storage__';
    localStorage.setItem(key, key);
    localStorage.removeItem(key);
    return localStorage;
  } catch (e) {
    console.error(`Cannot to use localstorage: ${e}`);
    return null;
  }
}

export const storage = getLocalStorage();
