export default Vue.component('activity-entry', {
  props: ['entry'],
  computed: {
    metaText: function() {
      if(this.entry.schema === 'activity.browsing.search') {
        return 'Google search';
      }
      else if(this.entry.schema === 'activity.browsing.watch') {
        return 'YouTube video';
      }
      else {
        return 'Page view';
      }
    },
    icon: function() {
      return this.entry.schema === 'activity.browsing.search' ? `"${this.entry.title}"` : this.entry.title;
    },
    url: function() {
      return this.entry.extra_attributes.url;
    },
    hostname: function() {
      let hostname = null;
      try {
        hostname = (new URL(this.url)).hostname.replace(/^(www\.)/,"");
      }
      catch {}
      return hostname;
    },
    entryClass: function() {
      if (this.hostname && this.hostname.startsWith('youtube.')) {
        return 'watch youtube';
      }
      else if(this.entry.schema === 'activity.browsing.search') {
        return 'search';
      }
      else {
        return 'browse';
      }

    },
    iconClass: function() {
      if (this.hostname && this.hostname.startsWith('youtube.')) {
        return 'fab fa-youtube';
      }
      else if(this.entry.schema === 'activity.browsing.search') {
        return 'fas fa-search';
      }
      else {
        return 'fas fa-globe-americas';
      }
    },
  },
  template: `
    <div :class="entryClass">
      <i class="icon" :class="iconClass" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">{{ metaText }}</div>
      <div class="content">
        <a :href="url">"{{ entry.title }}"</a>
        <small v-if="entry.description">{{ entry.description }}</small>
      </div>
    </div>
  `
});