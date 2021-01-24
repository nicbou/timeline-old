import EntryMap from './entryMap.js';

export default Vue.component('entry-recap', {
  props: ['entries'],
  computed: {
    geolocationEntries: function() {
      return this.entries.filter(e => e.extra_attributes.location && e.extra_attributes.location.latitude && e.extra_attributes.location.longitude);
    },
    fileEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('file.'));
    },
    photoEntries: function() {
      return this.fileEntries.filter(e => e.schema.startsWith('file.image'));
    },
    videoEntries: function() {
      return this.fileEntries.filter(e => e.schema.startsWith('file.video'));
    },
    hackernewsEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('social.hackernews.'));
    },
    redditEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('social.reddit.'));
    },
    twitterEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('social.twitter.'));
    },
    blogEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('social.blog.'));
    },
  },
  template: `
    <div>
      <ul class="recap">
        <li v-if="photoEntries.length">
          <i class="fas fa-map-marker-alt"></i>
          {{ photoEntries.length }} photos
        </li>
        <li v-if="videoEntries.length">
          <i class="fas fa-map-marker-alt"></i>
          {{ videoEntries.length }} videos
        </li>
        <li v-if="fileEntries.length">
          <i class="fas fa-file"></i>
          {{ fileEntries.length }} files changed
        </li>
        <li v-if="redditEntries.length">
          <i class="fab fa-reddit"></i>
          {{ redditEntries.length }} reddit comments
        </li>
        <li v-if="hackernewsEntries.length">
          <i class="fab fa-y-combinator"></i>
          {{ hackernewsEntries.length }} Hacker News comments
        </li>
        <li v-if="twitterEntries.length">
          <i class="fab fa-twitter"></i>
          {{ twitterEntries.length }} tweets
        </li>
        <li v-if="blogEntries.length">
          <i class="fas fa-rss-square"></i>
          {{ blogEntries.length }} blog posts
        </li>
        <li v-if="geolocationEntries.length">
          <i class="fas fa-map-marker-alt"></i>
          {{ geolocationEntries.length }} location pings
        </li>
      </ul>
      <entry-map :entries="entries" width="300" height="200"></entry-map>
    </div>
  `
});