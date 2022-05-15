import config from './../googleMap.js';
import { hasGeolocation } from './../../utils/entries.js';

export default Vue.component('entry-map', {
  props: ['entries',],
  computed: {
    geolocationEntries: function() {
      return this.entries.filter(hasGeolocation);
    },
    markers: function() {
      return this.geolocationEntries.map(e => {
        return {
          lat: e.extra_attributes.location.latitude,
          lng: e.extra_attributes.location.longitude,
        };
      });
    },
  },
  template: `
    <google-map :markers="markers" v-if="geolocationEntries.length"></google-map>
  `
});