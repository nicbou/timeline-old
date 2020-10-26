export default class {
  static getEntries(date) {
    const requestUrl = new URL('/api/timeline/entries/', `https://${window.location.hostname}`);
    requestUrl.search = new URLSearchParams({
        date_on_timeline__gte: moment(date).startOf('day').toJSON(),
        date_on_timeline__lt: moment(date).startOf('day').add(1, 'day').toJSON(),
    });
    return fetch(requestUrl).then((response) => {
      return response.json();
    });
  }
}