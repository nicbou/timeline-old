import ApiService from './api-service.js';

export default class extends ApiService {
  static getEntries(date, filters, accessToken) {
    const requestUrl = new URL('timeline/entries/', this.getApiBase());
    requestUrl.search = new URLSearchParams({
      date_on_timeline__gte: moment(date).startOf('day').toJSON(),
      date_on_timeline__lt: moment(date).startOf('day').add(1, 'day').toJSON(),
      ...filters
    });
    return this.fetchWithToken(requestUrl, {}, accessToken).then((response) => {
      return response.json();
    });
  }

  static saveEntry(entry, accessToken){
    let url = '/api/timeline/entries/';
    let method = 'POST';
    if(entry.id !== null && entry.id !== undefined){
      url += entry.id + '/';
      method = 'PUT';
    }
    const requestUrl = new URL(url, `https://${window.location.hostname}`);
    return this.fetchWithToken(
      requestUrl,
      { 
        method: method,
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify(entry),
      },
      accessToken
    ).then((response) => {
      return response.json();
    });
  }

  static async deleteEntry(entry, accessToken) {
    const entryUrl = new URL(`/api/timeline/entries/${entry.id}/`, `https://${window.location.hostname}/api/`);
    return this.fetchWithToken(entryUrl, { method: 'DELETE' }, accessToken);
  }
}