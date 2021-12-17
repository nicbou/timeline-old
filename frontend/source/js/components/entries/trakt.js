export default Vue.component('trakt-tile', {
    props: ['entry'],
    computed: {
      time: function() {
        return new Date(this.entry.date_on_timeline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      },
      text: function() {
        if (this.entry.schema == 'activity.watching.show') {
          var category = 'Show'
        }
        else if (this.entry.schema == 'activity.watching.movie') {
          var category = 'Film'
        }
        let txt = `Watched ${category}: <a href="${this.url}">${this.entry.title}</a>`;
        return txt;
      },
      iconClass: function() {
        if (this.entry.schema == 'activity.watching.movie') {
          return 'fas fa-film';
        }
        else if (this.entry.schema == 'activity.watching.show') {
          return 'fas fa-tv';
        }
        else return
      },
      url: function() {
        const trakt_site = 'https://trakt.tv/'
        if (this.entry.schema == 'activity.watching.movie') {
          const category = 'movies'
          const slug = this.entry.extra_attributes.ids.slug
          return trakt_site + category + '/' + slug
        }
        else if (this.entry.schema == 'activity.watching.show') {
          var category = 'shows'
          const show_slug = this.entry.extra_attributes.show.show_ids.slug
          const season = this.entry.extra_attributes.episode.season
          const episode = this.entry.extra_attributes.episode.number
          return trakt_site + category + '/' + show_slug + '/seasons/' + season + '/episodes/' + episode
        }

      },
    },
    template: `
      <div class="activity compact">
        <i class="icon" :class="iconClass"></i>
        <time>{{ time }}</time>
         <span v-html="text"></span>
      </div>
    `
  });