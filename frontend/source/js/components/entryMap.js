export default Vue.component('entry-map', {
  props: ['entries'],
  computed: {
    geolocationEntries: function() {
      return this.entries.filter(e => e.extra_attributes.location && e.extra_attributes.location.latitude && e.extra_attributes.location.longitude);
    },
    mapUrl: function() {
      const imageUrl = new URL("https://maps.googleapis.com/maps/api/staticmap");
      imageUrl.searchParams.append("maptype", "roadmap");
      imageUrl.searchParams.append("scale", "2");
      imageUrl.searchParams.append("size", "300x200");
      imageUrl.searchParams.append("style", "feature:poi|element:labels|visibility:off");
      imageUrl.searchParams.append("key", "AIzaSyBdUNg8QHEUgkxxmT94OIW5t3tCYmHmng4");
      if (this.geolocationEntries.length) {
        const latestEntryLocation = this.geolocationEntries[0].extra_attributes.location;
        const latestEntryLocationString = `${latestEntryLocation.latitude},${latestEntryLocation.longitude}`;
        imageUrl.searchParams.append("markers", latestEntryLocationString);
        const path = this.geolocationEntries
          .map(e => `${e.extra_attributes.location.latitude},${e.extra_attributes.location.longitude}`)
          .join('|');
        imageUrl.searchParams.append("path", path);
      }
      return imageUrl;
    }
  },
  template: `
    <div class="map" v-if="geolocationEntries.length">
      <img
        loading="lazy"
        :src="mapUrl"
        />
    </div>
  `
});