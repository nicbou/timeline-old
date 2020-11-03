export default Vue.component('post', {
  props: ['entry'],
  computed: {
    postType: function() {
      return this.entry.schema.split('.')[1];
    },
    userPermalink: function() {
      return `https://twitter.com/${this.entry.extra_attributes.post_user}`;
    },
    tweetPermalink: function() {
      return `${this.userPermalink}/status/${this.entry.extra_attributes.post_id}`;
    },
    richDescription: function() {
      return this.entry.description.replace(/@([\w]{1,15})/ig, '<a target="_blank" href="https://twitter.com/$1">@$1</a>');
    }
  },
  template: `
    <article>
      <header>
        <a :href="userPermalink" class="post-title">@{{ entry.extra_attributes.post_user }}</a>
        <a :href="tweetPermalink" class="post-icon" :class="postType" target="_blank">
          <i class="fab fa-twitter"></i>
        </a>
      </header>
      <main>
        <p v-html="richDescription"></p>
      </main>

    </article>
  `
});