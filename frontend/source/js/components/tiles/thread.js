export default Vue.component('thread-tile', {
  props: ['thread'],
  computed: {
    iconClass: function() {
      if (this.thread[0].schema.startsWith('message.text.sms')) {
        return 'fas fa-sms';
      }
      return 'fas fa-comments';
    },
  },
  methods: {
    time: function(jsonDate) {
      return moment(jsonDate).format('HH:mm');
    },
    isSender: function(entry) {
      return entry.extra_attributes.sender_id === this.thread[0].extra_attributes.sender_id;
    },
  },
  template: `
    <div class="tile post thread">
      <header>
        <span class="post-icon">
          <i :class="iconClass"></i>
        </span>
        <span class="post-title">
          ...
        </span>
      </header>
      <main>
        <ul>
          <li class="message" v-for="entry in thread" :class="{'left': isSender(entry), 'right': !isSender(entry)}">
            <header>
              <time>{{ time(entry.date_on_timeline) }}</time>
              <span class="name">{{ entry.extra_attributes.sender_name }}</span>
            </header>
            <main>
              {{ entry.description }}
            </main>
          </li>
        </ul>
      </main>
    </div>
  `
});