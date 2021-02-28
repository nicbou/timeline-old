export default Vue.component('browsing-history-tile', {
  props: ['entries'],
  computed: {
    sortedEntries: function() {
      
    },
    activities: function() {
      return this.entries.map(entry => {
        const activity = {};

        activity.time = new Date(entry.date_on_timeline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        activity.title = entry.schema === 'activity.browsing.search' ? `"${entry.title}"` : entry.title;
        activity.description = entry.description;
        activity.url = entry.extra_attributes.url;

        let hostname = null;
        try {
          hostname = (new URL(activity.url)).hostname.replace(/^(www\.)/,"");
        }
        catch {}

        if (hostname && hostname.startsWith('google.')) {
          activity.website = null;
        }
        else if (hostname && hostname.startsWith('youtube.')) {
          activity.website = 'YouTube';
          activity.iconClass = 'fab fa-youtube';
        }
        else {
          activity.website = hostname;
          activity.iconClass = 'fas fa-globe-americas';
        }

        if(entry.schema === 'activity.browsing.search') {
          activity.iconClass = 'fas fa-search';
        }

        return activity;
      }).sort().reverse();
    },
  },
  template: `
    <article class="post tile browsing-history" v-if="entries.length">
      <header>
        <span class="post-icon">
          <i class="fas fa-history"></i>
        </span>
        Browsing history
      </header>
      <main>
        <ul>
          <li v-for="activity in activities">
            <i class="icon" :class="activity.iconClass"></i>
            <time>{{ activity.time }}</time>
            <a :href="activity.url">{{ activity.title }}</a><span v-if="activity.website"> - {{ activity.website }}</span>
            <small v-if="activity.description">{{ activity.description }}</small>
          </li>
        </ul>
      </main>
    </article>
  `
});