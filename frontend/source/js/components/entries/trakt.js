import TimelineEntryIcon from './entry-icon.js';

export default Vue.component('watch-entry', {
  props: ['entry'],
  computed: {
    metaText: function() {
      if (this.entry.schema == 'activity.watching.show') {
        return 'Show';
      }
      else if (this.entry.schema == 'activity.watching.movie') {
        return 'Film';
      }
    },
    iconClass: function() {
      if (this.entry.schema == 'activity.watching.movie') {
        return 'fas fa-film';
      }
      else if (this.entry.schema == 'activity.watching.show') {
        return 'fas fa-tv';
      }
    },
    url: function() {
      return this.entry.extra_attributes.url;
    }
  },
  template: `
    <div class="trakt">
      <entry-icon :icon-class="iconClass" :entry="entry"></entry-icon>
      <div class="meta">{{ metaText }}</div>
      <div class="content">
        <a :href="url">"{{ entry.title }}"</a>
        <small v-if="entry.description">{{ entry.description }}</small>
      </div>
    </div>
  `
});