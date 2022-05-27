export default class {
  static getApiBase() {
    // TODO: Don't include trailing slash
    return `https://${window.location.hostname}/api/`;
  }

  static fetchWithToken(relativeUrl, options, accessToken) {
    if(!accessToken){
      throw new Error("fetchWithToken called without an access token");
    }
    options.headers = options.headers || {};
    options.headers.Authorization = `Bearer ${accessToken}`;
    return fetch(new URL(relativeUrl, this.getApiBase()), options);
  }
}