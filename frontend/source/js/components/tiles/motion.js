export default Vue.component('motion-tile', {
  props: ['entry'],
  computed: {
    time: function() {
      return new Date(this.entry.date_on_timeline).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    period: function() {
      // Return a text of the time of day
      var hours = new Date(this.entry.date_on_timeline).getHours();
      if (hours < 12) {
        return 'morning';
      }
      else if (hours <= 18) {
        return 'afternoon';
      }
      else if (hours <= 24) {
        return 'evening';
      }
    },
    text: function() {
      var txt = `${this.period} ${this.entry.title}`;
      // Capitalize each word
      txt = txt.toLowerCase()
      .split(' ')
      .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
      .join(' ');
      return txt;
    },
    description: function() {
      return `in ` + this.entry.extra_attributes.duration.toFixed(1) + ` min`;
    },
    iconClass: function() {
      if (this.entry.title == 'walking') {
        return 'fas fa-walking';
      }
      else if (this.entry.title == 'biking') {
        return 'fas fa-biking';
      }
      else if (this.entry.title == 'running') {
        return 'fas fa-running';
      }
      else if (this.entry.title == 'skiing') {
        return 'fas fa-skiing';
      }
      else if (this.entry.title == 'rowing') {
        return 'fas fa-rowing';
      }
      else return 'fas fa heart'
    },
  },
  template: `
    <div class="activity compact">
      <i class="icon" :class="iconClass"></i>
      <time>{{ time }}</time>
      <span v-html="text"></span>
      <small>{{ description }}</small>
    </div>
  `
});