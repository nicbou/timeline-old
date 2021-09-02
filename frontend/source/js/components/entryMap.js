export default Vue.component('entry-map', {
  props: ['entries', 'width', 'height'],
  computed: {
    geolocationEntries: function() {
      return this.entries.filter(e => e.extra_attributes.location && e.extra_attributes.location.latitude && e.extra_attributes.location.longitude);
    },
    mapUrl: function() {
      const imageUrl = new URL("https://maps.googleapis.com/maps/api/staticmap");
      imageUrl.searchParams.append("maptype", "roadmap");
      imageUrl.searchParams.append("scale", 2);
      imageUrl.searchParams.append("size", `${this.width}x${this.height}`);
      imageUrl.searchParams.append("style", "feature:poi|element:labels|visibility:off");
      imageUrl.searchParams.append("key", "AIzaSyBdUNg8QHEUgkxxmT94OIW5t3tCYmHmng4");
      if (this.geolocationEntries.length) {
        const latestEntryLocation = this.geolocationEntries[this.geolocationEntries.length - 1].extra_attributes.location;
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
      <img :src="mapUrl"/>
    </div>
  `
});