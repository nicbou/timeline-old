export default Vue.component('text-tile', {
  props: ['entry'],
  computed: {
    fileName: function() {
      const pathParts = this.entry.extra_attributes.path.split('/');
      return pathParts[pathParts.length - 1];
    },
    richDescription: function() {
      if(this.entry.schema === 'social.reddit.post') {
        return `<h3><a href="${this.entry.extra_attributes.post_url}">${this.entry.title}</a></h3>`;
      }
      return this.entry.extra_attributes.post_body_html || this.entry.description
        .replace(/@([\w]{1,50})/ig, '<a target="_blank" href="https://twitter.com/$1">@$1</a>')
        .replace(/\/r\/([\w]{1,20})/ig, '<a target="_blank" href="https://reddit.com/r/$1">@$1</a>')
        .replace(/\/u\/([\w]{1,20})/ig, '<a target="_blank" href="https://reddit.com/user/$1">@$1</a>');
    },
  },
  template: `
    <article class="post text">
      <header @click="$emit('select', entry)">
        <a :href="postPermalink" class="post-icon" target="_blank">
          <i class="fas fa-file-alt"></i>
        </a>
        <span class="post-title">
          {{ fileName }}
        </span>
      </header>
      <main>
        <pre v-html="richDescription"></pre>
      </main>
    </article>
  `
});