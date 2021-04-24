export default Vue.component('activity-tile', {
  props: ['entry'],
  computed: {
    time: function() {
      return new Date(this.entry.date_on_timeline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    text: function() {
      if(this.entry.schema === 'activity.browsing.search') {
        return `Searched for <a href="${this.url}">"${this.entry.title}"</a>`;
      }
      else if(this.entry.schema === 'activity.browsing.watch') {
        return `Watched <a href="${this.url}">"${this.entry.title}"</a>`;
      }
      else {
        return `<a href="${this.url}">${this.entry.title}</a>`;
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
    <div class="activity">
      <i class="icon" :class="iconClass"></i>
      <time>{{ time }}</time>
      <span v-html="text"></span>
      <small v-if="entry.description">{{ entry.description }}</small>
    </div>
  `
});